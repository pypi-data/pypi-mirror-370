# #import pysnooper  # type: ignore

from logging import Logger, getLogger
from typing import Any, get_type_hints
from abc import ABC

log: Logger = getLogger(__name__)


class KConfig(ABC):
    name: str
    version: str
    display_label: str
    category: str
    description: str
    author: str
    author_email: str
    MANIFEST: dict
    DEFAULTS: dict
    _mandatory: list

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._mandatory = ["name", "version", "category", "author"]
        self.name = kwargs.get("name", "")
        self.version = kwargs.get("version", "")
        self.display_label = kwargs.get("display_label", "")
        self.category = kwargs.get("category", "")
        self.description = kwargs.get("description", "")
        self.author = kwargs.get("author", "")
        self.author_email = kwargs.get("author_email", "")
        self.MANIFEST = self._format_metadata(*args)

    #   #@pysnooper.snoop()
    def _format_metadata(self, *args: Any) -> dict:
        meta = {
            "PACKAGE": {
                "NAME": self.name,
                "LABEL": self.display_label,
                "VERSION": self.version,
                "DESCRIPTION": self.description,
                "CATEGORY": self.category,
            },
            "MODULES": {},
        }
        for arg in args:
            meta["MODULES"].update({arg[0]: arg[1].manifest})
        return meta

    def recompute_package_metadata(self, *args: Any) -> dict:
        log.info("Recomputing module package metadata...")
        self.MANIFEST = self._format_metadata(*args)
        log.debug(f"MANIFEST: {self.MANIFEST}")
        return self.MANIFEST

    def metadata(self) -> dict:
        log.info("Fething module metadata...")
        meta = get_type_hints(self, include_extras=True)
        log.debug(f"metadata: {meta}")
        return meta

    def data(self) -> dict:
        return self.__dict__
