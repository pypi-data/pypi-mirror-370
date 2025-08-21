from descartcan.llm.models.base import BaseImplementStrategy


class SiliconFlowStrategy(BaseImplementStrategy):

    def get_name(self) -> str:
        return "siliconflow"

    def base_url(self) -> str:
        return "https://api.siliconflow.cn/v1"
