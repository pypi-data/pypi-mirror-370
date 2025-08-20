from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


class Min(KMetadata, KValidation):
    def __init__(self, value: float | str) -> None:
        self._data = {"minimum": value}

    def __str__(self) -> str:
        return f'min:{self._data["minimum"]}'

    def load(self, str_repr: str) -> dict:
        segmented = str_repr.split(":")
        if not len(segmented) == 2 or segmented[0] != "min":
            return {}
        try:
            self._data["minimum"] = float(segmented[1])
        except Exception:
            self._data["minimum"] = segmented[1]
        return self._data
