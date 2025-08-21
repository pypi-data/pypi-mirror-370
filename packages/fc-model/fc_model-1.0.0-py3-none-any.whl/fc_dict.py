
from abc import ABC, abstractmethod
from typing import Generic, TypeVar


S = TypeVar("S")


class FCSrcRequiredId(Generic[S], ABC):
    id: int
    
    @abstractmethod
    def __init__(self, src_data: S):
        pass

    @abstractmethod
    def dump(self) -> S:
        pass


T = TypeVar("T", bound=FCSrcRequiredId)