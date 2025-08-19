from dotenv import load_dotenv

load_dotenv(".env")

from .config import MinioConfig, TaskConfig, FfcsConfig

__all__ = ["TaskConfig", "MinioConfig", "FfcsConfig"]
