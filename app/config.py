from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_name: str
    database_username: str
    database_port: str
    database_hostname: str
    database_password: str
    secret_key: str
    algorithm: str
    access_token_expiration_minutes: int
    google_client_id: str
    google_client_secret: str
    ios_client_id: str

    class Config:
        env_file = ".env"


settings = Settings()
