import hashlib
import multiprocessing
import os.path
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

from requests.adapters import HTTPAdapter, Retry
from requests.sessions import Session
from tqdm import tqdm

from easymaker.api.api_sender import ApiSender
from easymaker.common import constants, exceptions


class ObjectStorage:
    DUPLICATE_CHECK_FILE_SIZE = 100 * 1024 * 1024  # 100MB 이상이면 기존에 업로드 된 동일한 파일이 있는지 확인
    MULTIPART_UPLOAD_FILE_SIZE_THRESHOLD = 2 * 1024 * 1024 * 1024  # 2GB 이상이면 분할 업로드 (2,147,483,647bytes 이상에서 OverflowError 발생해서 5G->2G로 변경)
    MULTIPART_UPLOAD_CHUNK_SIZE = 500 * 1024 * 1024  # 500MB 분할 업로드 파일당 크기
    MAX_OBJECT_LIST_COUNT = 1000

    def __init__(self, easymaker_region=None, username=None, password=None):
        self.token_expires = None
        self.api_sender = None

        if easymaker_region:
            self.region = easymaker_region.lower()
        else:
            self.region = os.environ.get("EM_REGION", constants.DEFAULT_REGION).lower()
        self.username = username
        self.password = password

        self.session = Session()
        self.session.mount("https://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1)))

    def _get_default_workers(self):
        """CPU 수에 따라 기본 워커 수를 반환"""
        cpu_count = multiprocessing.cpu_count()
        # 최대 8개 워커 제한 (네트워크 I/O 병목 고려)
        return min(cpu_count, 8)

    def _get_token(self, tenant_id=None):
        if tenant_id:
            self.tenant_id = tenant_id

        if self.token_expires is not None:
            if os.environ.get("EM_TOKEN"):
                self.now = datetime.now(timezone(timedelta(hours=9)))
            else:
                self.now = datetime.now(timezone.utc)
            time_diff = self.token_expires - self.now
            if time_diff.total_seconds() > 600:
                return

        self.api_sender = ApiSender(self.region, os.environ.get("EM_APPKEY"), os.environ.get("EM_ACCESS_TOKEN"))
        response = self.api_sender.get_objectstorage_token(tenant_id=self.tenant_id, username=self.username, password=self.password)
        try:
            self.token = response["access"]["token"]
        except KeyError:
            print(response)

        self.token_id = self.token["id"]

        if os.environ.get("EM_TOKEN"):
            self.token_expires = datetime.strptime(self.token["expires"], "%Y-%m-%dT%H:%M:%S.%f%z")
        else:
            utc_time = datetime.strptime(self.token["expires"], "%Y-%m-%dT%H:%M:%SZ")
            self.token_expires = utc_time.replace(tzinfo=timezone.utc)

    def _get_request_header(self):
        self._get_token(self.tenant_id)
        return {"X-Auth-Token": self.token_id}

    def _get_object_list_generator(self, container_url, req_header, object_path, file_extensions=None):
        """Generator로 파일 목록을 순차적으로 반환"""
        marker = None
        while True:
            response = self.session.get(container_url, headers=req_header, params={"prefix": object_path, "marker": marker, "limit": self.MAX_OBJECT_LIST_COUNT})

            if response.status_code != 200 and response.status_code != 204:
                raise exceptions.EasyMakerError(response)

            object_list = response.text.split("\n")[:-1]

            if not object_list:  # 더 이상 파일이 없음
                break

            path = str(object_path)

            # 확장자 필터 준비
            def matches_extension(obj_name):
                if file_extensions is None:
                    return True

                obj_name_lower = obj_name.lower()
                return any(obj_name_lower.endswith(ext.lower()) for ext in file_extensions)

            # 파일만 필터링
            for obj in object_list:
                # 오브젝트가 파일인 경우, object_path를 파일 경로로 입력함
                if (path.endswith("/") is False) and (obj == path):
                    if matches_extension(obj):
                        yield obj

                if path.endswith("/") is False:
                    path = "".join([path, "/"])

                # 오브젝트가 루트 디렉토리의 파일인 경우 또는 디렉토리의 파일인 경우
                if (obj.startswith(path) or path == "/") and not obj.endswith("/"):
                    if matches_extension(obj):
                        yield obj

            # 다음 페이지가 있는지 확인
            if len(object_list) < self.MAX_OBJECT_LIST_COUNT:
                break

            marker = object_list[-1]  # 마지막 파일을 다음 marker로 사용

    def _get_object_list(self, container_url, req_header, object_path):
        """기존 호환성을 위한 메서드 - generator를 사용하여 모든 객체를 반환"""
        return list(self._get_object_list_generator(container_url, req_header, object_path))

    def _get_object_file_size(self, container_url, req_header, object_path):
        response = self.session.head(f"{container_url}/{object_path}", headers=req_header)

        if response.status_code != 200 and response.status_code != 204:
            raise exceptions.EasyMakerError(response)

        return response.headers["content-length"]

    def _get_object_metadata(self, container_url, req_header, object_path):
        """
        Get file metadata from HEAD request
        Args:
            container_url : obs container url
            req_header : request header with auth token
            object_path : object path
        Returns:
            dict : metadata including content-length, content-type, last-modified, etag
        """
        response = self.session.head(f"{container_url}/{object_path}", headers=req_header)

        if response.status_code != 200 and response.status_code != 204:
            raise exceptions.EasyMakerError(response)

        metadata = {
            "content_length": int(response.headers.get("content-length", 0)),
            "content_type": response.headers.get("content-type", ""),
            "last_modified": response.headers.get("last-modified", ""),
            "etag": response.headers.get("etag", ""),
            "object_path": object_path,
        }
        return metadata

    def _get_object_file_count(self, container_url, req_header, object_path, file_extensions=None, filter_func=None):
        """OBS 컨테이너의 파일 수를 계산"""
        count = 0
        for obj in self._get_object_list_generator(container_url, req_header, object_path, file_extensions):
            if filter_func:
                try:
                    metadata = self._get_object_metadata(container_url, req_header, obj)
                    if not filter_func(metadata):
                        continue
                except Exception:
                    continue
            count += 1
        return count

    def get_object_size(self, easymaker_obs_uri):
        """
        Args:
            easymaker_obs_uri : easymaker obs uri (obs://{object_storage_endpoint}/{container_name}/{path})
        """
        _, _, container_url, tenant_id, _, object_prefix = parse_obs_uri(easymaker_obs_uri)
        self._get_token(tenant_id)

        object_size_total = 0

        # Generator를 사용하여 모든 객체를 순회
        for obj in self._get_object_list_generator(container_url, self._get_request_header(), object_prefix):
            object_size_total += int(self._get_object_file_size(container_url, self._get_request_header(), obj))

        return object_size_total

    def upload(self, easymaker_obs_uri, local_path):
        """
        Args:
            easymaker_obs_uri : easymaker obs directory uri (obs://{object_storage_endpoint}/{container_name}/{path})
            local_path : upload local path (file or directory)
        """
        obs_full_url, _, _, tenant_id, _, _ = parse_obs_uri(easymaker_obs_uri)
        self._get_token(tenant_id)

        if os.path.isfile(local_path):
            upload_url = os.path.join(obs_full_url, os.path.basename(local_path))
            try:
                self._upload_file(upload_url, local_path)
            except FileNotFoundError as e:
                print(f"File not found: {e}")
                return
            except Exception as e:
                print(f"Error uploading file: {e}")
                return
        elif os.path.isdir(local_path):
            file_path_list = []
            for root, _dirs, files in os.walk(local_path):
                for file in files:
                    file_path_list.append(os.path.join(root, file))

            for upload_file_path in file_path_list:
                upload_url = os.path.join(obs_full_url, os.path.relpath(upload_file_path, os.path.abspath(local_path)))
                try:
                    self._upload_file(upload_url, upload_file_path)
                except FileNotFoundError as e:
                    print(f"File not found: {e}")
                    continue
                except Exception as e:
                    print(f"Error uploading file: {e}")
                    continue
        else:
            print(f"Path not found: {local_path}")

    def _calc_file_md5_hash(self, file_path):
        f = open(file_path, "rb")
        data = f.read()
        hash = hashlib.md5(data).hexdigest()
        return hash

    def _is_duplicate_file(self, request_url, local_file_path):
        file_size = os.path.getsize(local_file_path)

        if file_size < self.DUPLICATE_CHECK_FILE_SIZE:  # 크기 큰 파일만 동일 파일 존재 여부 확인
            return False

        self._get_token(self.tenant_id)
        req_header = self._get_request_header()

        response = self.session.head(request_url, headers=req_header)
        if response.status_code != 200:
            return False

        if response.headers["content-length"] == str(file_size):
            # 멀티파트 오브젝트의 ETag는 각 파트 오브젝트의 ETag 값을 이진 데이터로 변환하고 순서대로 연결해(concatenate) MD5 해시한 값이라 분할 업로드한 대용량 파일에서는 비교 불가
            if response.headers["etag"] == self._calc_file_md5_hash(local_file_path):
                return True

        return False

    def _upload_file(self, upload_url, upload_file_path):
        """
        Upload files under 5G
        Args:
            easymaker_obs_uri : obs object path (file)
            upload_file_path : upload local path (file)
        """
        if self._is_duplicate_file(upload_url, upload_file_path):
            return

        if os.path.getsize(upload_file_path) >= self.MULTIPART_UPLOAD_FILE_SIZE_THRESHOLD:
            return self._upload_large_file(upload_url, upload_file_path)

        req_header = self._get_request_header()
        with open(upload_file_path, "rb") as f:
            return self.session.put(upload_url, headers=req_header, data=f.read())

    def _upload_large_file(self, upload_url, upload_file_path):
        """
        Objects with a capacity exceeding 2 GB are uploaded in segments of 2 GB or less.
        """
        req_header = self._get_request_header()

        with open(upload_file_path, "rb") as f:
            chunk_index = 1
            chunk_size = self.MULTIPART_UPLOAD_CHUNK_SIZE
            total_bytes_read = 0
            obj_size = os.path.getsize(upload_file_path)

            while total_bytes_read < obj_size:
                remained_bytes = obj_size - total_bytes_read
                if remained_bytes < chunk_size:
                    chunk_size = remained_bytes

                request_url = f"{upload_url}/{chunk_index:03d}"
                self.session.put(request_url, headers=req_header, data=f.read(chunk_size))
                total_bytes_read += chunk_size
                f.seek(total_bytes_read)
                chunk_index += 1

        # create manifest
        req_header = self._get_request_header()
        # X-Object-Manifest : AUTH_*****/ 뒷부분 경로
        uri_element_list = upload_url.split("/")
        for idx, val in enumerate(uri_element_list):
            if val.startswith("AUTH_"):
                object_manifest = "/".join(uri_element_list[idx + 1 :])
        req_header["X-Object-Manifest"] = object_manifest
        return self.session.put(upload_url, headers=req_header)

    def download(self, easymaker_obs_uri, download_dir_path, max_workers=None, file_extensions=None, filter_func=None, show_progress=True):
        """
        Args:
            easymaker_obs_uri : easymaker obs uri (obs://{object_storage_endpoint}/{container_name}/{path})
            download_dir_path : download local path (directory)
            max_workers : Parallel download max thread count (default: CPU 코어 수에 따라 자동 조정)
            file_extensions : Target file extension filter (list of str, e.g., ['.txt', '.jpg'])
            filter_func : Callable that receives file metadata dict and returns True/False for download decision
            show_progress : Show progress bar (default: True)
        """
        if max_workers is None:
            max_workers = self._get_default_workers()
        obs_full_url, _, container_url, tenant_id, _, object_prefix = parse_obs_uri(easymaker_obs_uri)
        self._get_token(tenant_id)

        # 파일 수 계산
        print("Counting files...")
        file_count = self._get_object_file_count(container_url, self._get_request_header(), object_prefix, file_extensions, filter_func)

        if file_count == 0:
            print("No files found to download")
            return

        print(f"Found {file_count} files to download")

        # 실제 다운로드 (진행률 표시)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {}

            for obj in self._get_object_list_generator(container_url, self._get_request_header(), object_prefix, file_extensions):
                # filter_func가 있는 경우 메타데이터 확인
                if filter_func:
                    try:
                        metadata = self._get_object_metadata(container_url, self._get_request_header(), obj)
                        if not filter_func(metadata):
                            continue
                    except Exception:
                        print(f"File metadata get failed {obj}. Skip download.")
                        continue

                # 다운로드 경로 설정
                if object_prefix == "/":
                    download_file_path = os.path.join(download_dir_path, obj)
                else:
                    download_file_path = os.path.join(download_dir_path, os.path.relpath(obj, object_prefix))

                # 다운로드를 별도 스레드로 처리
                future = executor.submit(self._download_file, container_url, obj, download_file_path)
                future_to_file[future] = obj

            if show_progress:
                completed_count = 0
                with tqdm(total=file_count, desc="Downloading files", unit="file", position=0, ncols=100) as pbar:
                    for future in as_completed(future_to_file):
                        file_object = future_to_file[future]
                        try:
                            future.result()
                            completed_count += 1
                            pbar.set_postfix_str(f"{completed_count}/{file_count}")
                        except Exception as exc:
                            print(f"File download failed {file_object}: {exc}")
                        finally:
                            pbar.update(1)
            else:
                for future in as_completed(future_to_file):
                    file_object = future_to_file[future]
                    try:
                        future.result()
                    except Exception as exc:
                        print(f"File download failed {file_object}: {exc}")

    def _download_file(self, container_url, file_object, download_file_path):
        """
        Args:
            container_url : obs container url (https://{object_storage_endpoint}/{container_name})
            file_object : obs object path (file)
            download_file_path : download local path (file)
        """
        request_url = os.path.join(container_url, file_object)
        req_header = self._get_request_header()
        response = self.session.get(request_url, headers=req_header)

        if response.status_code != 200:
            raise exceptions.EasyMakerError(f"Object storage download fail {response.json()}")
        download_file_dir = os.path.dirname(download_file_path)
        if os.path.isfile(download_file_dir):
            raise exceptions.EasyMakerError(f"{download_file_dir} already exists as file. Please check if there is a file and a folder with the same names in object storage.")

        os.makedirs(os.path.dirname(download_file_path), exist_ok=True)
        with open(download_file_path, "wb") as f:
            f.write(response.content)

    def find_object_list(self, easymaker_obs_uri, file_extensions=None):
        _, _, container_url, tenant_id, _, object_prefix = parse_obs_uri(easymaker_obs_uri)
        self._get_token(tenant_id)

        return list(self._get_object_list_generator(container_url, self._get_request_header(), object_prefix, file_extensions))

    def delete(self, easymaker_obs_uri, file_extensions=None, max_workers=None):
        """
        Args:
            easymaker_obs_uri : easymaker obs uri (obs://{object_storage_endpoint}/{container_name}/{path})
            file_extensions : Target file extension filter (list of str)
            max_workers : Parallel delete max thread count (default: CPU 코어 수에 따라 자동 조정)
        """
        if max_workers is None:
            max_workers = self._get_default_workers()
        _, _, container_url, tenant_id, _, object_prefix = parse_obs_uri(easymaker_obs_uri)
        self._get_token(tenant_id)

        # 파일 수 계산
        print("Counting files...")
        file_count = 0
        for obj in self._get_object_list_generator(container_url, self._get_request_header(), object_prefix, file_extensions):
            file_count += 1

        if file_count == 0:
            print("No files found to delete")
            return

        print(f"Found {file_count} files to delete")

        # 실제 삭제 (진행률 표시)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            with tqdm(total=file_count, desc="Deleting files", unit="file", position=0, ncols=100, lock_args=(False,)) as pbar:
                future_to_file = {}

                for obj in self._get_object_list_generator(container_url, self._get_request_header(), object_prefix, file_extensions):
                    # 즉시 삭제 작업 제출
                    future = executor.submit(self._delete_file, os.path.join(container_url, obj))
                    future_to_file[future] = obj

                # 완료된 작업들을 처리
                completed_count = 0
                for future in as_completed(future_to_file):
                    file_object = future_to_file[future]
                    try:
                        future.result()
                        completed_count += 1
                        pbar.set_postfix_str(f"{completed_count}/{file_count}")
                    except Exception as exc:
                        print(f"File delete failed {file_object}: {exc}")
                    finally:
                        pbar.update(1)

    def _delete_file(self, request_url):
        response = self.session.delete(request_url, headers=self._get_request_header())
        if response.status_code != 200 and response.status_code != 204 and response.status_code != 404:
            raise exceptions.EasyMakerError(response)

        return response


def parse_obs_uri(easymaker_obs_uri):
    obs_full_url, number_of_subs_made = re.subn("^(obs)://(.+)$", r"https://\2", easymaker_obs_uri)
    obs_uri_pattern = re.compile("^(?P<container_url>https://(?P<obs_host>[^/]+)/(?P<version>[^/]+)/AUTH_(?P<tenant_id>[^/]+)/(?P<container_name>[^/]+))/?(?P<object_prefix>.*)$")
    match = obs_uri_pattern.match(obs_full_url)

    if number_of_subs_made != 1 or match is None:
        raise exceptions.EasyMakerError(f"Object storage uri parse fail. Invalid uri {easymaker_obs_uri}")

    return obs_full_url, match.group("obs_host"), match.group("container_url"), match.group("tenant_id"), match.group("container_name"), match.group("object_prefix")


def download(easymaker_obs_uri, download_dir_path, easymaker_region=None, username=None, password=None, max_workers=None, file_extensions=None, filter_func=None, show_progress=True):
    """
    Args:
        easymaker_obs_uri (str): easymaker obs uri (obs://{object_storage_endpoint}/{container_name}/{path})
        download_dir_path (str): download local path (directory)
        easymaker_region (str): NHN Cloud object storage Region
        username (str): NHN Cloud object storage username
        password (str): NHN Cloud object storage password
        max_workers (int): Parallel download max thread count (default: CPU 코어 수에 따라 자동 조정)
        file_extensions (list): Target file extension filter (e.g., ['.txt', '.jpg'])
        filter_func (callable): Callable that receives file metadata dict and returns True/False for download decision
        show_progress (bool): Show progress bar (default: True)
    """
    object_storage = ObjectStorage(easymaker_region=easymaker_region, username=username, password=password)
    object_storage.download(easymaker_obs_uri, download_dir_path, max_workers, file_extensions, filter_func, show_progress)


def upload(easymaker_obs_uri, local_path, easymaker_region=None, username=None, password=None):
    """
    Args:
        easymaker_obs_uri (str): easymaker obs directory uri (obs://{object_storage_endpoint}/{container_name}/{path})
        local_path (str): upload local path (file or directory)
        easymaker_region (str): NHN Cloud object storage Region
        username (str): NHN Cloud object storage username
        password (str): NHN Cloud object storage password
    """
    object_storage = ObjectStorage(easymaker_region=easymaker_region, username=username, password=password)
    object_storage.upload(easymaker_obs_uri, local_path)


def delete(easymaker_obs_uri, file_extensions=None, easymaker_region=None, username=None, password=None, max_workers=None):
    """
    Args:
        easymaker_obs_uri (str): easymaker obs directory uri (obs://{object_storage_endpoint}/{container_name}/{path})
        file_extensions (list): Target file extension filter (list of str)
        easymaker_region (str): NHN Cloud object storage Region
        username (str): NHN Cloud object storage username
        password (str): NHN Cloud object storage password
        max_workers (int): Parallel delete max thread count (default: CPU 코어 수에 따라 자동 조정)
    """
    object_storage = ObjectStorage(easymaker_region=easymaker_region, username=username, password=password)
    object_storage.delete(easymaker_obs_uri, file_extensions, max_workers)


def find_object_list(easymaker_obs_uri, file_extensions=None, easymaker_region=None, username=None, password=None):
    """
    Args:
        easymaker_obs_uri (str): easymaker obs directory uri (obs://{object_storage_endpoint}/{container_name}/{path})
        file_extensions (list): Target file extension filter (list of str)
        easymaker_region (str): NHN Cloud object storage Region
        username (str): NHN Cloud object storage username
        password (str): NHN Cloud object storage password
    """
    object_storage = ObjectStorage(easymaker_region=easymaker_region, username=username, password=password)
    return object_storage.find_object_list(easymaker_obs_uri, file_extensions)


def get_object_size(easymaker_obs_uri, easymaker_region=None, username=None, password=None):
    """
    Args:
        easymaker_obs_uri (str): easymaker obs directory uri (obs://{object_storage_endpoint}/{container_name}/{path})
        easymaker_region (str): NHN Cloud object storage Region
        username (str): NHN Cloud object storage username
        password (str): NHN Cloud object storage password
    """
    object_storage = ObjectStorage(easymaker_region=easymaker_region, username=username, password=password)
    return object_storage.get_object_size(easymaker_obs_uri)
