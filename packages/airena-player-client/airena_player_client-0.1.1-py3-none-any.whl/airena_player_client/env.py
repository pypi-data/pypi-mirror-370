from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AirenaClientSettings(BaseSettings):
    """
    AirenaClientSettings defines configuration settings for the Airena Python player client.

    Attributes:
        ugi_url (str): The URL for the UGI (User Gateway Interface) service. Defaults to "https://ugi.airena.dev".
            Can be set via the environment variable 'AIRENA_UGI_URL'.
        api_key (str): The API key used for authenticating requests to Airena services.
            Can be set via the environment variable 'AIRENA_API_KEY'.
    """

    model_config = SettingsConfigDict(env_prefix="AIRENA_")
    ugi_url: str = Field(default="https://ugi.airena.dev")
    api_key: str = Field(default=...)
