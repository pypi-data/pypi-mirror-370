from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class ModelParameters:
    temperature: float = 1.0
    top_p: float = 1.0
    max_tokens: Optional[int] = None
    timeout: Optional[int] = None
    stop: Optional[list] = None
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


class ModelParametersBuilder:
    def __init__(self):
        self._params = ModelParameters()

    def temperature(self, value: float) -> "ModelParametersBuilder":
        self._params.temperature = max(0.0, min(2.0, value))
        return self

    def top_p(self, value: float) -> "ModelParametersBuilder":
        self._params.top_p = max(0.0, min(1.0, value))
        return self

    def max_tokens(self, value: int) -> "ModelParametersBuilder":
        self._params.max_tokens = value
        return self

    def timeout(self, value: int) -> "ModelParametersBuilder":
        self._params.timeout = value
        return self

    def stop(self, value: list) -> "ModelParametersBuilder":
        self._params.stop = value
        return self

    def presence_penalty(self, value: float) -> "ModelParametersBuilder":
        self._params.presence_penalty = max(-2.0, min(2.0, value))
        return self

    def frequency_penalty(self, value: float) -> "ModelParametersBuilder":
        self._params.frequency_penalty = max(-2.0, min(2.0, value))
        return self

    def build(self) -> ModelParameters:
        return self._params
