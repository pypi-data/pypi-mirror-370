from descartcan.llm.models.base import BaseImplementStrategy


class AlibabaStrategy(BaseImplementStrategy):
    @classmethod
    def base_url(self) -> str:
        return "https://dashscope.aliyuncs.com/api/v1"

    @classmethod
    def get_name(self) -> str:
        return "alibaba"
