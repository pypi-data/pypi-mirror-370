class LLMException(Exception):
    """LLM基础异常类"""

    pass


class ConfigurationException(LLMException):
    """配置相关异常"""

    pass


class ModelNotFoundError(Exception):
    def __init__(self, model_name: str):
        super().__init__(f"Model '{model_name}' not found in the model instances.")
