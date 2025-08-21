import json
import threading
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from os import PathLike
from pathlib import Path
from typing import Dict, List, Literal, Optional, Union

from pandas import DataFrame

from mitoolspro.exceptions import (
    ArgumentKeyError,
    ArgumentTypeError,
    ArgumentValueError,
)


class ModelRegistry:
    _instances = {}

    OPENAI_MODELS = {
        "gpt-3.5-turbo": {"input": 3.0, "output": 8.0},
        "gpt-4o-mini": {"input": 0.15, "output": 0.6},
        "gpt-4o": {"input": 2.5, "output": 10.0},
        "o1-preview": {"input": 15.0, "output": 60.0},
        "o1": {"input": 15.0, "output": 60.0},
        "o1-mini": {"input": 3.0, "output": 12.0},
    }
    ANTHROPIC_MODELS = {
        "claude-3-opus": {"input": 0.0, "output": 0.0},
    }
    GOOGLE_MODELS = {
        "gemini-1.5-flash": {"input": 0.0, "output": 0.0},
    }

    @classmethod
    def get_instance(cls, source: Literal["openai", "anthropic", "google"]):
        if source not in ["openai", "anthropic", "google"]:
            raise ArgumentValueError(f"Source {source} not supported.")
        if source not in cls._instances:
            cls._instances[source] = cls(source)
        return cls._instances[source]

    def __init__(self, source: Literal["openai", "anthropic", "google"]):
        if source in ["anthropic", "google"]:
            raise ArgumentValueError(f"Source {source} not supported yet.")
        self.source = source
        self.models = getattr(self, f"{source.upper()}_MODELS", {})

    def get_model_cost(self, name: str) -> Dict:
        if name not in self.models:
            raise ArgumentValueError(f"Model {name} not supported for {self.source}")
        return self.models[name]


class Prompt:
    def __init__(self, text: str, metadata: Optional[Dict[str, str]] = None):
        if not isinstance(text, str) or not text.strip():
            raise ArgumentValueError("Prompt must be a non-empty string.")
        self.text = text.strip()
        self.metadata = metadata or {}

    def __repr__(self) -> str:
        return f"Prompt(\ntext={self.text},\n metadata={self.metadata}\n)"

    def __add__(self, other: Union["Prompt", str]) -> "Prompt":
        if isinstance(other, Prompt):
            combined_text = f"{self.text}\n{other.text}"
            combined_metadata = {
                **other.metadata,
                **self.metadata,
            }  # self.metadata has priority over other.metadata
            return Prompt(combined_text, combined_metadata)
        elif isinstance(other, str):
            combined_text = f"{self.text}\n{other.strip()}"
            return Prompt(combined_text, self.metadata)
        else:
            raise ArgumentTypeError("Can only concatenate with a Prompt or a string.")

    def __iadd__(self, other: Union["Prompt", str]) -> "Prompt":
        concatenated = self + other
        self.text = concatenated.text
        self.metadata = concatenated.metadata
        return self

    def format(self, **kwargs) -> "Prompt":
        try:
            formatted_text = self.text.format(**kwargs)
            return Prompt(text=formatted_text, metadata=self.metadata)
        except KeyError as e:
            raise ArgumentKeyError(f"String missing formatting key: {e}")

    def update_metadata(self, key: str, value: str) -> None:
        if not isinstance(key, str) or not isinstance(value, str):
            raise ArgumentValueError("Metadata keys and values must be strings.")
        self.metadata[key] = value

    def get_metadata(self, key: str) -> Optional[str]:
        return self.metadata.get(key)

    def to_dict(self) -> Dict[str, Union[str, Dict[str, str]]]:
        return {"text": self.text, "metadata": self.metadata}

    @classmethod
    def from_dict(cls, data: Dict[str, Union[str, Dict[str, str]]]) -> "Prompt":
        if "text" not in data:
            raise ArgumentValueError("Dictionary must contain a 'text' key.")
        return cls(text=data["text"], metadata=data.get("metadata", {}))

    @staticmethod
    def concatenate(
        prompts: List[Union["Prompt", str]], separator: str = "\n"
    ) -> "Prompt":
        combined_texts = []
        combined_metadata = {}
        for prompt in prompts:
            if isinstance(prompt, Prompt):
                combined_texts.append(prompt.text)
                combined_metadata.update(prompt.metadata)
            elif isinstance(prompt, str):
                combined_texts.append(prompt.strip())
            else:
                raise ArgumentTypeError(
                    "List must contain only Prompt instances or strings."
                )
        return Prompt(text=separator.join(combined_texts), metadata=combined_metadata)


class LLMModel(ABC):
    @abstractmethod
    def request(self, request: Prompt, **kwargs) -> Dict:
        pass

    @abstractmethod
    def parse_request(self, prompt: Prompt, **kwargs) -> Dict:
        pass

    @abstractmethod
    def _get_response(self, prompt) -> Dict:
        pass

    @abstractmethod
    def parse_response(self, response: Dict) -> str:
        pass

    @abstractmethod
    def get_model_info(self) -> Dict:
        pass

    @abstractmethod
    def model_name(self) -> str:
        pass


class LLMFactory:
    def __init__(self):
        self.registry = {}

    def register_client(self, name, client_class):
        self.registry[name] = client_class

    def get_client(self, name, **kwargs):
        if name not in self.registry:
            raise ValueError(f"Model '{name}' not supported.")
        return self.registry[name](**kwargs)


@dataclass
class TokenUsageStats:
    source: Literal["openai", "anthropic", "google"]
    model: str
    model_cost: Dict[str, int | float]
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    cost: float
    timestamp: datetime


