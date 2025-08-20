from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


class Max(KMetadata, KValidation):
    def __init__(self, value: float | str) -> None:
        self._data = {
            "maximum": value,
        }

    def __str__(self) -> str:
        return f'max:{self._data["maximum"]}'

    def load(self, str_repr: str) -> dict:
        segmented = str_repr.split(":")
        if not len(segmented) == 2 or segmented[0] != "max":
            return {}
        try:
            self._data["maximum"] = float(segmented[1])
        except Exception:
            self._data["maximum"] = segmented[1]
        return self._data
