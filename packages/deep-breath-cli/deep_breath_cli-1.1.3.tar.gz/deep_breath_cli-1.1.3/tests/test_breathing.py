from src.deep_breath_cli.breath import app, breath_phase, PATTERNS
from typer.testing import CliRunner
from unittest.mock import call, patch


def test_patterns_are_valid():
    """Test that all patterns in PATTERNS are valid."""
    # Check that the keys are strings and values are lists of tuples
    assert "4-7-8" in PATTERNS
    assert "4-4-4-4" in PATTERNS

    # Check that a pattern has a list of tuples with the correct structure
    pattern_478 = PATTERNS["4-7-8"]
    assert isinstance(pattern_478, list)
    assert len(pattern_478) == 3
    assert all(isinstance(phase, tuple) and len(phase) == 2 for phase in pattern_478)
    assert all(
        isinstance(duration, int) and duration > 0 for duration, _ in pattern_478
    )
    assert all(isinstance(message, str) for _, message in pattern_478)


@patch("src.deep_breath_cli.breath.time.sleep")
@patch("src.deep_breath_cli.breath.track")
def test_breath_phase(mock_track, mock_sleep):
    """Test the breath_phase function."""
    # Prepare the data
    duration = 5
    message = "Test phase"

    # Mock the track function to avoid actual time.sleep calls
    mock_track.return_value = range(duration)  # track should iterate over this range

    # Call the function
    breath_phase(duration, message)

    # Check that track was called with the correct parameters
    mock_sleep.assert_called_with(1)  # Ensure sleep is called with 1 second
    assert mock_sleep.call_count == duration  # Ensure it was called duration times
    mock_track.assert_called_once_with(range(duration), description=message)


def test_presets_command():
    """Test the presets command."""
    runner = CliRunner()
    result = runner.invoke(app, ["presets"])

    # Check that the command executed successfully
    assert result.exit_code == 0
    # Check that the output contains the expected patterns
    assert "Available breathing patterns:" in result.stdout
    assert "4-7-8" in result.stdout
    assert "4-4-4-4" in result.stdout


@patch("src.deep_breath_cli.breath.typer.confirm")
@patch("src.deep_breath_cli.breath.time.sleep")
@patch("src.deep_breath_cli.breath.os.system")
@patch("src.deep_breath_cli.breath.track")
def test_breath_command(mock_track, mock_system, mock_sleep, mock_confirm):
    """Test the breath command."""
    # Mock the confirm function to return True
    mock_confirm.return_value = (
        True  # Simulate user confirming to start the breathing cycle
    )
    mock_track.side_effect = (
        lambda x, **kwargs: x
    )  # Mock track to return the range directly

    runner = CliRunner()
    result = runner.invoke(app, ["start", "--cycle", "1"])

    # Check that the command executed successfully
    assert result.exit_code == 0

    # Check that the confirmation was called
    mock_confirm.assert_called_once_with(
        "Do you want to start a breathing cycle?", abort=True
    )

    # Check that the number of cycles is respected
    assert "Starting a breathing cycle of 1 cycles..." in result.stdout

    # Check that the system clear command was called
    mock_system.assert_called_with("clear")

    # Check that the messages for the breathing pattern are printed
    expected_calls = [
        call(range(4), description="[blue]Breathe in..."),
        call(range(7), description="[green]Hold..."),
        call(range(8), description="[dark_orange]Breathe out..."),
    ]
    mock_track.assert_has_calls(expected_calls)

    # Check that the sleep function was called for each phase in the pattern
    assert mock_sleep.call_count == 20


@patch("src.deep_breath_cli.breath.typer.confirm")
@patch("src.deep_breath_cli.breath.time.sleep")
@patch("src.deep_breath_cli.breath.track")
def test_breath_command_invalid_pattern(mock_track, mock_sleep, mock_confirm):
    """Test the breath command with invalid pattern."""
    mock_confirm.return_value = True
    mock_track.side_effect = lambda x, **kwargs: x

    runner = CliRunner()
    result = runner.invoke(app, ["start", "--cycle", "2", "--pattern", "inexistant"])

    assert result.exit_code == 0
    assert (
        "Pattern 'inexistant' not found. Using default pattern '4-7-8'."
        in result.stdout
    )
    assert mock_sleep.call_count == 39


@patch("src.deep_breath_cli.breath.typer.confirm")
@patch("src.deep_breath_cli.breath.time.sleep")
@patch("src.deep_breath_cli.breath.track")
def test_breath_command_cycle_less_than_one(mock_track, mock_sleep, mock_confirm):
    """Test the breath command with cycle < 1."""
    mock_confirm.return_value = True
    mock_track.side_effect = lambda x, **kwargs: x

    runner = CliRunner()
    result = runner.invoke(app, ["start", "--cycle", "0"])

    assert result.exit_code == 0
    assert "Cycle must be at least 1. Setting to 1." in result.stdout
    assert mock_sleep.call_count == 20
