from logging import Logger, getLogger
from abc import ABC
from typing import Annotated, Any, get_type_hints

from kaya_module_sdk.src.utils.constraints.min_len import kminlen
from kaya_module_sdk.src.utils.metadata.display_description import DisplayDescription
from kaya_module_sdk.src.utils.metadata.display_name import DisplayName
from kaya_module_sdk.src.utils.metadata.min_len import MinLen

log: Logger = getLogger(__name__)


class Rets(ABC):
    _results: Annotated[
        list[Any],
        DisplayName("Result"),
        DisplayDescription("Module computation results."),
        MinLen(1),
    ]
    _errors: Annotated[
        list[Exception],
        DisplayName("Errors"),
        DisplayDescription("Collection of things that went very, very wrong."),
    ]

    def __init__(self, results: list | None = None, errors: list | None = None):
        self._results = []
        self._errors = []

        if results is not None:
            self.set_results(results)
        if errors is not None:
            self.set_errors(*errors)

    @property
    def results(self) -> list[Any]:
        return self._results

    @property
    def errors(self) -> list[Exception]:
        return self._errors

    @kminlen(1)
    def set_results(self, *values: Any) -> None:
        self._results += list(values)

    def set_errors(self, *values: Exception) -> None:
        self._errors += list(values)

    def metadata(self) -> dict:
        return get_type_hints(self, include_extras=True)
