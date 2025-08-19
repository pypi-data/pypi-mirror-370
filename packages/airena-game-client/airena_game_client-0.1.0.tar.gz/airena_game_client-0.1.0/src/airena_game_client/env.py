from uuid import UUID

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AirenaClientSettings(BaseSettings):
    """
    Settings for configuring the Airena game client.

    Values are set by environment variables when run in Airena.

    Attributes:
        model_config (SettingsConfigDict): Configuration for environment variable prefix.
        cgi_url (str): URL for the CGI server. Defaults to "https://cgi.airena.dev".
        game_id (UUID): Unique identifier for the game.
        game_secret (UUID): Secret key for the game.
        player_count (int): Number of players in the game.
    """

    model_config = SettingsConfigDict(env_prefix="AIRENA_")
    cgi_url: str = Field(default="https://cgi.airena.dev")
    game_id: UUID = Field(default=...)
    game_secret: UUID = Field(default=...)
    player_count: int = Field(default=...)
