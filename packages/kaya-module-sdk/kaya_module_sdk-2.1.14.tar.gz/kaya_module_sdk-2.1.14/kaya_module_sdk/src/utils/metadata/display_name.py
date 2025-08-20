from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata


class DisplayName(KMetadata):
    def __init__(self, name: str) -> None:
        self._data = {
            "name": name,
        }

    def __str__(self) -> str:
        return f'name:{self._data["name"]}'

    def load(self, str_repr: str) -> dict:
        segmented = str_repr.split(":")
        if not len(segmented) == 2 or segmented[0] != "name":
            return {}
        self._data["name"] = segmented[1]
        return self._data
