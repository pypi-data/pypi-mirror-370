from enum import Enum


class Environment(Enum):
    DEV   = ("dev", "https://simplex-gateway-dev.private.strusoft.com/")
    TEST  = ("test", "https://simplex-gateway-test.private.strusoft.com/")
    STAGE = ("stage", "https://simplex-gateway-stage.onstrusoft.com/")
    PROD  = ("prod", "https://simplex-gateway.onstrusoft.com/")

    def __init__(self, label: str, base_url: str):
        self._label = label
        self._base_url = base_url

    @property
    def base_url(self) -> str:
        return self._base_url

    def __str__(self):
        return self._label


# Default environment setting - can be modified to change the active environment
ENVIRONMENT = Environment.PROD