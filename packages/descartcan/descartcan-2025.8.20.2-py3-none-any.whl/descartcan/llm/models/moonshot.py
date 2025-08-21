from descartcan.llm.models.base import BaseImplementStrategy


class MoonshotStrategy(BaseImplementStrategy):

    @classmethod
    def get_name(self) -> str:
        return "moonshot"

    @classmethod
    def base_url(self) -> str:
        return "https://api.moonshot.cn/v1"
