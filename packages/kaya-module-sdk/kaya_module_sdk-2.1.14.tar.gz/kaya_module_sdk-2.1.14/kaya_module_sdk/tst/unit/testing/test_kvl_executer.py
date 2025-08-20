# External dependencies
import importlib
import pytest

# Internal dependencies
from kaya_module_sdk.src.exceptions.module_not_found import ModuleNotFoundException
from kaya_module_sdk.src.testing.kvl_harness import KVL
from kaya_module_sdk.src.testing.kvl_executer import KVLE


def test_check_package_installed_success(monkeypatch):
    # NOTE: Simulate a successful find_spec call.
    def fake_find_spec(package):
        return object()

    import importlib.util

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)
    kvle = KVLE()
    assert kvle.check_package_installed({"package": "dummy_pkg"}) is True


def test_check_package_installed_failure(monkeypatch):
    # NOTE: Simulate failure by raising ModuleNotFoundError.
    def fake_find_spec(package):
        raise ModuleNotFoundError("not found")

    import importlib.util

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)
    kvle = KVLE()
    with pytest.raises(ModuleNotFoundException):
        kvle.check_package_installed({"package": "dummy_pkg"})


def test_load_constraint_rules(monkeypatch, patch_meta_kvle):
    patch_meta_kvle(monkeypatch)
    kvle = KVLE()
    # NOTE: Call load_constraint_rules with a test rule.
    result = kvle.load_constraint_rules("rule1")
    # NOTE: Expect that DummyConstraint was used to load the rule.
    assert "DummyConstraint" in result
    assert result["DummyConstraint"]._data["dummy"] == "value"


def test_check_rules(monkeypatch, mock_module_instance, dummy_constraint):
    context = {"module_package": {"instance": mock_module_instance}}
    kvle = KVLE(**context)

    # NOTE: Patch load_constraint_rules to simulate a successful constraint load.
    def fake_load_constraint_rules(*rules):
        if "rule1" in rules:
            dummy = dummy_constraint(None)
            return {"DummyConstraint": dummy}
        return {}

    monkeypatch.setattr(kvle, "load_constraint_rules", fake_load_constraint_rules)
    result = kvle.check_rules()
    # NOTE: Expect a dict with keys "ok" and "nok"
    assert "ok" in result
    assert "nok" in result
    # NOTE: Since mod2 has manifest=None, it should appear in "nok".
    nok = result["nok"]
    assert any(mod["module"] == "mod2" for mod in nok)


def test_check_meta(monkeypatch, mock_module_instance):
    context = {"module_package": {"instance": mock_module_instance}}
    kvle = KVLE(**context)
    result = kvle.check_meta(module_data={})
    assert "ok" in result
    assert "nok" in result
    nok = result["nok"]
    ok = result["ok"]
    # NOTE: mod2 (missing manifest) should be in nok.
    assert any(mod["module"] == "mod2" for mod in nok)
    # NOTE: mod1 should be valid and appear in ok.
    assert any(mod["module"] == "mod1" for mod in ok)


def test_check_source_success(tmp_path, monkeypatch, dummy_kvle, dummy_kvlr):
    # Create a temporary Python file.
    file_path = tmp_path / "test_source.py"
    content = "print('Hello')"
    file_path.write_text(content)
    # NOTE: Loaded files dictionary (expected format by check_source).
    #   loaded_files = {str(file_path): content.splitlines(keepends=True)}
    kvl_instance = KVL(str(file_path))
    # NOTE: Patch the method search_python_files_in_dir on the KVL instance
    monkeypatch.setattr(kvl_instance, "search_python_files_in_dir", lambda x: [str(file_path)])
    # NOTE: Let load_python_files work normally
    #   Patch get_executer and get_reporter to return dummy objects.
    monkeypatch.setattr(kvl_instance, "get_executer", lambda **kwargs: dummy_kvle())
    monkeypatch.setattr(kvl_instance, "get_reporter", lambda **kwargs: dummy_kvlr())
    report = kvl_instance.check_source(file_path=str(file_path), dump_report=False)
    # NOTE: Dummy reporter wraps the data under key "report"
    assert "report" in report


def test_check_source_errors(tmp_path, monkeypatch, dummy_kvlr_nok, dummy_kvle_source_nok):
    """
    Test that check_source returns a report with errors when simulated errors occur.
    We simulate errors by patching get_executer to return a dummy error result and
    by patching flake8 and mypy to simulate failures.
    """
    file_path = tmp_path / "test_source.py"
    content = "print('Hello')"
    file_path.write_text(content)
    kvl_instance = KVL(str(file_path))
    # NOTE: Patch search_python_files_in_dir on the KVL instance.
    monkeypatch.setattr(kvl_instance, "search_python_files_in_dir", lambda target: [str(file_path)])
    # NOTE: Patch get_executer and get_reporter to return dummy objects that simulate errors.
    monkeypatch.setattr(kvl_instance, "get_executer", lambda **kwargs: dummy_kvle_source_nok())
    monkeypatch.setattr(kvl_instance, "get_reporter", lambda **kwargs: dummy_kvlr_nok())

    # NOTE: Patch flake8 to simulate errors.
    class DummyFlake8Report:
        total_errors = 5
        _application = type(
            "DummyApp",
            (),
            {"file_checker_manager": type("DummyFcm", (), {"results": [("file", 1, 2)]})},
        )()

    dummy_style_guide = type("DummyStyleGuide", (), {"check_files": lambda self, files: DummyFlake8Report()})()
    monkeypatch.setattr("flake8.api.legacy.get_style_guide", lambda: dummy_style_guide())
    # NOTE: Patch mypy to simulate errors.
    monkeypatch.setattr("mypy.api.run", lambda files: ("mypy error", "mypy stderr", 1))
    report = kvl_instance.check_source(file_path=str(file_path), dump_report=False)
    # NOTE: The DummyKVLRForErrors wraps the KVLE result in a dict under "report".
    rep = report.get("report")
    assert rep is not None
    # NOTE: Dummy executer returns a dict with a non-empty "nok" list.
    #   We assume the structure is: { "source": { "ok": [...], "nok": [...] } }
    if "source" in rep:
        nok_list = rep["source"].get("nok", [])
    else:
        nok_list = rep.get("nok", [])
    assert len(nok_list) > 0


def test_check_combined(monkeypatch, import_module):
    monkeypatch.setattr(importlib, "import_module", import_module)
    kvl_instance = KVL(module_name="dummy_module")
    # NOTE: Patch individual check methods to return dummy reports.
    monkeypatch.setattr(kvl_instance, "check_meta", lambda **kwargs: {"meta": "ok"})
    monkeypatch.setattr(kvl_instance, "check_source", lambda **kwargs: {"source": "ok"})
    monkeypatch.setattr(kvl_instance, "check_rules", lambda **kwargs: {"rules": "ok"})
    # NOTE: Call the combined check method explicitly
    combined = kvl_instance.check("meta", "source", "rules", module="dummy_module")
    # NOTE: Expect a dictionary with keys for each target.
    assert "meta" in combined
    assert "source" in combined
    assert "rules" in combined
    # NOTE: Call the combined check method implicitly
    combined = kvl_instance.check("all", module="dummy_module")
    assert "meta" in combined
    assert "source" in combined
    assert "rules" in combined


# CODE DUMP
