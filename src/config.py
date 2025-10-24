from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    LOG_LEVEL: str = "DEBUG"

    ROOT_PATH: str = "/api/v1"

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int = 0

    TASK_TIME_LIMIT: int = 600
    TASK_RESULT_EXPIRES: int = 3600

    DEVICE: str = "cpu"
    COMPUTE_TYPE: str = "float16"
    DOWNLOAD_ROOT: str = "models"
    BATCH_SIZE: int = 4
    CHUNK_SIZE: int = 10

    HF_TOKEN: str | None = None  # Hugging Face token for diarization models

    @property
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DB_URL_SYNC(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


settings = Settings()
