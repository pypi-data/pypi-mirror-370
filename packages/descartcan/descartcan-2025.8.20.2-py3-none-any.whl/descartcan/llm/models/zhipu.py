from descartcan.llm.models.base import BaseImplementStrategy


class ZhipuStrategy(BaseImplementStrategy):

    def get_name(self) -> str:
        return "zhipu"

    def base_url(self) -> str:
        return "https://open.bigmodel.cn/api/paas/v4/"
