from descartcan.llm.models.base import BaseImplementStrategy


class DeepSeekStrategy(BaseImplementStrategy):

    @classmethod
    def get_name(self) -> str:
        return "deepseek"

    @classmethod
    def base_url(self) -> str:
        return "https://api.deepseek.com/v1"
