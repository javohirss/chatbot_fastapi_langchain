from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_PORT: str
    DB_NAME: str

    JWT_KEY: str
    JWT_ALGORITHM: str

    OPENAI_API_KEY: str

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()