# KayaModuleSDK

# [ KIT ]: Kaya Integration Testing Framework

## Overview
The **Kaya Integration Testing (KIT) Framework** is a lightweight, Python-based framework built on top of `pytest` to automate API integration tests. KIT extracts test method parameters, dynamically determines API endpoints based on test class names, executes HTTP requests via `curl`, and injects the response back into the test function. The framework is designed with low coupling and high cohesion in mind, where each component has a clear, focused responsibility.

## Architecture and Design Principles

### Low Coupling
- **Modular Responsibilities:** Each method in the KIT class handles a distinct task (e.g., precondition checks, constructing HTTP requests, executing shell commands). This minimizes dependencies between different parts of the code.
- **Explicit Interfaces:** The KIT class methods accept parameters and return structured data (e.g., a response dictionary) so that changes in one area (such as shell command execution) have minimal impact on other areas (like response parsing).

### High Cohesion
- **Single Responsibility:** Methods like `check_preconditions()`, `module_request()`, and `shell_cmd()` each encapsulate a single, well-defined behavior.
- **Clear Separation of Concerns:** The KIT framework separates:
  - **Precondition checks:** Verifying that the necessary environment and module dependencies are present.
  - **HTTP request execution:** Building and executing a `curl` command to send requests.
  - **Response processing:** Parsing and packaging the server’s response for use in tests.
  - **Test decoration:** The `request` decorator extracts method parameters and injects the HTTP response into test methods.

## Key Components

### 1. KIT Class Configuration
- **Web Server Settings:**
  - `_webserver_protocol`, `_webserver_host`, `_webserver_port`, and `_webserver_method` are defined as class attributes for easy configuration.
- **Run-Time Execution:**
  - The `run` class method wraps test functions to execute integration tests. It extracts arguments from an `Args` object, checks preconditions, sends a request, processes the response, and passes the results to the test.

### 2. Decorators and Request Handling
- **`@KIT.run` Decorator:**
  - **Responsibility:**
    - Extracts named arguments from the test method.
    - Constructs a JSON payload from these arguments.
    - Dynamically builds the API endpoint URL using the test class name.
    - Executes a `curl` command and processes the response.
    - Injects the response as a `response` keyword argument into the test method.
  - **Design Decisions:**
    - Uses `functools.wraps` to preserve metadata.
    - Keeps the HTTP request logic separated from test assertions.

### 3. Preconditions and Module Validation
- **Precondition Checks:**
  - `check_preconditions()` aggregates general checks (e.g., webserver availability) and module-specific checks (e.g., package installation, module existence).
  - Individual helper methods such as `check_webserver_running()`, `check_package_installed()`, and `check_module_exists()` handle specific validations.
- **Benefits:**
  - The separation of these concerns makes it easier to modify or extend precondition checks without affecting other parts of the system.

### 4. Module Request and Shell Command Execution
- **`module_request()`:**
  - Converts a given request body to JSON.
  - Constructs the curl command with proper headers.
  - Invokes `shell_cmd()` to execute the command and then parses the response.
- **`shell_cmd()`:**
  - Encapsulates the logic to execute a shell command (using `subprocess.Popen`) and return decoded output.
  - Handles user context and ensures proper cleanup of subprocess resources.
- **Cohesion Aspect:**
  - Both methods are focused on the execution and handling of external processes, thereby keeping their functionality isolated from higher-level test logic.

### 5. Utility Methods
- **`_get_method_kwargs()`:**
  - Uses the `inspect` module to extract default keyword arguments from test functions.
  - This supports the dynamic configuration of test parameters without hard-coding them in multiple places.

## Workflow
1. **Pre-Test Phase:**
   - The test method is decorated with `@KIT.run`.
   - When the test method is invoked, the `wrapper()` function extracts any provided keyword arguments.
2. **Request Phase:**
   - The API endpoint URL is constructed based on specified data or on the module Args class name (e.g., `ADDArgs` maps to `/ADD`).
   - A JSON payload is built from the test method’s named parameters.
   - A `curl` command is constructed and executed.
3. **Response Phase:**
   - The output from the curl command is parsed.
   - The parsed JSON (or raw text if JSON parsing fails) along with status information is packaged into a response dictionary.
4. **Injection Phase:**
   - The original test function is called with the response injected as a keyword argument (`response`), along with the original parameters.
5. **Test Assertions:**
   - The test function then performs assertions on both its input parameters and the injected response.

## Error Handling and Exceptions
- **Preconditions:**
  - If preconditions are not met, a `KITFailureException` is raised.
- **Module Not Found:**
  - Specific exceptions such as `ModuleNotFoundException` are raised when expected modules or packages are missing.
- **Shell Command Execution:**
  - The exit code and error output from shell commands are captured and used to determine if an error occurred during the HTTP request.

