# EasyMaker.SDK

* AI EasyMaker 서비스의 Python SDK를 위한 저장소이다.
* 학습, 모델 등의 리소스를 생성하고 관리할 수 있는 기능을 제공한다.
* [SDK 사용 가이드 - NHN Cloud 사용자 가이드](https://docs.nhncloud.com/ko/Machine%20Learning/AI%20EasyMaker/ko/sdk-guide/)
* SDK를 사용하여 AI EasyMaker를 사용하는 예제는 docs 디렉터리 하위에 Juptyer Notebook으로 제공한다.

## 프로젝트 구조

```sh
.
├── src/easymaker # 소스 코드
│   ├── api # AI EasyMaker API를 호출하기 위한 클라이언트 코드
│   ├── cli # Instance, Image 정보 조회 등을 위한 CLI 명령 지원
│   ├── log # Log & Crash Search 서비스의 로그 수집 기능 지원
│   ├── storage # Object Storage 서비스의 오브젝트 업로드 및 다운로드 기능 지원
│   ├── ... # 그 외 도메인(학습, 모델, 엔드포인트 등)별 디렉터리
│   └── initializer.py # 기본 정보 셋팅 (앱키, 리전 등)
├── tests # 테스트 코드
├── docs # 사용 참고 코드
├── pyproject.toml # 프로젝트 설정 파일
├── docs/README.md # PyPI에 올라갈 README 파일
└── README.md # 내부 README 파일
```

## UV 사용법

> `uv sync`로 설치되는 의존성에는 개발 환경에 필요한 패키지도 포함된다.
> 명령어의 자세한 설명이나 다른 명령어를 확인하려면 `uv {명령어}` 또는 `uv --help`를 입력한다.

### 파이썬 설치

```sh
uv python install 3.10
```

### 파이썬 의존성 패키지 설치

```sh
uv sync
```

### PyPI에 등록된 패키지 설치

```sh
uv sync --no-install-project
uv pip install easymaker=={버전}
```

### python 실행

```sh
uv run python
```

### `pytest` 실행

```sh
uv run pytest -s -v
```

### `ruff` 포맷터 실행

```sh
uv run ruff check
uv run ruff check --fix
uv run ruff check --fix --unsafe-fixes
```

### `uv.lock` 충돌 해결 방법

* 베이스 브랜치를 현재 브랜치에 머지
* 충돌이 발생하는 상황에서 아래의 명령어 수행 후 `uv.lock` 변경 커밋 추가

```sh
git checkout {베이스 브랜치} -- uv.lock
uv lock
```

## CLI 실행

```sh
easymaker [options]
```

위와 같이 실행시 cli.py가 실행됨, 여기에 CLI 호출 코드 추가

## 개발 환경 세팅

* 코드 포맷터
    * Python 포맷터는 ruff를 사용한다.
    * line-length를 320으로 설정한다.
    * 그 외 lint 설정은 pyproject.toml에 정의된 설정을 따른다.
* 기본 설정
    * 패키지 관리는 uv를 사용한다.
        * <https://docs.astral.sh/uv/getting-started/installation/>
        * `uv sync`로 의존성을 설치한다.
    * Python 관리는 uv의 기능 사용을 권장한다.
        * <https://docs.astral.sh/uv/guides/install-python/>
* IntelliJ, PyCharm # TODO: Intellij, PyCharm 설정 수정
    * 코드 포맷은 Actions on Save를 사용한다.
    * Ruff 설정 방법
        * Settings > Plugins: File Watchers 플러그인을 설치한다. (Intellij인 경우)
        * 아래의 설정 중 $가 들어간 변수들은 Intellij나 Pycharm에서 설정된 변수로 인터프리터 경로나 다른 경로를 바꾸는게 아니라면 그대로 사용
        * Settings > Tools > File Watchers > [+] 클릭하여 `<custom>` 추가
            * Ruff lint 추가
                * Name : ruff lint
                * File type: Python
                * Scope: Project Files
                * Program: uv
                * Arguments: run ruff check --fix-only --silent $FilePath$
                * Output paths to refresh: $FilePath$
                * Working directory: $ProjectFileDir$
                * Advanced Options: 1번 항목 체크
            * Ruff Format 추가
                * Name : ruff format
                * File type: Python
                * Scope: Project Files
                * Program: uv
                * Arguments: run ruff format $FilePath$
                * Output paths to refresh: $FilePath$
                * Working directory: $ProjectFileDir$
                * Advanced Options: 1번 항목 체크
            * File Watcher: ruff lint와 ruff format을 체크한다.
* VSCode
    * 프로젝트 단위 설정이 .vscode에 저장되어 있다.
    * 포맷터 적용을 위해 vscode의 확장 프로그램 탭에서 추천 확장 프로그램을 설치한다.
        * 추천 확장 프로그램은 .vscode/extensions.json에 정의되어 있다.
    * 파이썬 환경을 구성은 **기본 설정**을 따른다.
