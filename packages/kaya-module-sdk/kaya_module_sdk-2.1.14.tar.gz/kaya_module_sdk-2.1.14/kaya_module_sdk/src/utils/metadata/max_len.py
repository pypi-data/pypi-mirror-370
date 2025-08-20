from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


class MaxLen(KMetadata, KValidation):
    def __init__(self, value: float | str) -> None:
        self._data = {
            "max_len": value,
        }

    def __str__(self) -> str:
        return f'maxlen:{self._data["max_len"]}'

    def load(self, str_repr: str) -> dict:
        segmented = str_repr.split(":")
        if not len(segmented) == 2 or segmented[0] != "maxlen":
            return {}
        try:
            self._data["max_len"] = float(segmented[1])
        except Exception:
            self._data["max_len"] = segmented[1]
        return self._data
