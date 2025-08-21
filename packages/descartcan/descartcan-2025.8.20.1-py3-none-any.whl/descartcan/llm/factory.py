from typing import Dict, List, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
import yaml
from descartcan.llm.exceptions import ModelNotFoundError
from descartcan.llm.models.base import ModelStrategy
from descartcan.utils.log import logger
from descartcan.llm.models.alibaba import AlibabaStrategy
from descartcan.llm.models.openai import OpenaiStrategy
from descartcan.llm.models.anthropic import AnthropicStrategy
from descartcan.llm.models.bedrock import BedrockStrategy
from descartcan.llm.models.deepseek import DeepSeekStrategy
from descartcan.llm.models.moonshot import MoonshotStrategy
from descartcan.llm.models.ollama import OllamaStrategy
from descartcan.llm.models.zhipu import ZhipuStrategy
from descartcan.llm.models.siliconflow import SiliconFlowStrategy


@dataclass
class ModelProperty:
    name: str
    max_input_token: int = 4096
    max_output_token: int = 2048
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 1.0
    timeout: float = 60.0
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    stop: [List[str]] = None


@dataclass
class ModelConfig:
    name: ModelProperty
    keys: Dict[str, Dict[str, str]]
    models: Dict[str, str]


class BaseLoader(ABC):
    def __init__(self, provider_map: Dict):
        self.provider_map = provider_map
        self._registered_models = set()
        self.factory = LLModelFactory()

    @abstractmethod
    def load(self) -> "LLModelFactory":
        pass

    def _process_model_config(
        self, provider: str, provider_config: Dict
    ) -> ModelConfig:
        keys = {}
        for key_config in provider_config.get("keys", []):
            keys[key_config["name"]] = {
                "api_key": key_config["api_key"],
                "api_secret": key_config.get("api_secret", ""),
                "api_region": key_config.get("api_region", None),
            }

        return ModelConfig(
            name=ModelProperty(name=provider),
            keys=keys,
            models=provider_config.get("models", {}),
        )

    def _create_models(self, provider: str, config: ModelConfig) -> List[ModelStrategy]:
        provider_strategy = self.provider_map.get(provider)
        if not provider_strategy:
            raise ValueError(f"不支持的提供商: {provider}")

        models = []
        for alias, model_name in config.models.items():
            model_id = f"{provider}.{alias}"
            if model_id in self._registered_models:
                logger.warning(f"模型已存在: {model_id}")
                continue

            self._registered_models.add(model_id)
            model_prop = ModelProperty(name=model_name)
            models.append((model_id, provider_strategy(config.keys, model_prop)))

        return models

    def _process_config(self, config: Dict) -> "LLModelFactory":
        for provider, provider_config in config.items():
            try:
                model_conf = self._process_model_config(provider, provider_config)
                models = self._create_models(provider, model_conf)
                for model_id, model in models:
                    self.factory.register_model_instance(model_id, model)
            except ValueError as e:
                logger.warning(f"跳过提供商 {provider} 的注册: {e}")
        return self.factory


class DictLoader(BaseLoader):
    def __init__(self, config_dict: Dict, provider_map: Dict):
        super().__init__(provider_map)
        self.config_dict = config_dict

    def load(self) -> "LLModelFactory":
        return self._process_config(self.config_dict)


class YAMLLoader(BaseLoader):
    def __init__(self, config_file: str, provider_map: Dict):
        super().__init__(provider_map)
        self.config_file = config_file

    def load(self) -> "LLModelFactory":
        try:
            with open(self.config_file, "r") as f:
                config = yaml.safe_load(f)
            return self._process_config(config)
        except Exception as e:
            logger.error(f"加载YAML配置失败: {e}")
            raise


class LLModelFactory:
    PROVIDER_MAP = {
        "alibaba": AlibabaStrategy,
        "openai": OpenaiStrategy,
        "anthropic": AnthropicStrategy,
        "bedrock": BedrockStrategy,
        "deepseek": DeepSeekStrategy,
        "moonshot": MoonshotStrategy,
        "ollama": OllamaStrategy,
        "zhipu": ZhipuStrategy,
        "siliconflow": SiliconFlowStrategy,
    }

    def __init__(self):
        self._model_instances: Dict[str, ModelStrategy] = {}

    def register_model_instance(self, name: str, model_instance: ModelStrategy):
        self._model_instances[name] = model_instance

    def get_model(self, name: str) -> ModelStrategy:
        model = self._model_instances.get(name)
        if not model:
            raise ModelNotFoundError(name)
        return model

    def all_models(self) -> Dict[str, ModelStrategy]:
        return self._model_instances

    @classmethod
    def from_config(cls, config: Union[str, Dict]) -> "LLModelFactory":
        factory = cls()
        try:
            if isinstance(config, str):
                loader = YAMLLoader(config, cls.PROVIDER_MAP)
            else:
                loader = DictLoader(config, cls.PROVIDER_MAP)
            loaded_factory = loader.load()
            factory._model_instances.update(loaded_factory._model_instances)
            return factory
        except Exception as e:
            logger.error(f"加载模型配置失败: {e}")
            raise
