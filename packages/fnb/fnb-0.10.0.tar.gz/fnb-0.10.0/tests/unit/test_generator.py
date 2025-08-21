import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open, call

from fnb.generator import find_template, create_file_from_template, run, ConfigKind


def test_find_template_not_found():
    """
    Test that find_template returns None when the template does not exist.
    """
    with patch("importlib.resources.files") as mock_files:
        # Configure the mock to simulate that no file exists
        mock_files.return_value.joinpath.return_value.exists.return_value = False

        # Also patch Path.exists to return False
        with patch("pathlib.Path.exists") as mock_path_exists:
            mock_path_exists.return_value = False

            template_path = find_template("non_existent_template.toml")
            assert template_path is None


@patch("fnb.generator.find_template")
@patch("pathlib.Path.exists")
def test_create_file_from_template_already_exists_no_force(
    mock_exists, mock_find_template
):
    """
    Test that create_file_from_template does not overwrite an existing file if force is False.
    """
    # Arrange
    mock_exists.return_value = True
    dest_path = Path("/fake/dest/file.toml")

    # Act
    success = create_file_from_template(
        template_name="any_template.toml", dest_path=dest_path, force=False
    )

    # Assert
    assert not success, "Should return False when file exists and force is False"
    mock_find_template.assert_not_called()  # Should not even look for a template


@patch("fnb.generator.typer.echo")
@patch("fnb.generator.find_template", return_value=None)
@patch("pathlib.Path.exists", return_value=False)
def test_create_file_from_template_template_not_found(
    mock_exists, mock_find_template, mock_echo
):
    """
    Test that create_file_from_template handles the case where the template is not found.
    """
    # Arrange
    dest_path = Path("/fake/dest/file.toml")

    # Act
    success = create_file_from_template(
        template_name="non_existent_template.toml", dest_path=dest_path, force=False
    )

    # Assert
    assert not success, "Should return False when template is not found"
    mock_find_template.assert_called_once_with("non_existent_template.toml")
    mock_echo.assert_called_with(
        "❌ Template file non_existent_template.toml not found. Check if fnb is installed correctly."
    )


@patch("fnb.generator.typer.echo")
@patch("fnb.generator.find_template")
def test_create_file_from_template_success(mock_find_template, mock_echo):
    """
    Test the successful creation of a file from a template, including replacements and header.
    """
    # Arrange
    template_content = "Hello, {{name}}!"

    # 1. Mock the source path and its open() method
    mock_src_path = MagicMock(spec=Path)
    # mock_open returns a mock for the 'open' function.
    # We assign this mock to the 'open' attribute of our path mock.
    mock_src_path.open = mock_open(read_data=template_content)

    # 2. Mock find_template to return our source path mock
    mock_find_template.return_value = mock_src_path

    # 3. Mock the destination path and its open() method
    mock_dest_path = MagicMock(spec=Path)
    mock_dest_path.exists.return_value = False
    m_open_dest = mock_open()
    mock_dest_path.open = m_open_dest

    replacements = {"{{name}}": "world"}
    header = "# HEADER"

    # Act
    success = create_file_from_template(
        template_name="any_template.toml",
        dest_path=mock_dest_path,
        force=False,
        replacements=replacements,
        header_comment=header,
    )

    # Assert
    assert success, "Should return True on successful file creation"

    # Check find_template was called
    mock_find_template.assert_called_once_with("any_template.toml")

    # Check directory creation was attempted
    mock_dest_path.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    # Check template was read
    mock_src_path.open.assert_called_once_with("r")

    # Check destination file was written correctly
    mock_dest_path.open.assert_called_once_with("w")
    handle = m_open_dest()
    expected_content = "# HEADER\n\nHello, world!"
    handle.write.assert_called_once_with(expected_content)

    # Check success message
    mock_echo.assert_called_with(f"✅ Created {mock_dest_path} from template.")


@patch("fnb.generator.typer.echo")
def test_run_invalid_kind(mock_echo):
    """
    Test that run exits if an invalid kind is provided.
    """
    # Arrange
    invalid_kind = "invalid"

    # Act & Assert
    with pytest.raises(SystemExit) as excinfo:
        run(kind=invalid_kind, force=False)

    # Assert that sys.exit(1) was called
    assert excinfo.value.code == 1

    # Assert that the correct error messages were printed
    mock_echo.assert_any_call(f"❌ Invalid configuration kind: {invalid_kind}")
    mock_echo.assert_any_call("Valid kinds: all, config, env")
