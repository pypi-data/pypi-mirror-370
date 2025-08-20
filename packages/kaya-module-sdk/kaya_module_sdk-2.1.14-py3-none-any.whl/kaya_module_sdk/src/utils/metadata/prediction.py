from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation


class Prediction(KMetadata, KValidation):
    def __init__(self, value: bool | str) -> None:
        self._data = {
            "prediction": value,
        }

    def __str__(self) -> str:
        return f'prediction:{self._data["prediction"]}'

    def load(self, str_repr: str) -> dict:
        segmented = str_repr.split(":")
        if not len(segmented) == 2 or segmented[0] != "prediction":
            return {}
        try:
            self._data["prediction"] = eval(segmented[1])
        except Exception:
            self._data["prediction"] = segmented[1]
        return self._data
