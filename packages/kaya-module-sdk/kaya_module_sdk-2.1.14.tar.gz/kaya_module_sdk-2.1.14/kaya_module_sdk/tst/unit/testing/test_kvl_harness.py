import importlib
import pytest

from kaya_module_sdk.src.testing.kvl_harness import KVL
from kaya_module_sdk.src.exceptions.kvl_failure import KVLFailureException


def test_search_python_files_in_dir(tmp_path):
    """Test: search_python_files_in_dir finds only .py files."""
    d = tmp_path / "subdir"
    d.mkdir()
    file1 = d / "file1.py"
    file1.write_text("print('Hello')")
    file2 = d / "file2.txt"
    file2.write_text("Not Python")
    kvl_instance = KVL(str(d))
    found_files = kvl_instance.search_python_files_in_dir(str(d))
    assert file1.as_posix() in found_files
    assert file2.as_posix() not in found_files


def test_load_python_files(tmp_path):
    """Test: load_python_files reads file content correctly."""
    file_path = tmp_path / "dummy.py"
    content = "print('Test')\nprint('Line2')"
    file_path.write_text(content)
    kvl_instance = KVL(str(file_path))
    loaded = kvl_instance.load_python_files([str(file_path)])
    expected = content.splitlines(keepends=True)
    assert loaded[str(file_path)] == expected


def test_load_module_package(monkeypatch, import_module):
    """Test: load_module_package loads a module package and instantiates strategy module."""
    # NOTE: Patch import_module in the current module's namespace.
    monkeypatch.setattr(importlib, "import_module", import_module)
    kvl_instance = KVL(module_name="dummy_module")
    pkg = kvl_instance.load_module_package("dummy_module")
    assert pkg["name"] == "dummy_module"
    # NOTE: Verify that the instance has a config with name 'dummy'
    assert hasattr(pkg["instance"], "config")
    assert pkg["instance"].config.name == "dummy"


def test_get_executer_and_reporter(dummy_kvle, dummy_kvlr):
    """Test: get_executer and get_reporter return the stored dummy objects."""
    kvl_instance = KVL()
    # NOTE: Initially, executer and reporter should be None.
    assert kvl_instance.executer is None
    assert kvl_instance.reporter is None
    # NOTE: Set them manually.
    kvl_instance.executer = dummy_kvle(dummy="data")
    kvl_instance.reporter = dummy_kvlr(dummy="data")
    exe = kvl_instance.get_executer()
    rep = kvl_instance.get_reporter()
    assert isinstance(exe, dummy_kvle)
    assert isinstance(rep, dummy_kvlr)


def test_check_rules_no_module():
    """Test: check_rules raises exception if module argument is missing."""
    kvl_instance = KVL()
    with pytest.raises(KVLFailureException):
        kvl_instance.check_rules(module=None)


def test_check_rules_success(monkeypatch, import_module, dummy_kvle, dummy_kvlr):
    """Test: check_rules success path."""
    # NOTE: Patch import_module so that load_module_package does not fail.
    monkeypatch.setattr(importlib, "import_module", import_module)
    # NOTE: Create a KVL instance with module_name.
    kvl_instance = KVL(module_name="dummy_module")
    # NOTE: Patch get_executer and get_reporter to return dummy objects.
    monkeypatch.setattr(kvl_instance, "get_executer", lambda **kwargs: dummy_kvle())
    monkeypatch.setattr(kvl_instance, "get_reporter", lambda **kwargs: dummy_kvlr())
    # NOTE: Call check_rules and expect a report with key "report" from dummy_kvlr.
    report = kvl_instance.check_rules(module="dummy_module", dump_report=False)
    assert "report" in report


def test_check_meta_no_module():
    """Test: check_meta raises exception if module argument is missing."""
    kvl_instance = KVL()
    with pytest.raises(KVLFailureException):
        kvl_instance.check_meta(module=None)


def test_check_meta_success(monkeypatch, import_module, dummy_kvle, dummy_kvlr):
    """Test: check_meta success path."""
    monkeypatch.setattr(importlib, "import_module", import_module)
    kvl_instance = KVL(module_name="dummy_module")
    monkeypatch.setattr(kvl_instance, "get_executer", lambda **kwargs: dummy_kvle())
    monkeypatch.setattr(kvl_instance, "get_reporter", lambda **kwargs: dummy_kvlr())
    report = kvl_instance.check_meta(module="dummy_module", dump_report=False)
    assert "report" in report


def test_check_source_success(tmp_path, monkeypatch, dummy_kvle, dummy_kvlr):
    """Test: check_source success path."""
    # NOTE: Create a temporary Python file.
    file_path = tmp_path / "test_source.py"
    file_path.write_text("print('Hello')")
    kvl_instance = KVL(str(file_path))
    # NOTE: Patch search_python_files_in_dir to return our file.
    monkeypatch.setattr(kvl_instance, "search_python_files_in_dir", lambda x: [str(file_path)])
    # NOTE: Let load_python_files work normally. Patch get_executer and get_reporter.
    monkeypatch.setattr(kvl_instance, "get_executer", lambda **kwargs: dummy_kvle())
    monkeypatch.setattr(kvl_instance, "get_reporter", lambda **kwargs: dummy_kvlr())
    report = kvl_instance.check_source(file_path=str(file_path), dump_report=False)
    assert "report" in report


def test_check_combined(monkeypatch, import_module):
    """Test: Combined check method (check) returns all targets."""
    monkeypatch.setattr(importlib, "import_module", import_module)
    kvl_instance = KVL(module_name="dummy_module")
    # NOTE: Patch individual checks.
    monkeypatch.setattr(kvl_instance, "check_meta", lambda **kwargs: {"meta": "ok"})
    monkeypatch.setattr(kvl_instance, "check_source", lambda **kwargs: {"source": "ok"})
    monkeypatch.setattr(kvl_instance, "check_rules", lambda **kwargs: {"rules": "ok"})
    combined = kvl_instance.check("meta", "source", "rules", module="dummy_module")
    assert "meta" in combined
    assert "source" in combined
    assert "rules" in combined
