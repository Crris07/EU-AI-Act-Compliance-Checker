from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


ROOT_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    llm_provider: str = Field(default="ollama", alias="LLM_PROVIDER")
    ollama_model: str = Field(default="llama3.2:3b", alias="OLLAMA_MODEL")
    mistral_api_key: str | None = Field(default=None, alias="MISTRAL_API_KEY")
    mistral_model: str = Field(default="mistral-small-latest", alias="MISTRAL_MODEL")
    embed_model: str = Field(default="BAAI/bge-small-en-v1.5", alias="EMBED_MODEL")
    chroma_path: str = Field(default="data/chroma_db", alias="CHROMA_PATH")
    chroma_collection: str = Field(default="eu_ai_act", alias="CHROMA_COLLECTION")
    top_k: int = Field(default=6, alias="TOP_K")

    @property
    def chroma_dir(self) -> Path:
        return ROOT_DIR / self.chroma_path


settings = Settings()
