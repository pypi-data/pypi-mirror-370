from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


class Order(KMetadata, KValidation):
    def __init__(self, value: int) -> None:
        self._data = {"position": value}

    def __str__(self) -> str:
        return f'position:{self._data["position"]}'

    def load(self, str_repr: str) -> dict:
        segmented = str_repr.split(":")
        if not len(segmented) == 2 or segmented[0] != "position":
            return {}
        try:
            self._data["position"] = int(segmented[1])
        except Exception:
            self._data["position"] = segmented[1]
        return self._data
