from kaya_module_sdk.src.module.config import KConfig


def test_initialization_with_default_values():
    """Test Initialization with default values"""
    config = KConfig(name="Test", version="1.0", category="Category", author="Author")
    # NOTE: Assert default initialization
    assert config.name == "Test"
    assert config.version == "1.0"
    assert config.category == "Category"
    assert config.author == "Author"
    assert config.display_label == ""
    assert config.description == ""
    assert config.author_email == ""
    assert config.MANIFEST == {
        "PACKAGE": {
            "NAME": "Test",
            "LABEL": "",
            "VERSION": "1.0",
            "DESCRIPTION": "",
            "CATEGORY": "Category",
        },
        "MODULES": {},
    }
    assert config._mandatory == ["name", "version", "category", "author"]


def test_metadata():
    """Test metadata"""
    config = KConfig(name="Test", version="1.0", category="Category", author="Author")
    metadata = config.metadata()
    # NOTE: Check that metadata contains type hints for each attribute
    assert "name" in metadata
    assert "version" in metadata
    assert "display_label" in metadata
    assert "category" in metadata
    assert "description" in metadata
    assert "author" in metadata
    assert "author_email" in metadata
    assert "MANIFEST" in metadata
    assert "DEFAULTS" in metadata
    assert "_mandatory" in metadata


def test_format_metadata_with_no_modules():
    """Test the _format_metadata method"""
    config = KConfig(name="Test", version="1.0", category="Category", author="Author")
    result = config._format_metadata()
    # NOTE: Check if 'PACKAGE' keys are populated correctly
    assert "PACKAGE" in result
    assert result["PACKAGE"]["NAME"] == "Test"
    assert result["PACKAGE"]["VERSION"] == "1.0"
    assert result["PACKAGE"]["CATEGORY"] == "Category"
    # NOTE: Check MODULES is empty
    assert "MODULES" in result
    assert result["MODULES"] == {}


def test_initialization_with_kwargs():
    """Test Initialization with custom values"""
    config = KConfig(
        name="App",
        version="2.0",
        display_label="App Label",
        category="Utilities",
        author="Dev",
        author_email="dev@example.com",
    )
    # NOTE: Assert all values are correctly set
    assert config.name == "App"
    assert config.version == "2.0"
    assert config.display_label == "App Label"
    assert config.category == "Utilities"
    assert config.author == "Dev"
    assert config.author_email == "dev@example.com"
    assert config.MANIFEST == {
        "PACKAGE": {
            "NAME": "App",
            "LABEL": "App Label",
            "VERSION": "2.0",
            "DESCRIPTION": "",
            "CATEGORY": "Utilities",
        },
        "MODULES": {},
    }


def test_format_metadata_with_modules():
    # NOTE: Create a KConfig object for module1
    module = (
        "module1",
        KConfig(name="Module1", version="1.0", category="Category", author="Author"),
    )
    module[1].manifest = {}
    # NOTE: Create a KConfig object for the main config
    config = KConfig(name="Test", version="1.0", category="Category", author="Author")
    # NOTE: Call _format_metadata with the module
    result = config._format_metadata(module)
    # NOTE: Verify the structure of the result
    assert "MODULES" in result, "MODULES should be in the result."
    assert "module1" in result["MODULES"], "Module 'module1' should be in the MODULES."


def test_recompute_package_metadata():
    """Test recompute_package_metadata"""
    config = KConfig(name="Test", version="1.0", category="Category", author="Author")
    new_module = (
        "module2",
        KConfig(name="Module2", version="1.1", category="Category", author="Author"),
    )
    new_module[1].manifest = {}
    # NOTE: Recompute metadata and check if MANIFEST is updated
    result = config.recompute_package_metadata(new_module)
    assert "MODULES" in result
    assert "module2" in result["MODULES"]


def test_data_method():
    """Test data method"""
    config = KConfig(name="Test", version="1.0", category="Category", author="Author")
    # NOTE: Check if data() returns the expected dict with instance attributes
    data = config.data()
    assert data["name"] == "Test"
    assert data["version"] == "1.0"
    assert data["category"] == "Category"
    assert data["author"] == "Author"
    assert "MANIFEST" in data
    assert "_mandatory" in data
