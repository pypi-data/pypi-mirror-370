import os
from descartcan.llm.models.base import BaseImplementStrategy


class OllamaStrategy(BaseImplementStrategy):
    def get_name(self) -> str:
        return "ollama"

    def base_url(self) -> str:
        return os.getenv("OLLAMA_BASE_URL", "https://localhost:11434")
