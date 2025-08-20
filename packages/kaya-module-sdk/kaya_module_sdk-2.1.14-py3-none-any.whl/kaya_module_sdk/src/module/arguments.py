from logging import Logger, getLogger
from abc import ABC
from typing import Annotated, get_type_hints

from kaya_module_sdk.src.utils.metadata.display_description import DisplayDescription
from kaya_module_sdk.src.utils.metadata.display_name import DisplayName

log: Logger = getLogger(__name__)


class Args(ABC):
    _errors: Annotated[
        list[Exception],
        DisplayName("Errors"),
        DisplayDescription("Collection of things that went very, very wrong."),
    ]
    _live: Annotated[
        bool,
        DisplayName("Live Execution"),
        DisplayDescription(
            "Input provided by the Systemic runtime. Indicates if the current request is a historical"
            "backfilling request, or a LIVE execution request. Live requests should only return the"
            "last computed datapoint"
        ),
    ]

    def __init__(self, errors: list[Exception] | None = None, live: bool | None = None) -> None:
        self._errors = []
        self._live = False

        if errors is not None:
            self.set_errors(*errors)
        if live is not None:
            self.set_live(live)

    @property
    def errors(self) -> list[Exception]:
        return self._errors

    @property
    def live(self) -> bool:
        return self._live

    def set_errors(self, *values: Exception) -> None:
        self._errors += list(values)

    def set_live(self, value: bool) -> None:
        self._live = value

    def metadata(self) -> dict:
        return get_type_hints(self, include_extras=True)
