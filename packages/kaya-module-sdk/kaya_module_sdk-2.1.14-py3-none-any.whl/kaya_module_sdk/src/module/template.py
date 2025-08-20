import importlib
import inspect
import heapq
import os

# import pysnooper  # type: ignore

from logging import Logger, LoggerAdapter, getLogger
from logging.handlers import RotatingFileHandler
from abc import ABC, abstractmethod
from typing import Annotated, Any, Callable, get_args, get_origin, get_type_hints

from mypy.moduleinspect import ModuleType

from kaya_module_sdk.src.module.arguments import Args
from kaya_module_sdk.src.module.config import KConfig
from kaya_module_sdk.src.module.returns import Rets
from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation
from kaya_module_sdk.src.datatypes.classifier import KClassifier
from kaya_module_sdk.src.utils.metadata.display_description import DisplayDescription
from kaya_module_sdk.src.utils.metadata.display_name import DisplayName

from kaya_module_sdk.src.utils.logger import setup_datadog_logging, setup_logging, DatadogJSONFormatter


class Config(KConfig):
    def __init__(self) -> None:
        super().__init__()


class Module(ABC):
    """
    [ DESCRIPTION ]: Kaya Strategy Module Template.

    [ MANIFEST ]: {
        "moduleName": "string",         -- Name of the module
        "moduleDisplayLabel": "string", -- Display label for this module in the frontend
        "moduleCategory": "enum",       -- Category of the module. An ENUM defined by the NeptuneAPI smithy model.
        "moduleDescription": "string",  -- Description of the module
        "author": "kaya_id(user)",      -- UserID of the User vertex that owns this module.
        "inputs": [{
            "name": "string",           -- Name of the input field in the request object
            "label": "string",          -- Display label for this input in the frontend
            "type": "kaya_id(value)",   -- VertexID of the value that represents this input datatype
            "description": "string",    -- Description of the INPUT
            "validations": [
                "validation_pattern"    -- An array of validation queries to run against the inputs.
            ]}
        ],
        "outputs": [{
            "name": "string",           -- Name of the output field in the returned structure
            "label": "string",          -- Display label for this output in the frontend
            "type": "kaya_id(value)",   -- VertexID of the value that represents this output datatype
            "description": "string"     -- Description of the output
            "validations": [
                "validation_pattern"    -- An array of validation queries to run against the inputs.
            ]}
        ]
    }
    """

    config: KConfig
    log: Logger | LoggerAdapter[Logger]
    subclasses: list = []
    modules: dict = {}
    _manifest: dict = {}
    _recompute_manifest: bool = True

    def __init__(self) -> None:
        self.log = self._get_logger(self.__class__, "Module", "2.1.13")
        self.config = Config()
        self.import_subclasses()
        self.modules = {item.__class__.__name__: item for item in self.subclasses}

    def _get_logger(
        self,
        cls: type,
        service: str,
        version: str,
        level: str = "",
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5,
        **extra_fields: dict[str, Any],
    ) -> LoggerAdapter[Logger]:
        """
        Returns a logger adapter for the given (strategy module) class.
        Each class gets its own log file <service>.<package>.<class>.log (in PROD/STAGING).
        In DEV, logs go exclusively to STDOUT.
        """
        environment = os.environ.get("KAYA_STAGE", "PROD")
        log_level = level or os.getenv("KAYA_LOG_LVL", "INFO")
        log_name = f"{service}.{cls.__name__}"
        if os.getenv("KAYA_LOG_NAME"):
            log_name = os.getenv("KAYA_LOG_NAME", "") + "." + log_name
        logger = getLogger(log_name)
        # Only write to file on PROD and STAGING environments - DEV only to STDOUT
        if environment in ("PROD", "STAGING"):
            log_dir = os.getenv("KAYA_LOG_DIR", "/var/log") + "/kaya_modules/"
            os.makedirs(log_dir, exist_ok=True)
            file_handler = RotatingFileHandler(
                filename=f"{log_dir}/{log_name}.log",
                mode="a",
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8",
            )
            file_handler.setFormatter(DatadogJSONFormatter())
            file_handler.setLevel(log_level)
            logger.addHandler(file_handler)
        logger.setLevel(log_level)
        return LoggerAdapter(
            logger,
            extra={
                "class": cls.__name__,
                "dd.service": service,
                "dd.env": environment,
                "dd.version": version,
                **extra_fields,
            },
        )

    # @pysnooper.snoop()
    def import_subclasses(self) -> list:
        self.log.debug("Importing module package subclasses...")
        module_name = self.__module__
        self.log.info("Importing package %s", module_name)
        package = importlib.import_module(module_name).__package__
        self.log.info("Searching package for subclasses at %s.module", package)
        if not package:
            self.log.debug(f"Subclasses: {self.subclasses}")
            return self.subclasses
        try:
            module = importlib.import_module(f"{package}.module")
            self.log.debug(f"Module: {module}")
        except (TypeError, ModuleNotFoundError):
            self.log.debug(f"Subclasses: {self.subclasses}")
            return self.subclasses
        self._add_subclasses_from_module(module)
        return self.subclasses

    # @pysnooper.snoop()
    def _add_subclasses_from_module(self, module: ModuleType) -> None:
        """Add subclasses of Module from the given module."""
        self.log.debug("Adding subclasses of Module package from given module...")
        for _, obj in inspect.getmembers(module):
            if self._is_valid_subclass(obj):
                subclass_instance = obj()
                self.log.debug(f"Identified valid subclass: {subclass_instance}")
                self.subclasses.append(subclass_instance)

    @staticmethod
    def _is_valid_subclass(obj: type) -> bool:
        """Check if a class is a valid subclass of Module."""
        return (
            inspect.isclass(obj)
            and issubclass(obj, Module)
            and obj not in [Module, Args, Rets, KConfig, KMetadata, KValidation]
            and obj.__name__ != "KayaStrategyModule"
        )

    # @pysnooper.snoop()
    def _extract_manifest(self) -> dict[str, Any]:
        self.log.debug("Extracting manifest...")
        main_method = self.main
        self.log.debug(f"main_method: {main_method}")
        type_hints = get_type_hints(main_method)
        self.log.debug(f"type_hints: {type_hints}")
        params_metadata = self._get_params_metadata(main_method, type_hints)
        self.log.debug(f"params_metadata: {params_metadata}")
        rets_metadata = self._get_return_metadata(main_method, type_hints)
        self.log.debug(f"rets_metadata: {rets_metadata}")
        metadata = self._build_metadata(params_metadata, rets_metadata)
        self.log.debug(f"metadata: {metadata}")
        return metadata

    # @pysnooper.snoop()
    def _get_return_metadata(self, main_method: Callable, type_hints: dict) -> dict:
        """Return metadata for method return values"""
        self.log.debug("Extracting method return metadata...")
        expected_type = type_hints.get("return", "Any")
        return {
            "expected_type": expected_type,
            "details": (self._get_class_metadata(expected_type) if inspect.isclass(expected_type) else None),
        }

    # @pysnooper.snoop()
    def _get_params_metadata(self, main_method: Callable, type_hints: dict) -> dict:
        """Return metadata for method parameters."""
        self.log.debug("Extracting method parameter metadata...")
        signature = inspect.signature(main_method)
        self.log.debug(f"signature: {signature}")
        params_metadata = {}
        for param_name, param in signature.parameters.items():
            expected_type = type_hints.get(param_name, "Any")
            params_metadata[param_name] = {
                "expected_type": expected_type,
                "annotation": param.annotation,
                "details": (self._get_class_metadata(expected_type) if inspect.isclass(expected_type) else None),
            }
        return params_metadata

    def _build_metadata(self, params_metadata: dict, rets_metadata: dict) -> dict:
        """Build the metadata for the module."""
        self.log.debug("Building structured metadata dictionary...")
        metadata: dict[str, str | list[str]] = {
            "moduleName": str(self.config.name),
            "moduleVersion": str(self.config.version),
            "moduleDisplayLabel": str(self.config.display_label),
            "moduleCategory": str(self.config.category),
            "moduleDescription": str(self.config.description),
            "author": str(self.config.author),
            "inputs": [],
            "outputs": [],
        }
        metadata["inputs"] += self._order_records_by_priority(  # type: ignore
            *self._extract_metadata(params_metadata["args"]["details"])
        )
        metadata["outputs"] += self._order_records_by_priority(  # type: ignore
            *self._extract_metadata(rets_metadata["details"])
        )
        return metadata

    # @pysnooper.snoop()
    def _extract_metadata(self, details: dict) -> list[dict[str, str | list[str]]]:
        """Extract metadata from class annotations."""
        self.log.debug(f"Extracting metadata from details: {details}")
        metadata: list[dict[str, str | list[str]]] = []
        if not details:
            self.log.warning("Details dict empty! No metadata to extract.")
            return metadata
        for detail in details:
            self.log.debug(f"Processing detail: {detail}")
            unpacked = self._unpack_annotated(details[detail]["type"])
            self.log.debug(f"unpacked: {unpacked}")
            type_name = str(unpacked[0])
            self.log.debug(f"type_name: {type_name}")
            record = self._build_record(detail, unpacked, type_name)
            self.log.debug(f"record: {record}")
            metadata.append(record)
        return metadata

    # @pysnooper.snoop()
    def _build_record(self, detail: str, unpacked: tuple, type_name: str) -> dict[str, str | list[str]]:
        """Build a metadata record for a field."""
        self.log.debug("Building metadata record for field...")
        record: dict = {
            "name": detail.strip("_"),
            "label": detail,
            "type": (type_name if type_name.startswith("list") else type_name.split("'")[1]),
            "description": None,
            "validations": [],
        }
        match record["type"]:
            case "KClassifier":
                record["type"] = KClassifier.serialized()
            case "KPredictor":
                print("[ DEBUG ]: Unimplemented")
        for item in unpacked[1]:
            if isinstance(item, KMetadata):
                self._add_metadata_to_record(item, record)
        self.log.debug(f"record: {record}")
        return record

    def _add_metadata_to_record(self, item: KMetadata, record: dict) -> None:
        """Add metadata to the record."""
        self.log.debug(f"Adding metadata item {item} to record...")
        segmented = str(item).split(":")
        self.log.debug(f"segmented: {segmented}")
        if isinstance(item, DisplayName):
            record["label"] = segmented[1]
        elif isinstance(item, DisplayDescription):
            record["description"] = segmented[1]
        elif isinstance(item, KValidation):
            record["validations"].append(str(item))

    @staticmethod
    def _order_records_by_priority(*records: dict[str, str | list[str]]) -> list[dict[str, str | list[str]]]:
        """Order records by their validation priority."""
        ordered: list = []
        leftover: list = []
        to_order: list = []
        priority_queue: list = []

        for record in records:
            position = [
                int(item.split(":")[1]) for item in record.get("validations", []) if item.startswith("position:")
            ]
            if not position:
                leftover.append(record)
                continue
            to_order.append(
                (
                    position[0],
                    record,
                )
            )
        for record in to_order:
            heapq.heappush(priority_queue, record)
        while priority_queue:
            _, record = heapq.heappop(priority_queue)
            ordered.append(record)
        ordered += leftover
        return ordered

    # @pysnooper.snoop()
    def _unpack_annotated(self, annotated_type: type) -> tuple[type, list[str]]:
        """Unpack Annotated types to their base types."""
        self.log.debug("Unpacking annotated types to their base types...")
        if get_origin(annotated_type) is Annotated:
            base_type, *metadata = get_args(annotated_type)
            if get_origin(base_type) is Annotated:
                return self._unpack_annotated(base_type)
            return base_type, metadata
        elif get_origin(annotated_type) is list:
            inner_type = get_args(annotated_type)[0]
            return self._unpack_annotated(inner_type)
        return annotated_type, []

    # @pysnooper.snoop()
    def _get_class_metadata(self, cls: type) -> dict[str, Any]:
        """Recursively fetch the metadata for class attributes with type annotations."""
        self.log.debug("Fetching metadata for class attributes with type annotations...")
        if not hasattr(cls, "__annotations__"):
            return {}
        class_metadata = {}
        for attr_name, attr_type in cls.__annotations__.items():
            class_metadata[attr_name] = {
                "type": attr_type,
                "details": (self._get_class_metadata(attr_type) if inspect.isclass(attr_type) else None),
            }
        self.log.debug(f"class_metadata: {class_metadata}")
        return class_metadata

    @property
    def manifest(self) -> dict:
        """Return the module's metadata."""
        if self._manifest and not self._recompute_manifest:
            return self._manifest
        self._manifest = self._extract_manifest()
        return self._manifest

    @abstractmethod
    def main(self, args: Args) -> Rets:
        pass
