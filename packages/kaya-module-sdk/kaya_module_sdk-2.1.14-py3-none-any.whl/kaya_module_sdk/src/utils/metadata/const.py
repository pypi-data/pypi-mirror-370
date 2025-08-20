from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


class Const(KMetadata, KValidation):
    def __init__(self, value: bool | str) -> None:
        self._data = {
            "const": value,
        }

    def __str__(self) -> str:
        return f'const:{self._data["const"]}'

    def load(self, str_repr: str) -> dict:
        segmented = str_repr.split(":")
        if not len(segmented) == 2 or segmented[0] != "const":
            return {}
        try:
            self._data["const"] = eval(segmented[1])
        except Exception:
            self._data["const"] = segmented[1]
        return self._data
