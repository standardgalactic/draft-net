from __future__ import annotations

from abc import ABC, abstractmethod


class BaseEncoder(ABC):
    @abstractmethod
    def encode(self, content: str) -> list[float]:
        raise NotImplementedError
