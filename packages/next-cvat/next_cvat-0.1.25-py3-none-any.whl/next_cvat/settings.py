from __future__ import annotations

from pydantic_settings import BaseSettings


def settings(env_file: str | None = ".env.cvat.secrets", env_prefix: str | None = None):
    if env_prefix is None:
        env_prefix = "CVAT_"
    else:
        env_prefix = f"{env_prefix}_CVAT_"

    class Settings(
        BaseSettings, extra="ignore", env_file=env_file, env_prefix=env_prefix
    ):
        username: str | None = None
        password: str | None = None
        token: str | None = None

    return Settings()
