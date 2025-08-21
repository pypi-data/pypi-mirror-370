class EasyMakerError(Exception):
    """Base class for all errors."""


class EasyMakerAuthError(EasyMakerError):
    pass


class EasyMakerRegionError(EasyMakerError):
    pass


class EasyMakerDockerError(Exception):
    pass
