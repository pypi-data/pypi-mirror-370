from abc import ABC


class KMetadata(ABC):
    _data: dict

    def __repr__(self) -> str:
        return self.__str__()
