import atexit
import threading
import time

import easymaker
from easymaker.common import constants, exceptions


class Logger:
    def __init__(self, logncrash_appkey=None):
        """
        Args:
            logncrash_appkey (str): NHN Cloud Log&Crash app_key
        """
        self.easymaker_api_sender = easymaker.easymaker_config.api_sender
        self.logncrash_appkey = logncrash_appkey
        self.buffer = []
        atexit.register(self._flush_message)  # python 종료시 flush 호출
        threading.Timer(1, self._flush_message).start()  # 1초마다 flush

    def send(self, log_message, log_level="INFO", project_version="1.0.0", parameters=None):
        """
        Args:
            log_message (str): size limit 8000000
        """
        if parameters is None:
            parameters = {}
        try:
            logncrash_body = {"category": "easymaker.sdk", "logType": "NHN Cloud - AI EasyMaker", "projectName": self.logncrash_appkey, "body": log_message, "logLevel": log_level, "projectVersion": project_version, "sendTime": time.time(), "host": "easymaker"}
            logncrash_body.update(parameters)
            logncrash_body.update(
                {
                    "logVersion": "v2",
                }
            )

            if len(str(logncrash_body)) > constants.LOGNCRASH_MAX_MESSAGE_SIZE:
                self._flush_message()
                raise exceptions.EasyMakerError("Log message size more than limit size")

            if self.logncrash_appkey:
                self.buffer.append(logncrash_body)
                if len(str(self.buffer)) > constants.LOGNCRASH_MAX_BUFFER_SIZE:
                    self._flush_message()

        except Exception as e:
            print(f"{e}")

    def _flush_message(self):
        if len(self.buffer) == 0:
            return
        self.easymaker_api_sender.send_logncrash(logncrash_body=self.buffer)
        self.buffer = []
