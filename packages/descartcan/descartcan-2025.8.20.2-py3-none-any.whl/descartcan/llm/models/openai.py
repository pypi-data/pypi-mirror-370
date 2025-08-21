from descartcan.llm.models.base import BaseImplementStrategy


class OpenaiStrategy(BaseImplementStrategy):
    def get_name(self) -> str:
        return "openai"

    def base_url(self) -> str:
        return "https://api.openai.com/v1"
