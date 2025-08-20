from abc import ABC, abstractmethod


class KValidation(ABC):
    def __repr__(self) -> str:
        return self.__str__()

    @abstractmethod
    def __str__(self) -> str:
        return str(self)
