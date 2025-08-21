from pmsintegration.core.smtp.smtp_config import SmtpRestConnectorConfig


class SmtpRestAPIClient:
    def __init__(self, config: SmtpRestConnectorConfig):
        self._config = config

    @property
    def get_config(self):
        return self._config
