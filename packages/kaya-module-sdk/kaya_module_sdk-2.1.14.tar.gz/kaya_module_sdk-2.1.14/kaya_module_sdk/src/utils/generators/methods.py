# import pysnooper

from logging import Logger, getLogger
from functools import partial
from typing import get_type_hints, get_origin, Annotated, get_args, Callable, Type, Any

from kaya_module_sdk.src.utils.metadata.variadic import Variadic
from kaya_module_sdk.src.utils.check import is_matrix
from kaya_module_sdk.src.datatypes.classifier import KClassifier

log: Logger = getLogger(__name__)


# @pysnooper.snoop()
def kaya_io() -> Callable:
    def wrapper(cls: type) -> type:
        log.info(f"Module IO code generator triggered for ({cls})...")
        annotations = get_type_hints(cls, include_extras=True)
        log.debug(f"Fetched annotations: {annotations}")
        parameter_lines, body_lines = build_class_structure(cls, annotations)
        attach_init_method(cls, parameter_lines, body_lines)
        log.info("Dynamic module code generation complete!")
        return cls

    return wrapper


# @pysnooper.snoop()
def build_class_structure(cls: type, annotations: dict[str, Any]) -> tuple[list[str], list[str]]:
    """
    Build the list of parameters and the initialization body for the class.
    """
    log.info("Building the __init__ signature and method body...")
    parameter_lines = []
    body_lines = []
    for field_name, field_type in annotations.items():
        log.debug(f"Processing field name ({field_name}) of type ({field_type})...")
        # NOTE: Process fields with Annotated types only
        field_type_origin = get_origin(field_type)
        if field_type_origin is not Annotated:
            log.warning(f"Field type ({field_type}) is not annotated! Skipping. Details: {field_type_origin}")
            continue
        if field_name in ["_results"]:  # "_errors",
            log.debug(f"Dismissing default field_name ({field_name}).")
            continue
        base_type = get_args(field_type)[0]
        metadata = get_args(field_type)[1:]
        variadic = next((meta for meta in metadata if isinstance(meta, Variadic)), None)
        log.debug(f"Base type detection: ({base_type})")
        log.debug(f"Fetched metadata: ({metadata})")
        log.debug(f"Variadic detection: ({variadic})")
        if variadic or is_matrix(base_type):
            log.debug("Only 2D matrix currently supported!")
            # NOTE: Supports 2D matrix only for variadic input fields
            base_type = get_args(get_args(get_args(field_type)[0])[0])[0]
            log.debug("Base type recompute: ({base_type})")
        add_getter_and_setter(cls, field_name, base_type)
        # optional_type = Union[base_type, None]  # Optional[type]
        parameter_lines.append(build_parameter(field_name, base_type))
        body_lines.append(build_body_line(field_name))
    log.debug("Generated the following class structure:")
    log.debug(f"parameter_lines - {parameter_lines}")
    log.debug(f"body_lines - {body_lines}")
    return parameter_lines, body_lines


# @pysnooper.snoop()
def add_getter_and_setter(cls: Type[Any], field_name: str, base_type: Type) -> None:
    """
    Dynamically create and attach getter and setter methods for a given field.
    """
    log.info("Attaching getter and setter functions for field ({field_name}) of type ({base_type})...")
    getter_func = partial(create_getter, field_name=field_name)
    setter_func = partial(create_setter, field_name=field_name)
    setattr(cls, field_name.lstrip("_"), getter_func())
    log.debug("Successfully attached getter function!")
    setattr(cls, f'set_{field_name.lstrip("_")}', setter_func())
    log.debug("Successfully attached setter function!")


# @pysnooper.snoop()
def build_parameter(field_name: str, base_type: Type[Any]) -> str:
    """
    Build a string representation of a parameter for the dynamic __init__ method.
    """
    log.info("Generating string representation for field name parameter for dynamic __init__ method...")
    parameter = f"{field_name.strip('_')}: {base_type.__name__} | None = None"
    log.debug(f"__init__ method parameter: {parameter}")
    return parameter


# @pysnooper.snoop()
def build_body_line(field_name: str) -> str:
    """
    Build a line of code for the __init__ method body to set instance attributes.
    """
    log.info("Generating __init__ method body code...")
    body_line = f"if {field_name.strip('_')} is not None: self.set_{field_name.strip('_')}({field_name.strip('_')})"
    log.debug(f"__init__ method body line: {body_line}")
    return body_line


# @pysnooper.snoop()
def attach_init_method(cls: Type, parameter_lines: list[str], body_lines: list[str]) -> None:
    """
    Dynamically create and attach the __init__ method to the class.
    """
    log.info("Generating and attaching the dynamic __init__ method...")
    init_code = f"""def __init__(self, {', '.join(parameter_lines)}):\n\
        super(type(self), self).__init__()\n\
        {'\n        '.join(body_lines)}"""
    log.debug(f"__init__ code: {init_code}")
    namespace: dict = {}
    constructor: str = "__init__"
    exec(init_code, globals(), namespace)
    setattr(cls, constructor, namespace[constructor])


# NOTE: Placeholder functions for getter and setter creation
# @pysnooper.snoop()
def create_getter(field_name: str) -> Callable:
    log.info("Creating getter function...")

    @property  # type: ignore
    def getter(self: Type) -> Any:
        return getattr(self, field_name, None)

    log.debug(f"getter function: {getter}")
    return getter


# @pysnooper.snoop()
def create_setter(field_name: str) -> Callable:
    log.info("Creating setter function...")

    def setter(self: Type, value: Any) -> None:
        setattr(self, field_name, value)

    log.debug(f"setter function: {setter}")
    return setter


# CODE DUMP
