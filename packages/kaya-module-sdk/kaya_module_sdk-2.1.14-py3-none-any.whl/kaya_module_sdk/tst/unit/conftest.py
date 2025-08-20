import pytest

from typing import Annotated
from types import ModuleType

# from unittest.mock import MagicMock, patch

from kaya_module_sdk.src.module.template import Module, Config
from kaya_module_sdk.src.module.arguments import Args
from kaya_module_sdk.src.module.returns import Rets
from kaya_module_sdk.src.utils.generators.methods import kaya_io
from kaya_module_sdk.src.utils.metadata.abstract_metadata import KMetadata
from kaya_module_sdk.src.utils.metadata.abstract_validation import KValidation

# DUMMY DATA


class DummyResource:
    """Dummy resource classes to simulate importlib.resources behavior."""

    def __init__(self, file_path):
        self.dummy_path = file_path

    def joinpath(self, file_name):
        # For testing we ignore file_name and simply return self.
        return self


class DummyContextManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def __enter__(self):
        return self.file_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class ArgsType(Args):
    key1: str
    key2: str

    def set_key1(self, value):
        pass

    def set_key2(self, value):
        pass


class RetsType(Rets):
    key1: str
    key2: str

    def __init__(self, *args, **kwargs):
        pass


@kaya_io()
class DecoratedArgsType(Args):
    _field1: Annotated[int, "metadata"]
    _field2: Annotated[str, "metadata"]


class DummyConfig(Config):
    def __init__(self, name="dummy", version="1.0"):
        self.name = name
        self.version = version
        self._mandatory = []  # NOTE: For simplicity, no mandatory fields


class TestModule(Module):
    def __init__(self, manifest=None, config=None):
        if manifest:
            self.manifest = manifest
        self.config = config or DummyConfig()
        self.log = self._get_logger(self.__class__, "UnitTest", "0.0.0")
        # mod1 has a valid manifest; mod2 is missing a manifest.
        self.modules = {
            "mod1": DummyModule(
                manifest={
                    "inputs": [{"label": "a", "validations": ["rule1"]}],
                    "outputs": [],
                },
                config=DummyConfig(),
            ),
            "mod2": DummyModule(manifest=None, config=DummyConfig()),
        }

    def __repr__(self):
        return "DummyModule"

    def main(self, args) -> Rets:
        return Rets()  # NOTE: Simulating main method behavior for testing


class DummyModule:
    def __init__(self, manifest, config=None):
        self.manifest = manifest
        self.config = config or DummyConfig()

    def __repr__(self):
        return "DummyModule"


class KMetadataSubclass(KMetadata):
    def __init__(self, data):
        self._data = data

    def get_data(self):
        return self._data

    def __str__(self) -> str:
        return f"KMetadata: {self._data}"


class KValidationSubclass(KValidation):
    def __init__(self, data):
        self._data = data

    def get_data(self):
        return self._data

    def __str__(self) -> str:
        return f"KValidation: {self._data}"


class DummyKVLE:
    """Dummy implementations for KVLE to isolate KVL tests."""

    def __init__(self, **context):
        self.context = context

    def check_rules(self):
        # Return a dummy rules result
        return {"dummy_rule": "passed"}

    def check_meta(self, module_package):
        # Return a dummy metadata result
        return {"dummy_meta": "passed"}

    def check_source(self, python_files):
        # Return a dummy source result
        return {"dummy_source": "passed"}


class DummyKVLR:
    """Dummy implementations for KVLR to isolate KVL tests."""

    def __init__(self, **context):
        self.context = context

    def generate_report(self, data, dump=False):
        return {"report": data}


class DummyKVLEForSuccess:
    def check_source(self, python_files):
        # Return a dummy "success" result.
        # Format: a dict with keys "ok" and "nok".
        file_key = list(python_files.keys())[0] if python_files else "unknown"
        return {"ok": [{"path": file_key, "errors": [], "result": "OK"}], "nok": []}


class DummyKVLRForSuccess:
    def generate_report(self, data, dump=False):
        # Simply wrap the provided data in a dict under "report".
        return {"report": data}


