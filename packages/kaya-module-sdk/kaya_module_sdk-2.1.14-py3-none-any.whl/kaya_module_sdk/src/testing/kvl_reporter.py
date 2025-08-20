# External dependencies
import json
import os

# import pysnooper

from logging import getLogger, Logger
from typing import Any

# Internal dependencies
from kaya_module_sdk.src.exceptions.malformed_results import MalformedResultsException
from kaya_module_sdk.src.exceptions.write_failure import WriteFailureException

log: Logger = getLogger(__name__)


class KVLR:
    """
    [ KVL(R) ]: Kaya Validation Framewor (Reporter)

    Responsibilities:
      - Process and format the validation results produced by KVLE.
      - Generate a JSON report and optionally dump it to a file.
    """

    report: dict
    context: dict
    dump_file_path: str

    def __init__(self, dump_file: str | None = None, **kwargs: dict) -> None:
        self.report = {}
        self.context = kwargs
        self.dump_file_path = dump_file or "kvl.report"

    # @pysnooper.snoop()
    def _check_dump_file_path(self) -> bool:
        directory = os.path.dirname(self.dump_file_path) or "."
        if not (os.path.exists(directory) and os.path.isdir(directory) and os.access(directory, os.W_OK)):
            raise WriteFailureException(
                f"KVL(R)eporter dump file {self.dump_file_path} has an unexistent "
                "parent directory or lacks write permissions."
            )
        return True

    # @pysnooper.snoop()
    def _check_kvle_results(self, *results: Any) -> bool:
        if not results:
            raise MalformedResultsException("KVL(R)eporter received malformed results to process!")
        for result in results:
            if not any(key in result for key in ("source", "meta", "rules")):
                raise MalformedResultsException("KVL(R)eporter received malformed results to process!")
        return True

    # @pysnooper.snoop()
    def check_preconditions(self, *results: dict, dump: bool = False) -> bool:
        if dump:
            self._check_dump_file_path()
        self._check_kvle_results(*results)
        return True

    # @pysnooper.snoop()
    def _dump_test_results_report_json(self, formatted_results: list, file_path: str) -> bool:
        try:
            with open(file_path, "a") as json_file:
                json.dump(formatted_results, json_file, indent=4)
            log.info(f"KVL(R) test reports dumped to: {file_path}")
        except (IOError, TypeError) as e:
            raise WriteFailureException("An error occurred while writing the report file") from e
        return True

    # @pysnooper.snoop()
    def _format_validation_result(self, result: dict) -> list:
        builder = []
        for key, value in result.items():
            if key not in ("source", "rules", "meta"):
                continue
            if key == "source":
                builder.append(
                    {
                        "Source File Check": {
                            "FILES": value["ok"] + value["nok"],
                            "RESULT": "NOK" if value["nok"] else "OK",
                        }
                    }
                )
            elif key == "meta":
                builder.append(
                    {
                        "Module Metadata Check": {
                            "MODULES": value["ok"] + value["nok"],
                            "RESULT": "NOK" if value["nok"] else "OK",
                        }
                    }
                )
            elif key == "rules":
                builder.append(
                    {
                        "Module Constraint Rules Check": {
                            "MODULES": value["ok"] + value["nok"],
                            "RESULT": "NOK" if value["nok"] else "OK",
                        }
                    }
                )
        return builder

    # @pysnooper.snoop()
    def _format_validation_report(self, *results: dict) -> list:
        builder = []
        for result in results:
            builder.extend(self._format_validation_result(result))
        return builder

    # @pysnooper.snoop()
    def generate_report(self, *results: dict, dump: bool = False) -> list:
        self.check_preconditions(*results, dump=dump)
        formatted = self._format_validation_report(*results)
        if dump:
            self._dump_test_results_report_json(formatted, self.dump_file_path)
        return formatted
