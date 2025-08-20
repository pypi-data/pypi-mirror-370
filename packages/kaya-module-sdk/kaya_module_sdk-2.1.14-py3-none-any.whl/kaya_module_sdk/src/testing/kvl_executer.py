# External dependencies
import importlib.util
import mypy.api as mypy_api

# import pysnooper

from logging import Logger, getLogger
from typing import Any
from flake8.api import legacy as flake8

# Internal dependencies
from kaya_module_sdk.src.exceptions.module_not_found import ModuleNotFoundException
from kaya_module_sdk.src.utils.metadata.equal import EQ
from kaya_module_sdk.src.utils.metadata.greater import GT
from kaya_module_sdk.src.utils.metadata.greater_or_equal import GTE
from kaya_module_sdk.src.utils.metadata.less import LT
from kaya_module_sdk.src.utils.metadata.less_or_equal import LTE
from kaya_module_sdk.src.utils.metadata.max_len import MaxLen
from kaya_module_sdk.src.utils.metadata.maximum import Max
from kaya_module_sdk.src.utils.metadata.min_len import MinLen
from kaya_module_sdk.src.utils.metadata.minimum import Min
from kaya_module_sdk.src.utils.metadata.value_range import ValueRange
from kaya_module_sdk.src.utils.metadata.eq_len import EQLen
from kaya_module_sdk.src.utils.metadata.const import Const
from kaya_module_sdk.src.utils.metadata.not_const import NotConst
from kaya_module_sdk.src.utils.metadata.order import Order

log: Logger = getLogger(__name__)

type Check = dict[str, list[dict[str, Any]]]
type Report = dict[str, Check]


