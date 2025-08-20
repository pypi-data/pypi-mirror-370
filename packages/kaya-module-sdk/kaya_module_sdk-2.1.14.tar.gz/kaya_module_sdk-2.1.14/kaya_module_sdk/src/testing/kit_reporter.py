import datetime
import json
import os

# import pysnooper  # type: ignore

from logging import Logger, getLogger
from typing import Callable, Any

from kaya_module_sdk.src.exceptions.malformed_results import MalformedResultsException
from kaya_module_sdk.src.exceptions.write_failure import WriteFailureException

log: Logger = getLogger(__name__)


class KITR:
    """[ KIT(R)eporter ]: Responsibilities -

    * Processes and formats results received from KIT(E)
    * Generates JSON report dump file if specified
    """

    report: dict
    context: dict
    dump_file_path: str

    def __init__(self, dump_file: str | None = None, **kwargs: Any) -> None:
        self.report = {}
        self.context = kwargs
        self.dump_file_path = dump_file or "kit.report"

    # @pysnooper.snoop()
    def _check_dump_file_path(self) -> bool:
        directory = os.path.dirname(self.dump_file_path)
        if not directory:
            directory = "."
        # Check if the directory is indeed a directory
        if not os.path.exists(directory) or not os.path.isdir(directory) or not os.access(directory, os.W_OK):
            raise WriteFailureException(
                "KIT(R)eporter dump file {self.dump_file_path} has an unexistent "
                "parent directory or location restricts write permissions."
            )
        return True

    # @pysnooper.snoop()
    def _check_test_result_structure(self, result: dict) -> bool:
        if not len(result["ok"]) and not len(result["nok"]):
            raise MalformedResultsException(f"KIT test execution results are malformed! Details: {result}")
        return True

    # @pysnooper.snoop()
    def check_preconditions(self, *results: dict, dump: bool = False) -> None:
        check_results: dict[str, bool] = {}
        preconditions: dict[str, dict[str, Callable]] = {
            "general": {
                "dump_file_path": self._check_dump_file_path,
            },
            "test_specific": {
                "test_result_structure": self._check_test_result_structure,
            },
        }
        for check in preconditions["general"]:
            if check == "dump_file_path" and not dump:
                continue
            check_results.update({check: preconditions["general"][check]()})
        for result in results:
            for check in preconditions["test_specific"]:
                check_results.update({check: preconditions["test_specific"][check](result)})

    # @pysnooper.snoop()
    @staticmethod
    def _dump_test_results_report_json(formatted_results: dict, file_path: str) -> bool:
        try:
            with open(file_path, "ab") as json_file:
                content = json.dumps(formatted_results, indent=4)
                json_file.write(content.encode("utf-8"))
            print(f"[ INFO ]: KIT(R) test reports dumped to: {file_path}")
        except Exception as e:
            raise WriteFailureException("An error occurred while writing to the file") from e
        return True

    # @pysnooper.snoop()
    @staticmethod
    def _format_test_execution_report(*results: dict[str, Any]) -> dict[str, Any]:
        formatted, nok_flag = {}, False
        for test_result in results:
            if test_result["nok"] and not nok_flag:
                nok_flag = True
            for conclusion in ("ok", "nok"):
                for test_name in test_result[conclusion].keys():
                    formatted.update({test_name: test_result[conclusion][test_name]["definition"]})
                    formatted[test_name].update(
                        {
                            "return": test_result[conclusion][test_name]["result"]["response"],
                            "errors": test_result[conclusion][test_name]["result"]["errors"],
                            "result": test_result[conclusion][test_name]["definition"]["result"] or "NOK",
                        }
                    )
        return {
            "TESTS": formatted,
            "TIMESTAMP": str(datetime.datetime.now()),
            "RESULT": "NOK" if nok_flag else "OK",
        }

    # @pysnooper.snoop()
    def generate_report(self, *results: dict, dump: bool = False) -> dict:
        self.check_preconditions(*results, dump=dump)
        formatted = self._format_test_execution_report(*results)
        if dump:
            self._dump_test_results_report_json(formatted, self.dump_file_path)
        return formatted
