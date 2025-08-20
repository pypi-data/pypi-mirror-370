from kaya_module_sdk.src.utils.metadata.display_description import (
    load_markdown,
    DisplayDescription,
)


def test_load_markdown_success(tmp_path, monkeypatch, dummy_resource, dummy_context_manager):
    """
    Test load_markdown successfully reads the content of a markdown file.
    We simulate the resource loading mechanism by patching `files` and `as_file`.
    """
    # Create a temporary markdown file.
    file_path = tmp_path / "test.md"
    expected_content = "# This is a test markdown\nSome dummy content here."
    file_path.write_text(expected_content)

    # Create a dummy resource that returns the temporary file's path.
    dummy_resource = dummy_resource(str(file_path))

    # Monkey-patch the files() function so that it returns our dummy resource.
    monkeypatch.setattr(
        "kaya_module_sdk.src.utils.metadata.display_description.files",
        lambda location: dummy_resource,
    )

    # Monkey-patch as_file() to yield our file path (wrapped in a context manager).
    monkeypatch.setattr(
        "kaya_module_sdk.src.utils.metadata.display_description.as_file",
        lambda resource: dummy_context_manager(resource.dummy_path),
    )

    # Call load_markdown and verify the content.
    result = load_markdown("dummy_location", "dummy_file.md")
    assert result == expected_content


def test_display_description_str():
    """
    Test that the string representation (__str__) returns the expected output.
    """
    desc = "Test description"
    instance = DisplayDescription(desc)
    assert str(instance) == f"description:{desc}"


def test_display_description_load_valid():
    """
    Test that load() correctly processes a valid string representation.
    """
    instance = DisplayDescription("Initial")
    # A valid string representation: prefix "description:" and a new value.
    result = instance.load("description:NewValue")
    expected = {"description": "NewValue"}
    assert result == expected
    # Also verify that the internal data was updated.
    assert instance._data["description"] == "NewValue"


def test_display_description_load_invalid():
    """
    Test that load() returns an empty dict when given an invalid string representation.
    """
    instance = DisplayDescription("Initial")
    # An invalid string (missing the proper prefix and colon)
    result = instance.load("invalid_string")
    assert result == {}
    # The internal data should remain unchanged.
    assert instance._data["description"] == "Initial"


def test_display_description_load_with_extra_segments():
    """
    Test that load() returns an empty dict when the string has extra segments.
    """
    instance = DisplayDescription("Initial")
    # A string with extra colon segments should be invalid.
    result = instance.load("description:Too:Many:Segments")
    assert result == {}
    # The internal data remains unchanged.
    assert instance._data["description"] == "Initial"
