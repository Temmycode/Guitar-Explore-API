from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_name: str
    database_username: str
    database_port: str
    database_hostname: str
    database_password: str

    class Config:
        env_file = ".env"


settings = Settings()
