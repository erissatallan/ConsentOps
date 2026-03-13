"""
Auth0 config should not be scattered.
Connection names matter in this project because the provider boundary is the Auth0 Connection.
We are setting up for real env-driven deployment early.
"""


from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    auth0_domain: str = Field(default="example.us.auth0.com", alias="AUTH0_DOMAIN")
    auth0_client_id: str = Field(default="placeholder-client-id", alias="AUTH0_CLIENT_ID")
    auth0_client_secret: str = Field(default="placeholder-client-secret", alias="AUTH0_CLIENT_SECRET")
    auth0_audience: str = Field(default="https://api.consentops.local", alias="AUTH0_AUDIENCE")

    # We will likely store connection names explicitly because Auth0 Token Vault
    # uses connections as the provider boundary.
    auth0_google_connection: str = Field(default="google-oauth2", alias="AUTH0_GOOGLE_CONNECTION")
    auth0_slack_connection: str = Field(default="slack", alias="AUTH0_SLACK_CONNECTION")


settings = Settings()
