from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Semantic Search Engine"
    app_env: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    top_k: int = 5
    chunk_size: int = 180
    chunk_overlap: int = 30

    data_dir: Path = PROJECT_ROOT / "data"
    raw_data_dir: Path = PROJECT_ROOT / "data" / "raw"
    processed_data_dir: Path = PROJECT_ROOT / "data" / "processed"
    index_dir: Path = PROJECT_ROOT / "data" / "indices"

    @property
    def vector_index_path(self) -> Path:
        return self.index_dir / "semantic.index"

    @property
    def metadata_path(self) -> Path:
        return self.index_dir / "metadata.json"

    def ensure_directories(self) -> None:
        for directory in (self.data_dir, self.raw_data_dir, self.processed_data_dir, self.index_dir):
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()