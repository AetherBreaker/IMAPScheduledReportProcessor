if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

import os
import sys
from logging import getLogger
from pathlib import Path
from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# from pydantic.networks import NameEmail

logger = getLogger(__name__)

os.environ.setdefault("PYDANTIC_ERRORS_INCLUDE_URL", "false")


CWD = Path(__file__).parent if getattr(sys, "frozen", False) else Path.cwd()

testing = False


class Settings(BaseSettings):
  model_config = (
    SettingsConfigDict(
      env_file=CWD / "testing.env",
      env_file_encoding="utf-8",
      env_ignore_empty=True,
    )
    if __debug__
    else SettingsConfigDict()
  )
