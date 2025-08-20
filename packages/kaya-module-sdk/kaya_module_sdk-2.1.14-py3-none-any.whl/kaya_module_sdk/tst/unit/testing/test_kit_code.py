import json
import subprocess
import socket
import pytest
import sys

from types import ModuleType

from kaya_module_sdk.src.exceptions.kit_failure import KITFailureException
from kaya_module_sdk.src.exceptions.module_not_found import ModuleNotFoundException
from kaya_module_sdk.src.testing.kit_code import KIT


def test_get_method_kwargs():
    def dummy_func(a, b="default_b", c=42):
        pass

    kwargs_dict = KIT._get_method_kwargs(dummy_func)
    # NOTE: Expect to see only parameters that have defaults.
    assert kwargs_dict == {"b": "default_b", "c": 42}


def test_shell_cmd_success(monkeypatch):
    # NOTE: Simulate subprocess.Popen with a dummy process.
    class DummyProcess:
        def __init__(self, stdout, stderr, returncode):
            self._stdout = stdout
            self._stderr = stderr
            self.returncode = returncode

        def communicate(self):
            return (self._stdout.encode("utf-8"), self._stderr.encode("utf-8"))

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    def fake_popen(command, shell, stdout, stderr):
        # NOTE: For testing, return fixed outputs.
        return DummyProcess("Get Lost", "", 0)

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    out, err, code = KIT.shell_cmd("echo Hello")
    assert out == "Get Lost"
    assert err == ""
    assert code == 0


def test_module_request_success(monkeypatch):
    # NOTE: Monkeypatch shell_cmd so that it returns controlled output.
    fake_output = '{"foo": "bar"}'

    def fake_shell_cmd(cmd, user=None):
        return (fake_output, "", 0)

    monkeypatch.setattr(KIT, "shell_cmd", fake_shell_cmd)
    response = KIT.module_request("dummy_module", {"param": "value"})
    # Expected: response['response'] is parsed JSON
    assert response["response"] == json.loads(fake_output)
    assert response["exit"] == 0
    assert response["errors"] == []


def test_module_request_failure(monkeypatch):
    # NOTE: Simulate an error response (nonzero exit).
    fake_stdout = ""
    fake_stderr = "Error occurred"

    def fake_shell_cmd(cmd, user=None):
        return (fake_stdout, fake_stderr, 1)

    monkeypatch.setattr(KIT, "shell_cmd", fake_shell_cmd)
    response = KIT.module_request("dummy_module", {"param": "value"})
    # NOTE: On error, the errors list should include the stderr.
    assert response["exit"] == 1
    assert fake_stderr in response["errors"]


def test_check_webserver_running_true(monkeypatch):
    # NOTE: Monkeypatch socket.socket so that connect_ex returns 0.
    class DummySocket:
        def __init__(self, *args, **kwargs):
            pass

        def connect_ex(self, address):
            return 0

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(socket, "socket", lambda *args, **kwargs: DummySocket())
    assert KIT.check_webserver_running() is True


def test_check_webserver_running_false(monkeypatch):
    # NOTE: Simulate a nonzero result.
    class DummySocket:
        def __init__(self, *args, **kwargs):
            pass

        def connect_ex(self, address):
            return 1

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(socket, "socket", lambda *args, **kwargs: DummySocket())
    assert KIT.check_webserver_running() is False


def test_check_package_installed_success(monkeypatch):
    # NOTE: Use a package known to exist or simulate find_spec.
    def fake_find_spec(package):
        return object()  # return dummy spec object

    monkeypatch.setattr("importlib.util.find_spec", fake_find_spec)
    # NOTE: Should return True when no exception is raised.
    assert KIT.check_package_installed("some_package", "some_module") is True


def test_check_package_installed_failure(monkeypatch):
    # NOTE: Define a fake find_spec that always raises ModuleNotFoundError.
    def fake_find_spec(package):
        raise ModuleNotFoundError("not found")

    # NOTE: Get the module where KIT is defined.
    kit_module = sys.modules[KIT.__module__]
    # NOTE: Patch the 'find_spec' in that module.
    monkeypatch.setattr(kit_module, "find_spec", fake_find_spec)
    with pytest.raises(ModuleNotFoundException):
        KIT.check_package_installed("nonexistent_package", "any_module")


def test_check_module_exists_success(monkeypatch):
    # NOTE: Create a dummy module that has an attribute 'TEST'
    dummy_mod = ModuleType("dummy.module")
    setattr(dummy_mod, "TEST", True)

    def fake_import_module(name):
        return dummy_mod

    # NOTE: Get the module in which KIT is defined.
    kit_module = sys.modules[KIT.__module__]
    # NOTE: Patch the import_module function in that module's namespace.
    monkeypatch.setattr(kit_module, "import_module", fake_import_module)
    assert KIT.check_module_exists("dummy", "TEST") is True


def test_check_module_exists_failure(monkeypatch):
    def fake_import_module(name):
        raise ImportError("module not found")

    monkeypatch.setattr("importlib.import_module", fake_import_module)
    assert KIT.check_module_exists("dummy", "TEST") is False


def test_run_decorator_success(monkeypatch, args_type, rets_type_cls):
    # NOTE: Dummy module_request: simulate a response dictionary.
    fake_response = {"response": {"key1": "foo", "key2": "bar"}, "errors": [], "exit": 0}
    monkeypatch.setattr(KIT, "module_request", lambda module, body: fake_response)
    # NOTE: Force precondition check to pass.
    monkeypatch.setattr(KIT, "check_preconditions", lambda package="", module="": True)

    # NOTE: Define a dummy test function to be wrapped.
    def dummy_test(result=rets_type_cls):
        return result

    # NOTE: Wrap the dummy_test function using KIT.run decorator.
    decorated = KIT.run(args_type, package="dummy_pkg", module="dummy_module")(dummy_test)
    # NOTE: Call the decorated function; note: no extra arguments.
    outcome = decorated()
    # NOTE: Expect that the result constructor was called with fake_response['response'].
    assert isinstance(outcome, rets_type_cls)


def test_run_decorator_missing_result(monkeypatch, args_type):
    def dummy_test_no_result(x):
        return x

    # NOTE: Force preconditions to pass.
    monkeypatch.setattr(KIT, "check_preconditions", lambda package="", module="": True)
    # NOTE: Monkeypatch module_request.
    fake_response = {"response": {"key1": "foo", "key2": "var"}, "errors": [], "exit": 0}
    monkeypatch.setattr(KIT, "module_request", lambda module, body: fake_response)
    # NOTE: When running the decorator, it should raise a KITFailureException because 'result' is missing.
    with pytest.raises(KITFailureException):
        decorated = KIT.run(args_type)(dummy_test_no_result)
        decorated()


# CODE DUMP
