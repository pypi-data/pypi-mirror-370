# External dependencies
import os
import importlib

# import pysnooper

from logging import Logger, getLogger
from typing import Callable, Any

# Internal dependencies
from kaya_module_sdk.src.exceptions.kvl_failure import KVLFailureException
from kaya_module_sdk.src.testing.kvl_executer import KVLE
from kaya_module_sdk.src.testing.kvl_reporter import KVLR

log: Logger = getLogger(__name__)


class KVL:
    """
    [ KVL(H) ]: Kaya Validation Framework (Harness)

    Coordinates:
      - Locating Python source files.
      - Loading a module package.
      - Delegating validation checks to KVLE.
      - Generating a final report via KVLR.

    Responsibilities are separated as follows:
      • File and module loading.
      • Invoking validations.
      • Maintaining a stable backend interface.
    """

    filename_convention: dict
    module_name: str
    python_files: dict
    module_package: dict
    executer: KVLE | None
    reporter: KVLR | None

    def __init__(self, *file_paths: str, module_name: str = "") -> None:
        self.filename_convention = {"suffix": ".py"}
        self.module_name = module_name
        self.python_files = {fl: [] for fl in file_paths}
        self.module_package = {"name": module_name, "instance": None}
        self.executer = None
        self.reporter = None
        if module_name:
            self.load_module_package(module_name)

    # UTILS

    # @pysnooper.snoop()
    def search_python_files_in_dir(self, dir_path: str) -> list:
        """Recursively finds all Python files in a directory."""
        python_files = []
        for root, _, files in os.walk(dir_path):
            for f in files:
                if f.endswith(self.filename_convention["suffix"]):
                    python_files.append(os.path.join(root, f))
        return python_files

    # @pysnooper.snoop()
    def load_python_files(self, target_files: list[str]) -> dict:
        """Reads each target file and stores its content."""
        log.info("Loading python files...")
        log.debug(f"Target files: {target_files}")
        for file_path in target_files:
            with open(file_path, encoding="utf-8") as fl:
                self.python_files[file_path] = fl.readlines()
        return self.python_files

    # @pysnooper.snoop()
    def load_module_package(self, module_name: str) -> dict:
        """Imports the module package and instantiates the strategy module."""
        log.info(f"Loading module {module_name}...")
        normalized = module_name.replace("-", "_")
        log.debug(f"Normalized module name: {normalized}")
        pkg = importlib.import_module(f"{normalized}.module")
        log.debug(f"Imported module package: {pkg}")
        strategy_class = pkg.KayaStrategyModule
        log.debug(f"Strategy module class: {strategy_class}")
        instance = strategy_class()
        log.debug(f"Strategy module class instance: {instance}")
        self.module_package = {"name": module_name, "instance": instance}
        return self.module_package

    # @pysnooper.snoop()
    def get_executer(self, **kwargs: dict) -> KVLE:
        """Instantiates or returns an existing KVLE instance."""
        if self.executer is None:
            log.info("No KVL(E) instance found! Creating...")
            self.executer = KVLE(**kwargs)
        return self.executer

    # @pysnooper.snoop()
    def get_reporter(self, **kwargs: Any) -> KVLR:
        """Instantiates or returns an existing KVLR instance."""
        if self.reporter is None:
            log.info("No KVL(R) instance found! Creating...")
            self.reporter = KVLR(**kwargs)
        return self.reporter

    # ACTIONS

    # @pysnooper.snoop()
    def check_rules(self, module: str, dump_report: bool = False, **kwargs: dict) -> list:
        """
        Validates module constraint rules.
        Loads the module package, then uses KVLE to check rules and KVLR to format the report.
        """
        log.info(f"Validating module {module} constraint rules...")
        if not module:
            err_msg = "No module package name specified!"
            log.error(err_msg)
            raise KVLFailureException(err_msg)
        if self.module_name and not self.module_package.get("instance"):
            self.load_module_package(self.module_name)
        try:
            results = self.get_executer(**self.__dict__).check_rules()
            log.debug(f"KVL(E) rule results: {results}")
            report = self.get_reporter(**self.__dict__).generate_report({"rules": results}, dump=dump_report)
            log.debug(f"KVL(R) rule report: {report}")
        except Exception as e:
            err_msg = "Module constraints verification failed!"
            log.error(err_msg)
            raise KVLFailureException(err_msg) from e
        return report

    # @pysnooper.snoop()
    def check_meta(self, module: str, dump_report: bool = False, **kwargs: dict) -> list:
        """
        Validates module metadata.
        """
        log.info(f"Validating module {module} metadata...")
        if not module:
            err_msg = "No module package name specified!"
            log.error(err_msg)
            raise KVLFailureException(err_msg)
        if self.module_name and not self.module_package.get("instance"):
            self.load_module_package(self.module_name)
        try:
            results = self.get_executer(**self.__dict__).check_meta(self.module_package)
            log.debug(f"KVL(E) metadata results: {results}")
            report = self.get_reporter(**self.__dict__).generate_report({"meta": results}, dump=dump_report)
            log.debug(f"KVL(R) metadata report: {report}")
        except Exception as e:
            err_msg = "Module metadata verification failed!"
            log.error(err_msg)
            raise KVLFailureException(err_msg) from e
        return report

    # @pysnooper.snoop()
    def check_source(self, file_path: str = "", dump_report: bool = False, **kwargs: dict) -> list:
        """
        Validates source code either from a single file or recursively from a directory.
        """
        log.info(f"Validating source code files from path {file_path}...")
        target = file_path or "."
        files = self.search_python_files_in_dir(target) if os.path.isdir(target) else [target]
        log.info(f"Identified files: {files}")
        self.load_python_files(files)
        try:
            results = self.get_executer(**self.__dict__).check_source(self.python_files)
            log.debug(f"KVL(E) file results: {results}")
            report = self.get_reporter(**self.__dict__).generate_report({"source": results}, dump=dump_report)
            log.debug(f"KVL(E) file report: {report}")
        except Exception as e:
            err_msg = "Source file verification failed!"
            log.error(err_msg)
            raise KVLFailureException(err_msg) from e
        return report

    # @pysnooper.snoop()
    def check(self, *targets: str, **kwargs: dict) -> dict:
        """
        Main entry point to run one or more verifications.
        *targets*: one or more of "meta", "source", "rules", or "all".
        Additional kwargs (e.g. dump_report, module, file_path) are passed to the specific checks.
        """
        actions: dict[str, Callable] = {
            "meta": self.check_meta,
            "source": self.check_source,
            "rules": self.check_rules,
        }
        to_check = list(actions.keys()) if "all" in targets else list(targets)
        log.info(f"Initiating KVL validation of {to_check}...")
        if not to_check:
            log.error("No verification targets specified!")
            return {}
        if self.module_name and not self.module_package.get("instance"):
            self.load_module_package(self.module_name)
        check = {target: actions[target](**kwargs) for target in to_check}
        log.debug(f"Validation results: {check}")
        return check
