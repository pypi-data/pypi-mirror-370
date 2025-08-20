import logging
from abc import ABC, abstractmethod

from beartype import beartype
from beartype.typing import Any, Dict

logger = logging.getLogger(__name__)


@beartype
class BackendBase(ABC):
    """Base abstract class for tool backends."""

    @abstractmethod
    def execute(self, query: str) -> str: ...
    @abstractmethod
    def initialize(self) -> None: ...
    @abstractmethod
    def teardown(self) -> None: ...
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]: ...
    @classmethod
    @abstractmethod
    def from_dict(cls, params: Dict[str, Any]) -> "BackendBase": ...

    def __getstate__(self) -> dict:
        return self.__dict__.copy()

    def __setstate__(self, state: dict) -> None:
        self.__dict__.update(state)
