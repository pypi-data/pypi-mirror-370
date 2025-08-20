import os
import json
import pytest

from kaya_module_sdk.src.exceptions.malformed_results import MalformedResultsException
from kaya_module_sdk.src.exceptions.write_failure import WriteFailureException
from kaya_module_sdk.src.testing.kvl_reporter import KVLR


def test_check_dump_file_path_success(tmp_path):
    """
    Test that _check_dump_file_path returns True when the dump file's
    parent directory exists, is a directory, and is writable.
    """
    dump_file = tmp_path / "report.json"
    kvlr_instance = KVLR(dump_file=str(dump_file))
    # NOTE: Since tmp_path is writable, _check_dump_file_path should return True.
    assert kvlr_instance._check_dump_file_path() is True


def test_check_dump_file_path_failure(monkeypatch, tmp_path):
    """
    Test that _check_dump_file_path raises WriteFailureException when
    the parent directory does not exist or is not writable.
    We simulate this by monkeypatching os.path.exists and os.access.
    """
    dump_file = str(tmp_path / "nonexistent_dir" / "report.json")
    kvlr_instance = KVLR(dump_file=dump_file)
    # NOTE: Patch os.path.exists to always return False.
    monkeypatch.setattr(os.path, "exists", lambda path: False)
    with pytest.raises(WriteFailureException):
        kvlr_instance._check_dump_file_path()


def test_check_kvle_results_success():
    """
    Test that _check_kvle_results returns True when provided with at least one
    result dictionary that contains one of the keys: "source", "meta", or "rules".
    """
    kvlr_instance = KVLR()
    valid_result = {"source": {"ok": ["file1.py"], "nok": []}}
    assert kvlr_instance._check_kvle_results(valid_result) is True


def test_check_kvle_results_failure_empty():
    """
    Test that _check_kvle_results raises MalformedResultsException when no results are provided.
    """
    kvlr_instance = KVLR()
    with pytest.raises(MalformedResultsException):
        kvlr_instance._check_kvle_results()


def test_check_kvle_results_failure_invalid():
    """
    Test that _check_kvle_results raises MalformedResultsException when the provided result
    dictionary does not contain any of the required keys.
    """
    kvlr_instance = KVLR()
    invalid_result = {"other": {}}
    with pytest.raises(MalformedResultsException):
        kvlr_instance._check_kvle_results(invalid_result)


def test_dump_test_results_report_json_success(tmp_path):
    """
    Test that _dump_test_results_report_json writes a valid JSON report to the file.
    """
    dump_file = tmp_path / "report.json"
    kvlr_instance = KVLR(dump_file=str(dump_file))
    formatted_results = [{"Source File Check": {"FILES": ["a.py"], "RESULT": "OK"}}]
    # NOTE: should return True.
    assert kvlr_instance._dump_test_results_report_json(formatted_results, str(dump_file)) is True
    # NOTE: Read back the file contents.
    with open(str(dump_file), "r", encoding="utf-8") as f:
        content = json.load(f)
    assert content == formatted_results


def test_dump_test_results_report_json_failure(monkeypatch):
    """
    Test that _dump_test_results_report_json raises WriteFailureException if writing fails.
    We simulate a failure by monkeypatching open to always raise an IOError.
    """
    kvlr_instance = KVLR(dump_file="dummy_report.json")
    formatted_results = [{"Source File Check": {"FILES": ["a.py"], "RESULT": "OK"}}]

    def fake_open(*args, **kwargs):
        raise IOError("Cannot open file")

    monkeypatch.setattr("builtins.open", fake_open)
    with pytest.raises(WriteFailureException):
        kvlr_instance._dump_test_results_report_json(formatted_results, "dummy_report.json")


def test_format_validation_result_source():
    """
    Test that _format_validation_result correctly formats a result dictionary
    for the "source" key.
    """
    kvlr_instance = KVLR()
    result = {"source": {"ok": ["file1.py"], "nok": []}}
    formatted = kvlr_instance._format_validation_result(result)
    # NOTE: Expect a list containing one dictionary with key "Source File Check".
    assert any("Source File Check" in item for item in formatted)


def test_format_validation_result_meta():
    """
    Test formatting for the "meta" key.
    """
    kvlr_instance = KVLR()
    result = {"meta": {"ok": ["module1"], "nok": ["module2"]}}
    formatted = kvlr_instance._format_validation_result(result)
    assert any("Module Metadata Check" in item for item in formatted)


def test_format_validation_result_rules():
    """
    Test formatting for the "rules" key.
    """
    kvlr_instance = KVLR()
    result = {"rules": {"ok": ["rule1"], "nok": []}}
    formatted = kvlr_instance._format_validation_result(result)
    assert any("Module Constraint Rules Check" in item for item in formatted)


def test_format_validation_report():
    """
    Test that _format_validation_report aggregates results from multiple dictionaries.
    """
    kvlr_instance = KVLR()
    result1 = {"source": {"ok": ["file1.py"], "nok": []}}
    result2 = {"meta": {"ok": ["module1"], "nok": []}}
    aggregated = kvlr_instance._format_validation_report(result1, result2)
    # NOTE: Expect the aggregated list to contain entries for both "source" and "meta".
    keys = [list(item.keys())[0] for item in aggregated]
    assert "Source File Check" in keys
    assert "Module Metadata Check" in keys


def test_generate_report_no_dump(monkeypatch):
    """
    Test that generate_report returns a formatted report without dumping to file.
    """
    kvlr_instance = KVLR()
    monkeypatch.setattr(kvlr_instance, "check_preconditions", lambda *results, dump=False: True)
    monkeypatch.setattr(
        kvlr_instance,
        "_format_validation_report",
        lambda *results: [{"dummy": "result"}],
    )
    report = kvlr_instance.generate_report({"source": {"ok": ["file1.py"], "nok": []}}, dump=False)
    # NOTE: The returned report should be the dummy formatted result.
    assert report == [{"dummy": "result"}]


def test_generate_report_with_dump(tmp_path, monkeypatch):
    """
    Test that generate_report dumps the report to a file when dump=True.
    """
    dump_file = tmp_path / "report.json"
    kvlr_instance = KVLR(dump_file=str(dump_file))
    monkeypatch.setattr(kvlr_instance, "check_preconditions", lambda *results, dump=False: True)
    dummy_formatted = [{"dummy": "result"}]
    monkeypatch.setattr(kvlr_instance, "_format_validation_report", lambda *results: dummy_formatted)
    report = kvlr_instance.generate_report({"rules": {"ok": ["rule1"], "nok": []}}, dump=True)
    # NOTE: Check that the file was created and contains the dummy report.
    with open(str(dump_file), "r", encoding="utf-8") as f:
        file_content = json.load(f)
    assert file_content == dummy_formatted
    assert report == dummy_formatted
