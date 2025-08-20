from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


class LTE(KMetadata, KValidation):
    def __init__(self, value: float | str) -> None:
        self._data = {
            "less_than_or_equal_to": value,
        }

    def __str__(self) -> str:
        return f'<=:{self._data["less_than_or_equal_to"]}'

    def load(self, str_repr: str) -> dict:
        segmented = str_repr.split(":")
        if not len(segmented) == 2 or segmented[0] != "<=":
            return {}
        try:
            self._data["less_than_or_equal_to"] = float(segmented[1])
        except Exception:
            self._data["less_than_or_equal_to"] = segmented[1]
        return self._data