## Example KIT usage
```python
from kaya_core_modules.module import ADDArgs, ADDRets
from kaya_module_sdk.sdk import setup_kit_framework
KIT = setup_kit_framework(legacy=False)

@KIT.run(
    ADDArgs(first_value=[1], second_value=[2]),
    # NOTE: Optionally, you can specify:
    # package='kaya_core_modules',
    # module='ADD'
)
def test_add_module(result = ADDRets):
    assert result.sum == ['3.0']
```

# [ KVL ]: Kaya Validation Framework

## Overview

The Kaya Integration Testing (KIT/KVL) Framework is a modular, Python‑based testing solution built on top of `pytest`. The framework is designed with low coupling and high cohesion in mind, where each module has a single, focused responsibility:

- **KVL (Harness):**
  Coordinates file and module loading, and delegates validation tasks.

- **KVLE (Executer):**
  Executes various validations including linters (flake8), type checkers (mypy), and module metadata/rule checks.
  It also dynamically loads metadata constraint rules.

- **KVLR (Reporter):**
  Formats, validates, and optionally dumps the aggregated validation results into a JSON report.

## Design Principles

- **Low Coupling:**
  Each component interacts with others via well‑defined interfaces and minimal dependencies. For instance, file loading, module importation, validation execution, and reporting are handled by separate modules.

- **High Cohesion:**
  Each module is focused on a single aspect of the overall process:
  - *KVL (Harness)* is responsible for locating and loading source files and modules.
  - *KVLE (Executer)* handles executing various validation checks.
  - *KVLR (Reporter)* focuses on formatting and outputting test reports.

- **Extensibility:**
  The design makes it straightforward to extend functionality:
  - Adding new validation checks in KVLE.
  - Supporting additional report formats in KVLR.
  - Adjusting file/module search strategies in KVL.

## Modules

### 1. KVL (Harness)
- **Location:** `kaya_module_sdk/src/testing/kvl_harness.py`
- **Responsibilities:**
  - Search for Python files in directories.
  - Load Python files and module packages.
  - Delegate validation actions to KVLE and reporting to KVLR.
- **Key Methods:**
  - `search_python_files_in_dir(dir_path)`: Recursively finds all Python source files.
  - `load_python_files(target_files)`: Reads the content of each file.
  - `load_module_package(module_name)`: Imports and instantiates a module package.
  - `check_rules()`, `check_meta()`, and `check_source()`: Entry points for different validation types.
  - `check(*targets, **kwargs)`: Main entry point that selects and runs one or more validations based on provided targets.

### 2. KVLE (Executer)
- **Location:** `kaya_module_sdk/src/testing/kvl_executer.py`
- **Responsibilities:**
  - Execute various validations (e.g., linting, type-checking, metadata rules).
  - Load constraint rules dynamically from a set of metadata constraint classes.
  - Aggregate validation results for rules, metadata, and source code.
- **Key Methods:**
  - `check_package_installed(test)`: Verifies that the required package is installed.
  - `load_constraint_rules(*rules)`: Loads and validates constraint rules.
  - `check_rules()`: Aggregates rule validation results.
  - `check_meta(module_data, report=True)`: Aggregates metadata validation results.
  - `check_source(loaded_files, report=True)`: Runs source code validations using external tools like flake8 and mypy.

### 3. KVLR (Reporter)
- **Location:** `kaya_module_sdk/src/testing/kvl_reporter.py`
- **Responsibilities:**
  - Format the aggregated validation results from KVLE.
  - Generate a human‑readable report and optionally dump it as a JSON file.
- **Key Methods:**
  - `_check_dump_file_path()`: Validates that the report file’s parent directory exists and is writable.
  - `_check_kvle_results(*results)`: Verifies that results are in a valid format.
  - `_dump_test_results_report_json(formatted_results, file_path)`: Dumps the formatted results to a file.
  - `_format_validation_result(result)`: Formats individual validation result groups.
  - `_format_validation_report(*results)`: Merges and formats multiple result dictionaries.
  - `generate_report(*results, dump=False)`: Main method to produce and optionally dump the final report.

## Usage

### Running Validations

The main entry point for executing validations is through the `KVL` class. A user may create an instance of `KVL`, provide file paths or a module package name, and then invoke one or more of the check methods:
```python
from kaya_module_sdk.src.testing.kvl_harness import KVL

# Example: Validate module rules
kvl = KVL("path/to/source", module_name="dummy_module")
rules_report = kvl.check_rules(module="dummy_module", dump_report=True)

# Example: Validate module metadata
meta_report = kvl.check_meta(module="dummy_module", dump_report=False)

# Example: Validate source code files
source_report = kvl.check_source(file_path="path/to/file.py", dump_report=False)

# Example: Run multiple validations
overall_report = kvl.check("meta", "source", "rules", module="dummy_module", file_path="path/to/file.py", dump_report=True)
# OR
overall_report = kvl.check("all", module="dummy_module", file_path="path/to/file.py", dump_report=True)
```


