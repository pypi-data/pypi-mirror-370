from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


class Variadic(KMetadata, KValidation):
    def __init__(self, min_val: float | str, max_val: float | str) -> None:
        self._data = {
            "min_val": min_val,
            "max_val": max_val,
        }

    def __str__(self) -> str:
        return f'variadic:{self._data["min_val"]};{self._data["max_val"]}'

    def load(self, str_repr: str) -> dict:
        segmented = str_repr.split(":")
        if not len(segmented) == 2 or segmented[0] != "variadic":
            return {}
        segmented = segmented[1].split(";")
        if not len(segmented) == 2:
            return {}
        try:
            self._data.update(
                {
                    "min_val": float(segmented[0]),
                    "max_val": float(segmented[1]),
                }
            )
        except Exception:
            self._data.update(
                {
                    "min_val": segmented[0],
                    "max_val": segmented[1],
                }
            )
        return self._data
