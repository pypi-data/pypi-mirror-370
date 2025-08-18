from pydantic import Field
from pydantic_settings import BaseSettings


class S3Settings(BaseSettings):
    HOST: str = Field(default="localhost", description="S3 host")
    PORT: int = Field(default=9000, description="S3 port")
    ACCESS_KEY: str | None = Field(default=None, description="S3 access key")
    SECRET_KEY: str | None = Field(default=None, description="S3 secret key")
    BUCKET_NAME: str = Field(default="my-bucket", description="S3 bucket name")
    SECURE: bool = Field(default=False, description="S3 secure")

    @property
    def ENDPOINT_URL(self) -> str:  # noqa: N802
        return f"{self.HOST}:{self.PORT}"
