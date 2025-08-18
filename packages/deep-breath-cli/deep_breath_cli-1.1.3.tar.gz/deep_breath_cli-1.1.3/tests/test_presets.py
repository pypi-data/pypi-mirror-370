import json
from unittest.mock import patch, mock_open
from src.deep_breath_cli.presets import PresetManager


def test_preset_manager_init():
    """Test PresetManager initialization."""
    # Test with non-existent file
    with (
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
    ):
        manager = PresetManager()
        assert manager.custom_presets == {}


def test_load_presets_file_exists():
    """Test loading presets from existing file."""
    # Fake JSON data
    mock_data = {"custom-pattern": [[4, "[blue]Breathe in..."], [7, "[green]Hold..."]]}

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data=json.dumps(mock_data))),
        patch("json.load", return_value=mock_data),
    ):
        manager = PresetManager()

        # Check that data is loaded and converted to tuples
        expected = {
            "custom-pattern": [(4, "[blue]Breathe in..."), (7, "[green]Hold...")]
        }
        assert manager.custom_presets == expected


def test_delete_preset_success():
    """Test successful preset deletion."""
    # Setup: manager with an existing preset
    with (
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
    ):
        manager = PresetManager()
        manager.custom_presets = {"test-pattern": [(4, "Breathe")]}

    # Mock typer.confirm to return True
    with (
        patch("typer.confirm", return_value=True),
        patch.object(manager, "_save_presets") as mock_save,
    ):
        result = manager.delete_preset("test-pattern")

        assert result is True
        assert "test-pattern" not in manager.custom_presets
        mock_save.assert_called_once()


def test_delete_preset_not_found():
    """Test deleting non-existent preset."""
    with (
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
    ):
        manager = PresetManager()

    result = manager.delete_preset("non-existent")
    assert result is False


def test_delete_preset_cancelled():
    """Test deleting preset but user cancels."""
    with (
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
    ):
        manager = PresetManager()
        manager.custom_presets = {"test-pattern": [(4, "Breathe")]}

    with patch("typer.confirm", return_value=False):
        result = manager.delete_preset("test-pattern")

        assert result is False
        assert "test-pattern" in manager.custom_presets  # Still there


def test_create_preset_already_exists():
    """Test creating preset with existing name."""
    with (
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
    ):
        manager = PresetManager()
        manager.custom_presets = {"existing": [(4, "Breathe")]}

    result = manager.create_interactive_preset("existing")
    assert result is False


@patch("typer.prompt")
def test_create_preset_success(mock_prompt):
    """Test successful preset creation."""
    # Setup manager
    with (
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
    ):
        manager = PresetManager()

    # Mock user inputs
    mock_prompt.side_effect = [
        2,  # number of phases
        "1",  # phase 1 type
        5,  # phase 1 duration
        "2",  # phase 2 type
        7,  # phase 2 duration
    ]

    with patch.object(manager, "_save_presets") as mock_save:
        result = manager.create_interactive_preset("new-pattern")

        assert result is True
        assert "new-pattern" in manager.custom_presets
        expected_phases = [(5, "[blue]Breathe in..."), (7, "[green]Hold...")]
        assert manager.custom_presets["new-pattern"] == expected_phases
        mock_save.assert_called_once()


@patch("typer.prompt")
def test_create_preset_invalid_phase_type(mock_prompt):
    """Test creation with invalid phase type."""
    with (
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
    ):
        manager = PresetManager()

    # Mock: number of phases OK, but invalid type
    mock_prompt.side_effect = [
        1,  # number of phases
        "9",  # invalid type
    ]

    result = manager.create_interactive_preset("test")
    assert result is False


def test_modify_preset_not_found():
    """Test modifying non-existent preset."""
    with (
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
    ):
        manager = PresetManager()

    result = manager.modify_preset("non-existent")
    assert result is False


@patch("typer.confirm")
@patch("typer.prompt")
def test_modify_preset_success(mock_prompt, mock_confirm):
    """Test successful preset modification."""
    with (
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
    ):
        manager = PresetManager()
        manager.custom_presets = {"old-pattern": [(3, "Old")]}

    # Mock user confirmation and new inputs
    mock_confirm.return_value = True
    mock_prompt.side_effect = [
        1,  # number of phases
        "3",  # phase 1 type
        8,  # phase 1 duration
    ]

    with patch.object(manager, "_save_presets") as mock_save:
        result = manager.modify_preset("old-pattern")

        assert result is True
        expected = [(8, "[dark_orange]Breathe out...")]
        assert manager.custom_presets["old-pattern"] == expected
        mock_save.assert_called_once()


@patch("typer.confirm")
def test_modify_preset_cancelled(mock_confirm):
    """Test modifying preset but user cancels."""
    with (
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
    ):
        manager = PresetManager()
        original = [(4, "Original")]
        manager.custom_presets = {"test": original.copy()}

    mock_confirm.return_value = False
    result = manager.modify_preset("test")

    assert result is False
    assert manager.custom_presets["test"] == original  # Unchanged


def test_save_presets():
    """Test saving presets to file."""
    with patch("pathlib.Path.exists", return_value=False):
        manager = PresetManager()
        manager.custom_presets = {"test": [(4, "[blue]Breathe in...")]}

    mock_file = mock_open()
    with patch("builtins.open", mock_file), patch("json.dump") as mock_json_dump:
        manager._save_presets()

        # Verify that json.dump was called with the correct data
        mock_file.assert_called_once()
        mock_json_dump.assert_called_once()

        # Verify the data passed to json.dump
        call_args = mock_json_dump.call_args[0]
        expected_data = {"test": [(4, "[blue]Breathe in...")]}
        assert call_args[0] == expected_data
