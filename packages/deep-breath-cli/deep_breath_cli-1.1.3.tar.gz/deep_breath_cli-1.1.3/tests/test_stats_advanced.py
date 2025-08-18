from unittest.mock import patch, mock_open, MagicMock, call
from datetime import datetime, timedelta
from src.deep_breath_cli.stats import StatsManager


def test_generate_sessions_chart():
    """Test sessions chart generation."""
    with (
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
    ):
        manager = StatsManager()

        # Mock sessions data for last 7 days
        today = datetime.now().date()
        yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
        today_str = today.strftime("%Y-%m-%d")

        manager.data["sessions"] = [
            {
                "date": today_str,
                "pattern": "4-7-8",
                "cycles": 4,
                "duration_seconds": 76,
            },
            {
                "date": today_str,
                "pattern": "4-7-8",
                "cycles": 2,
                "duration_seconds": 38,
            },
            {
                "date": yesterday,
                "pattern": "4-4-4-4",
                "cycles": 3,
                "duration_seconds": 48,
            },
        ]

    # Mock plotext
    with (
        patch("plotext.clear_data"),
        patch("plotext.bar"),
        patch("plotext.title"),
        patch("plotext.plot_size"),
        patch("plotext.canvas_color"),
        patch("plotext.axes_color"),
        patch("plotext.ticks_color"),
        patch("plotext.build", return_value="Mock Chart"),
    ):
        result = manager._generate_sessions_chart()
        assert result == "Mock Chart"


def test_generate_patterns_chart():
    """Test patterns chart generation."""
    with (
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
    ):
        manager = StatsManager()
        manager.data["patterns_used"] = {"4-7-8": 5, "4-4-4-4": 3}

    with (
        patch("plotext.clear_data"),
        patch("plotext.bar"),
        patch("plotext.title"),
        patch("plotext.plot_size"),
        patch("plotext.canvas_color"),
        patch("plotext.axes_color"),
        patch("plotext.ticks_color"),
        patch("plotext.build", return_value="Pattern Chart"),
    ):
        result = manager._generate_patterns_chart()
        assert result == "Pattern Chart"


def test_generate_patterns_chart_no_data():
    """Test patterns chart with no data."""
    with (
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
    ):
        manager = StatsManager()
        manager.data["patterns_used"] = {}

    result = manager._generate_patterns_chart()
    assert result == "No pattern data available."


def test_export_stats_invalid_format():
    """Test export with invalid format."""
    with (
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
    ):
        manager = StatsManager()

    # Capture print output
    with patch("builtins.print") as mock_print:
        manager.export_stats("invalid", "")
        mock_print.assert_called_with("Invalid format. Please choose 'json' or 'csv'.")


def test_export_json():
    """Test JSON export."""
    with (
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
    ):
        manager = StatsManager()
        manager.data = {"total_sessions": 5, "sessions": []}

    mock_file = mock_open()
    with patch("builtins.open", mock_file), patch("json.dump") as mock_json_dump:
        manager._export_json("test.json")

        mock_file.assert_called_once_with("test.json", "w")
        mock_json_dump.assert_called_once_with(manager.data, mock_file(), indent=2)


def test_export_csv():
    """Test CSV export."""
    with (
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
    ):
        manager = StatsManager()
        manager.data = {
            "sessions": [
                {
                    "date": "2025-08-06",
                    "pattern": "4-7-8",
                    "cycles": 4,
                    "duration_seconds": 76,
                },
                {
                    "date": "2025-08-05",
                    "pattern": "4-4-4-4",
                    "cycles": 2,
                    "duration_seconds": 32,
                },
            ]
        }

    mock_file = mock_open()
    with patch("builtins.open", mock_file), patch("csv.writer") as mock_csv_writer:
        mock_writer_instance = MagicMock()
        mock_csv_writer.return_value = mock_writer_instance

        manager._export_csv("test.csv")

        mock_file.assert_called_once_with("test.csv", "w", newline="")

        # Vérifier les appels au writer - syntaxe corrigée
        expected_calls = [
            call(["Date", "Pattern", "Cycles", "Duration (seconds)"]),
            call(["2025-08-06", "4-7-8", 4, 76]),
            call(["2025-08-05", "4-4-4-4", 2, 32]),
        ]
        mock_writer_instance.writerow.assert_has_calls(expected_calls)


def test_export_stats_success():
    """Test successful export with auto-generated filename."""
    with (
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
    ):
        manager = StatsManager()

    with (
        patch.object(manager, "_export_json") as mock_export,
        patch("builtins.print") as mock_print,
        patch("src.deep_breath_cli.stats.datetime") as mock_datetime,
    ):
        # Mock datetime pour filename généré
        mock_now = MagicMock()
        mock_now.strftime.return_value = "20250806_143000"
        mock_datetime.now.return_value = mock_now

        manager.export_stats("json", "")

        mock_export.assert_called_once_with("breathing_stats_20250806_143000.json")
        mock_print.assert_called_with(
            "Stats exported to: breathing_stats_20250806_143000.json"
        )


def test_get_detailed_stats():
    """Test detailed stats display with charts."""
    with (
        patch("pathlib.Path.exists", return_value=False),
        patch("builtins.open", mock_open()),
    ):
        manager = StatsManager()

    with (
        patch.object(manager, "get_display_stats", return_value="Basic Stats"),
        patch.object(
            manager, "_generate_sessions_chart", return_value="Sessions Chart"
        ),
        patch.object(
            manager, "_generate_patterns_chart", return_value="Patterns Chart"
        ),
    ):
        result = manager.get_detailed_stats()

        expected = "Basic Stats\n\nSessions Chart\n\nPatterns Chart"
        assert result == expected
