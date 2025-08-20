from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


class EQLen(KMetadata, KValidation):
    def __init__(self, value: int | str) -> None:
        self._data = {
            "eq_len": value,
        }

    def __str__(self) -> str:
        return f'eqlen:{self._data["eq_len"]}'

    def load(self, str_repr: str) -> dict:
        segmented = str_repr.split(":")
        if not len(segmented) == 2 or segmented[0] != "eqlen":
            return {}
        try:
            self._data["eq_len"] = int(segmented[1])
        except Exception:
            self._data["eq_len"] = segmented[1]
        return self._data
