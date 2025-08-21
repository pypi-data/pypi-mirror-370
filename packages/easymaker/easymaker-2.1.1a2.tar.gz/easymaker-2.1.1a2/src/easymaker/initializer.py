
import logging
import os

from easymaker.api.api_sender import ApiSender
from easymaker.common import constants

_LOGGER = logging.getLogger(__name__)


class _Config:
    """Stores common parameters and options for API calls."""

    def __init__(self):
        self._appkey = os.environ.get("EM_APPKEY")
        self._region = os.environ.get("EM_REGION")
        self._user_id = None
        self._access_token = None
        self.api_sender = None
        if os.environ.get("EM_APPKEY") and os.environ.get("EM_REGION"):
            self.api_sender = ApiSender(self._region, self._appkey)

    def init(
        self,
        *,
        appkey: str | None = None,
        region: str | None = None,
        access_token: str | None = None,
        profile: str | None = None,
        experiment_id: str | None = None,
    ):
        """
        Args:
            appkey (str): easymaker appkey
            region (str): region (kr1, ..)
            access_token (str): easymaker access token
            profile (str): easymaker profile (alpha, beta)
        """
        _LOGGER.debug("EasyMaker Config init")
        if appkey:
            self._appkey = appkey
            os.environ["EM_APPKEY"] = appkey
        if region:
            self._region = region
            os.environ["EM_REGION"] = region
        if access_token:
            self._access_token = access_token
            os.environ["EM_ACCESS_TOKEN"] = access_token
        if profile:
            os.environ["EM_PROFILE"] = profile
        if experiment_id:
            os.environ["EM_EXPERIMENT_ID"] = experiment_id

        self.api_sender = ApiSender(region, appkey, access_token)

    @property
    def appkey(self) -> str:
        return self._appkey

    @property
    def region(self) -> str:
        return self._region or constants.DEFAULT_REGION

    @property
    def access_token(self) -> str:
        return self._access_token


# global config to store init parameters: easymaker.init(appkey=..., region=...)
global_config = _Config()
