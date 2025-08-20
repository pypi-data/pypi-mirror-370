from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


class EQ(KMetadata, KValidation):
    def __init__(self, value: float | str) -> None:
        self._data = {"equals": value}

    def __str__(self) -> str:
        return f'==:{self._data["equals"]}'

    def load(self, str_repr: str) -> dict:
        segmented = str_repr.split(":")
        if not len(segmented) == 2 or segmented[0] != "==":
            return {}
        try:
            self._data["equals"] = float(segmented[1])
        except Exception:
            self._data["equals"] = segmented[1]
        return self._data
