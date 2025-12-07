from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi.security import OAuth2PasswordBearer
import redis.asyncio as redis
from passlib.context import CryptContext


class Settings(BaseSettings):
    DB_HOST: str
    DB_NAME: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    TEST_DB_NAME: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASS: str
    NUM_OF_LAST_FIELDS: int = 5
    SECRET_KEY: str
    ALGORITHM: str
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    ACCESS_TOKEN_EXPIRE_HOURS = 12

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def get_db_url(self, type_of_db):
        if type_of_db == "async":
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def get_test_db(self, type_of_db):
        if type_of_db == "async":
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def get_redis_client(self):
        return redis.StrictRedis(
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            password=self.REDIS_PASS,
            db=1,
            decode_responses=True,
        )

    def get_pwd(self):
        return CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_oauth2_scheme(self):
        return OAuth2PasswordBearer(tokenUrl="token")


settings = Settings()
