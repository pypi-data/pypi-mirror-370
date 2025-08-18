from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from src.deep_breath_cli.breath import app


def test_create_pattern_command():
    """Test create-pattern command."""
    runner = CliRunner()

    with patch("src.deep_breath_cli.breath.PresetManager") as mock_preset_manager:
        mock_instance = MagicMock()
        mock_preset_manager.return_value = mock_instance
        mock_instance.create_interactive_preset.return_value = True

        result = runner.invoke(app, ["create-pattern", "test-pattern"])

        assert result.exit_code == 0
        mock_instance.create_interactive_preset.assert_called_once_with("test-pattern")


def test_delete_pattern_command():
    """Test delete-pattern command."""
    runner = CliRunner()

    with patch("src.deep_breath_cli.breath.PresetManager") as mock_preset_manager:
        mock_instance = MagicMock()
        mock_preset_manager.return_value = mock_instance
        mock_instance.delete_preset.return_value = True

        result = runner.invoke(app, ["delete-pattern", "test-pattern"])

        assert result.exit_code == 0
        mock_instance.delete_preset.assert_called_once_with("test-pattern")


def test_modify_pattern_command():
    """Test modify-pattern command."""
    runner = CliRunner()

    with patch("src.deep_breath_cli.breath.PresetManager") as mock_preset_manager:
        mock_instance = MagicMock()
        mock_preset_manager.return_value = mock_instance
        mock_instance.modify_preset.return_value = True

        result = runner.invoke(app, ["modify-pattern", "test-pattern"])

        assert result.exit_code == 0
        mock_instance.modify_preset.assert_called_once_with("test-pattern")


def test_export_stats_command():
    """Test export-stats command."""
    runner = CliRunner()

    with patch("src.deep_breath_cli.breath.StatsManager") as mock_stats_manager:
        mock_instance = MagicMock()
        mock_stats_manager.return_value = mock_instance

        result = runner.invoke(app, ["export-stats", "--format", "json"])

        assert result.exit_code == 0
        mock_instance.export_stats.assert_called_once_with("json", "")


def test_stats_detailed_command():
    """Test stats command with --detailed flag."""
    runner = CliRunner()

    with patch("src.deep_breath_cli.breath.StatsManager") as mock_stats_manager:
        mock_instance = MagicMock()
        mock_stats_manager.return_value = mock_instance
        mock_instance.get_detailed_stats.return_value = "Detailed Stats Output"

        result = runner.invoke(app, ["stats", "--detailed"])

        assert result.exit_code == 0
        assert "Detailed Stats Output" in result.stdout
        mock_instance.get_detailed_stats.assert_called_once()