class DummyKVLEWithSourceError:
    def check_source(self, python_files):
        # Return a dummy error structure:
        file_key = list(python_files.keys())[0] if python_files else "unknown"
        return {
            "ok": [],
            "nok": [{"path": file_key, "errors": ["dummy error"], "result": "NOK"}],
        }


class DummyKVLRForErrors:
    def generate_report(self, data, dump=False):
        return {"report": data}


class DummyConstraint:
    """Dummy constraint class for testing load_constraint_rules"""

    def __init__(self, a, b=None):
        self._data = {"dummy": "value"}

    def load(self, rule):
        # NOTE: For testing purposes, we ignore the rule and assume successful load.
        pass


class DummyModuleInstance:
    def __init__(self):
        self.config = DummyConfig()
        # NOTE: mod1 has a valid manifest; mod2 is missing a manifest.
        self.modules = {
            "mod1": DummyModule(
                manifest={
                    "inputs": [{"label": "a", "validations": ["rule1"]}],
                    "outputs": [],
                },
                config=DummyConfig(),
            ),
            "mod2": DummyModule(manifest=None, config=DummyConfig()),
        }


# UTILS


def fake_import_module(name):
    """Fake import_module for module package loading."""
    # NOTE: When KVL.load_module_package calls import_module,
    #   we expect a module with a "KayaStrategyModule" attribute.
    if name == "dummy_module.module":
        dummy_mod = ModuleType("dummy_module.module")

        class DummyStrategyModule:
            def __init__(self):
                self.config = type("Config", (), {"name": "dummy", "version": "1.0"})

        setattr(dummy_mod, "KayaStrategyModule", DummyStrategyModule)
        return dummy_mod
    raise ModuleNotFoundError("Module not found: " + name)


def patch_metadata_classes_kvle(monkeypatch):
    """
    Patch all metadata constraint class names used in KVLE.load_constraint_rules
    to our DummyConstraint.
    """
    # NOTE: Import the module where KVLE is defined.
    import kaya_module_sdk.src.testing.kvl_executer as kvle_mod

    names = [
        "EQ",
        "GT",
        "GTE",
        "LT",
        "LTE",
        "MaxLen",
        "Max",
        "MinLen",
        "Min",
        "ValueRange",
        "EQLen",
        "Const",
        "NotConst",
        "Order",
    ]
    for name in names:
        monkeypatch.setattr(kvle_mod, name, DummyConstraint)


@pytest.fixture
def dummy_resource():
    return DummyResource


@pytest.fixture
def dummy_context_manager():
    return DummyContextManager


@pytest.fixture
def dummy_kvle():
    return DummyKVLE


@pytest.fixture
def dummy_kvlr():
    return DummyKVLR


@pytest.fixture
def dummy_kvle_ok():
    return DummyKVLEForSuccess


@pytest.fixture
def dummy_kvlr_ok():
    return DummyKVLRForSuccess


@pytest.fixture
def dummy_kvle_source_nok():
    return DummyKVLEWithSourceError


@pytest.fixture
def dummy_kvlr_nok():
    return DummyKVLRForErrors


@pytest.fixture
def dummy_config():
    return DummyConfig


@pytest.fixture
def dummy_constraint():
    return DummyConstraint


@pytest.fixture
def patch_meta_kvle():
    return patch_metadata_classes_kvle


@pytest.fixture
def import_module():
    return fake_import_module


@pytest.fixture
def mock_module():
    return TestModule()


@pytest.fixture
def mock_module_instance():
    return DummyModuleInstance()


@pytest.fixture
def kaya_io_decorated_args_type(request):
    instance = DecoratedArgsType()
    instance.set_field1(request.param.get("_field1"))
    instance.set_field2(request.param.get("_field2"))
    return instance


@pytest.fixture
def args_type():
    return ArgsType()


@pytest.fixture
def rets_type_obj():
    return RetsType()


@pytest.fixture
def rets_type_cls():
    return RetsType


@pytest.fixture
def kmetadata_subclass(request):
    instance = KMetadataSubclass(data=request.param.get("_data"))
    return instance


@pytest.fixture
def kvalidation_subclass(request):
    instance = KValidationSubclass(data=request.param.get("_data"))
    return instance


# CODE DUMP
