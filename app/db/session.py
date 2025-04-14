from pydantic_settings import BaseSettings
from app.config import DB_URL, DB_ECHO, API_V1_PREFIX


class Setting(BaseSettings):
    # API prefix for versioning the API
    api_prefix: str = API_V1_PREFIX
    # Database URL and echo flag loaded from environment variables
    db_url: str = DB_URL
    db_echo: bool = DB_ECHO


# Create an instance of the settings using pydantic's BaseSettings,
# which automatically reads environment variables.
settings = Setting()