class TokensCounter(ABC):
    def __init__(self, source: Literal["openai", "anthropic", "google"], model: str):
        self.source = source
        self.model_registry = ModelRegistry.get_instance(self.source)
        self.model = model
        self.model_cost = self.model_registry.get_model_cost(self.model)
        self.usage_history: List[TokenUsageStats] = []
        self.prompt_tokens_count: int = 0
        self.completion_tokens_count: int = 0
        self.total_tokens_count: int = 0
        self.total_cost: float = 0.0
        self.max_context_length: Optional[int] = None

    @abstractmethod
    def get_usage_stats(self, response: Dict) -> TokenUsageStats:
        pass

    def update(self, usage: TokenUsageStats) -> None:
        self.usage_history.append(usage)
        self.total_cost += usage.cost
        self.prompt_tokens_count += usage.prompt_tokens
        self.completion_tokens_count += usage.completion_tokens
        self.total_tokens_count = (
            self.prompt_tokens_count + self.completion_tokens_count
        )

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        pass

    def set_max_context_length(self, max_length: int) -> None:
        self.max_context_length = max_length

    def would_exceed_context(self, text: str) -> bool:
        if self.max_context_length is None:
            return False
        return self.count_tokens(text) > self.max_context_length

    def _calculate_cost(self) -> float:
        return sum(usage.cost for usage in self.usage_history)

    def _calculate_input_cost(self, input_token_count: Optional[int] = None) -> float:
        if input_token_count is None:
            return sum(
                usage.prompt_tokens * (usage.model_cost["input"] / 1_000_000)
                for usage in self.usage_history
            )
        return input_token_count * (self.model_cost["input"] / 1_000_000)

    def _calculate_output_cost(self, output_token_count: Optional[int] = None) -> float:
        if output_token_count is None:
            return sum(
                usage.completion_tokens * (usage.model_cost["output"] / 1_000_000)
                for usage in self.usage_history
            )
        return output_token_count * (self.model_cost["output"] / 1_000_000)

    @property
    def count(self) -> int:
        return self.total_tokens_count

    @property
    def cost(self) -> float:
        return self._calculate_cost()

    @property
    def cost_detail(self) -> Dict:
        return {
            "prompt_tokens": self._calculate_input_cost(),
            "completion_tokens": self._calculate_output_cost(),
            "total": self.cost,
        }

    def json(self) -> str:
        data = {
            "usage_history": [asdict(usage) for usage in self.usage_history],
            "prompt_tokens_count": self.prompt_tokens_count,
            "completion_tokens_count": self.completion_tokens_count,
            "total_tokens_count": self.total_tokens_count,
            "max_context_length": self.max_context_length,
            "cost_detail": self.cost_detail,
            "model": self.model,
            "source": self.source,
        }
        return json.dumps(data, indent=4, default=str)

    def save(self, file_path: PathLike) -> None:
        if Path(file_path).suffix != ".json":
            raise ArgumentValueError("File path must have a .json extension.")
        with open(file_path, "w") as f:
            f.write(self.json())

    @classmethod
    def load(cls, file_path: PathLike) -> "TokensCounter":
        with open(file_path, "r") as f:
            data = json.load(f)
        instance = cls(data["source"], data["model"])
        instance.prompt_tokens_count = data["prompt_tokens_count"]
        instance.completion_tokens_count = data["completion_tokens_count"]
        instance.total_tokens_count = data["total_tokens_count"]
        instance.max_context_length = data["max_context_length"]
        instance.usage_history = [
            TokenUsageStats(**usage) for usage in data["usage_history"]
        ]
        return instance

    def usage(self) -> DataFrame:
        return DataFrame([asdict(usage) for usage in self.usage_history])


class PersistentTokensCounter(TokensCounter):
    _instances = {}
    _lock = threading.Lock()

    def __new__(cls, file_path: PathLike, source: str, model: str, *args, **kwargs):
        file_path = Path(file_path).absolute()
        with cls._lock:
            if file_path not in cls._instances:
                cls._instances[file_path] = super(PersistentTokensCounter, cls).__new__(
                    cls
                )
        return cls._instances[file_path]

    def __init__(
        self,
        file_path: PathLike,
        source: Literal["openai", "anthropic", "google"],
        model: str,
    ):
        self.file_path = Path(file_path).absolute()
        if not hasattr(self, "_initialized"):
            super().__init__(source=source, model=model)
            if self.file_path.exists():
                instance_data = self._load_instance_data(self.file_path)
                for usage in instance_data["usage_history"]:
                    self.update(TokenUsageStats(**usage))
                self.max_context_length = instance_data.get("max_context_length")
            else:
                self.save(self.file_path)
            self._initialized = True
        else:
            self.source = source
            self.model = model
            self.model_registry = ModelRegistry.get_instance(self.source)
            self.model_cost = self.model_registry.get_model_cost(self.model)

    def _load_instance_data(self, file_path: PathLike) -> Dict:
        with open(file_path, "r") as f:
            data = json.load(f)
        return data

    def update(self, usage: TokenUsageStats) -> None:
        super().update(usage)
        self.save(self.file_path)

    def save(self, file_path: PathLike = None) -> None:
        file_path = file_path or self.file_path
        super().save(file_path)

    @classmethod
    def load(cls, file_path: PathLike) -> "PersistentTokensCounter":
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"No file found at {file_path}")
        with open(file_path, "r") as f:
            data = json.load(f)
        # Use the most recent model in the usage history, or default to the last known model
        last_usage = data["usage_history"][-1] if data["usage_history"] else None
        source = last_usage["source"] if last_usage else data.get("source")
        model = last_usage["model"] if last_usage else data.get("model")

        return cls(file_path=file_path, source=source, model=model)