class KVLE:
    """
    [ KVL(E) ]: Kaya Validation Framework (Executor)

    Responsibilities:
      - Run linters (flake8), type checkers (mypy) and module validations.
      - Load and apply metadata constraint rules.
      - Aggregate validation results for rules, metadata, and source.
    """

    def __init__(self, **context: Any) -> None:
        self.context = context
        self.check: Report = {
            "rules": {"ok": [], "nok": []},
            "meta": {"ok": [], "nok": []},
            "source": {"ok": [], "nok": []},
        }

    # @pysnooper.snoop()
    def check_package_installed(self, test: dict) -> bool:
        log.info(f'Checking module package {test["package"]} is installed...')
        try:
            importlib.util.find_spec(test["package"])
        except ModuleNotFoundError as e:
            err_msg = f'Package {test["package"]} is not installed!'
            log.error(err_msg)
            raise ModuleNotFoundException(err_msg) from e
        log.info(f'Package {test["package"]} is installed!')
        return True

    # @pysnooper.snoop()
    def load_constraint_rules(self, *rules: str) -> dict:
        log.info("Loading constraing rules...")
        log.debug(f"Rules: {rules}")
        matches = []
        metadata_classes = [
            EQ,
            GT,
            GTE,
            LT,
            LTE,
            MaxLen,
            Max,
            MinLen,
            Min,
            ValueRange,
            EQLen,
            Const,
            NotConst,
            Order,
        ]
        for rule in rules:
            log.debug(f"Processing rule: {rule}")
            for mcls in metadata_classes:
                try:
                    instance = mcls(None, None) if ";" in rule else mcls(None)
                    instance.load(rule)
                    log.debug(f"Instance: {instance}")
                except Exception:
                    continue
                matches.append(instance)
        # NOTE: Only include those with complete data.
        formatted = {item.__class__.__name__: item for item in matches if None not in item._data.values()}
        log.debug(f"Formatted metadata classes: {formatted}")
        return formatted if rules and formatted else {}

    # @pysnooper.snoop()
    def check_rules(self) -> dict:
        """Runs constraint rules checks on module inputs/outputs and aggregates results."""
        log.info("Running constraint rule check on module inputs and outputs...")
        package_instance = self.context.get("module_package", {}).get("instance")
        log.debug(f"Package Instance: {package_instance}")
        package_name = package_instance.config.name
        log.debug(f"Package Name: {package_name}")
        submodules = package_instance.modules
        log.debug(f"Submodules: {submodules}")
        rules_report: dict = {"ok": [], "nok": []}
        for module_name, module_obj in submodules.items():
            log.debug(f"Processing module {module_name}...")
            error_flag = False
            module_record = {
                "package": package_name,
                "module": module_name,
                "functions": {"main": []},
            }
            # NOTE: Process manifest validations
            manifest = module_obj.manifest
            log.debug(f"Manifest: {manifest}")
            if not manifest:
                log.error("Could not extract manifest!")
                error_flag = True
                module_record["manifest"] = {"required": True, "set": False}
                module_record["error"] = error_flag
                rules_report["nok"].append(module_record)
                continue
            if not isinstance(manifest, dict) or not manifest.get("inputs"):
                log.error("Invalid manifest detected!")
                error_flag = True
                module_record["manifest"] = {
                    "required": True,
                    "set": True,
                    "valid": False,
                    "value": manifest,
                }
                module_record["error"] = error_flag
                rules_report["nok"].append(module_record)
                continue
            # NOTE: Process input validations.
            for arg in manifest["inputs"]:
                log.info(f"Processing module input argument {arg}...")
                if not arg.get("validations"):
                    log.warning(f"Input argument {arg} has no validation tags specified! Skipping.")
                    continue
                loaded = self.load_constraint_rules(*arg["validations"])
                log.debug(f"Loaded constraint rules: {loaded}")
                if arg["validations"] and not loaded:
                    error_flag = True
                for cname in loaded:
                    values = list(loaded[cname]._data.values())
                    if len(values) == 1:
                        values = values[0]
                    module_record["functions"]["main"].append(
                        {
                            "name": cname,
                            "target": "inputs",
                            "verb": cname.lower(),
                            "field": arg["label"],
                            "rule": [cname, values],
                            "error": error_flag,
                        }
                    )
            # NOTE: Process output validations.
            for ret in manifest["outputs"]:
                log.info(f"Processing module return value {ret}...")
                if not ret.get("validations"):
                    log.warning(f"Return value {ret} has no validation tags specified! Skipping.")
                    continue
                loaded = self.load_constraint_rules(*ret["validations"])
                log.debug(f"Loaded constraint rules: {loaded}")
                if ret["validations"] and not loaded:
                    error_flag = True
                for cname in loaded:
                    values = list(loaded[cname]._data.values())
                    if len(values) == 1:
                        values = values[0]
                    module_record["functions"]["main"].append(
                        {
                            "name": cname,
                            "target": "outputs",
                            "verb": cname.lower(),
                            "field": ret["label"],
                            "rule": [cname, values],
                            "error": error_flag,
                        }
                    )
            module_record["error"] = error_flag
            if error_flag:
                log.error(f"Module {module_name} constraint rule validation failed! Details: {module_record}")
                rules_report["nok"].append(module_record)
            else:
                log.info(f"Module {module_name} constraint rule validation passed!")
                rules_report["ok"].append(module_record)
        self.check["rules"] = rules_report
        return self.check["rules"]

    # @pysnooper.snoop()
    def check_meta(self, module_data: dict, report: bool = True, **kwargs: Any) -> dict:
        """Runs metadata validations and aggregates results."""
        log.info("Running metadata tag validations...")
        package_instance = self.context.get("module_package", {}).get("instance")
        log.debug(f"Package instance: {package_instance}")
        package_name = package_instance.config.name
        log.debug(f"Package name: {package_name}")
        package_version = package_instance.config.version
        log.debug(f"Package version: {package_version}")
        submodules = package_instance.modules
        log.debug(f"Submodules: {submodules}")
        meta_report: Check = {"ok": [], "nok": []}
        for module_name, module_obj in submodules.items():
            log.debug("Processing module {module_name}...")
            error_flag = False
            module_record = {
                "package": package_name,
                "package_version": package_version,
                "module": module_name,
            }
            if not module_obj.config:
                log.error(f"No module config found for {module_name}! Details: {module_obj}")
                error_flag = True
                module_record["config"] = {"required": True, "set": False}
            for key in module_obj.config._mandatory:
                log.debug(f"Processing mandatory key: {key}")
                value = module_obj.config.__dict__.get(key)
                log.debug(f"Key value: {value}")
                if not value:
                    log.error(f"Mandatory key {key} value not set! Details: {value}")
                    error_flag = True
                    module_record[key] = {"required": True, "set": False}
                    continue
                valid = (type(value) in (str,)) if key != "version" else (type(value) in (str, float))
                log.debug(f"Value valid: {valid}")
                module_record[key] = {
                    "required": True,
                    "set": True,
                    "valid": valid,
                    "value": value,
                }
            manifest = module_obj.manifest
            log.debug(f"Module manifest: {manifest}")
            if not manifest:
                log.error(f"Could not fetch module {module_name} manifest! Details: {manifest}")
                error_flag = True
                module_record["manifest"] = {
                    "required": True,
                    "set": False,
                    "valid": False,
                    "value": manifest,
                }
            elif not isinstance(manifest, dict):
                log.error(f"Invalid module {module_name} manifest data type: Details: {manifest}")
                error_flag = True
                module_record["manifest"] = {
                    "required": True,
                    "set": True,
                    "valid": False,
                    "value": manifest,
                }
            if error_flag:
                log.error(f"Module {module_name} metadata tag validation failed! Details: {module_record}")
                meta_report["nok"].append(module_record)
            else:
                log.info(f"Module {module_name} metadata tag validation passed!")
                meta_report["ok"].append(module_record)
        self.check["meta"] = meta_report
        return self.check["meta"]

    # @pysnooper.snoop()
    def check_source(self, loaded_files: dict) -> dict:
        """Runs source code validations (flake8, mypy) and aggregates results."""
        log.info("Running source code file validations...")
        log.debug(f"Loaded files: {loaded_files}")
        source_report: dict = {"ok": [], "nok": []}
        for file_path, _ in loaded_files.items():
            log.info(f"Processing file path: {file_path}")
            errors: list = []
            style_guide = flake8.get_style_guide()
            log.debug(f"Flake8 style guide: {style_guide}")
            flake8_report = style_guide.check_files([file_path])
            log.debug(f"Flake8 report: {flake8_report}")
            if flake8_report.total_errors > 0:
                log.error(f"Flake8 identified {flake8_report.total_errors} errors!")
                flake8_output = [
                    {
                        error[0]: [error[1], error[2]]
                        for error in flake8_report._application.file_checker_manager.results
                    }
                ]
                log.debug(f"Flake8 output: {flake8_output}")
                errors.append({"tool": "flake8", "output": flake8_output})
            mypy_result = mypy_api.run([file_path])
            log.debug(f"MyPy result: {mypy_result}")
            mypy_stdout, mypy_stderr, mypy_exit_status = mypy_result
            if mypy_stderr or mypy_exit_status:
                log.error(f"MyPy errors identified! Details: RC - {mypy_exit_status}, STDERR - {mypy_stderr}")
                errors.append(
                    {
                        "tool": "mypy",
                        "output": mypy_stdout + mypy_stderr,
                        "exit": mypy_exit_status,
                    }
                )
            if errors:
                log.error(f"File {file_path} source code validation failed! Details: {errors}")
                source_report["nok"].append({"path": file_path, "errors": errors, "result": "NOK"})
            else:
                log.info(f"File {file_path} source code validation passed!")
                source_report["ok"].append({"path": file_path, "errors": [], "result": "OK"})
        self.check["source"] = source_report
        return self.check["source"]
