from importlib.resources import files, as_file

from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata


def load_markdown(location_of: str, file_name: str) -> str:
    resource = files(location_of).joinpath(file_name)
    with as_file(resource) as file_path:  # Ensures compatibility with non-filesystem resources
        with open(file_path, "r") as file:
            content = file.read()
    return content


class DisplayDescription(KMetadata):
    def __init__(self, description: str) -> None:
        self._data = {
            "description": description,
        }

    def __str__(self) -> str:
        return f'description:{self._data["description"]}'

    def load(self, str_repr: str) -> dict:
        segmented = str_repr.split(":")
        if not len(segmented) == 2 or segmented[0] != "description":
            return {}
        self._data["description"] = segmented[1]
        return self._data
