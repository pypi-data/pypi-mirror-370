from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


class NotConst(KMetadata, KValidation):
    def __init__(self, value: bool | str) -> None:
        self._data = {
            "not_const": value,
        }

    def __str__(self) -> str:
        return f'notconst:{self._data["not_const"]}'

    def load(self, str_repr: str) -> dict:
        segmented = str_repr.split(":")
        if not len(segmented) == 2 or segmented[0] != "notconst":
            return {}
        try:
            self._data["not_const"] = eval(segmented[1])
        except Exception:
            self._data["not_const"] = segmented[1]
        return self._data
