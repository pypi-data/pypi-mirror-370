import os
import time
import typer
from rich.console import Console
from rich.progress import track
from typing_extensions import Annotated
from .presets import PresetManager
from .stats import StatsManager


PATTERNS: dict[str, list[tuple[int, str]]] = {
    "4-7-8": [
        (4, "[blue]Breathe in..."),
        (7, "[green]Hold..."),
        (8, "[dark_orange]Breathe out..."),
    ],
    "4-4-4-4": [
        (4, "[blue]Breathe in..."),
        (4, "[green]Hold..."),
        (4, "[dark_orange]Breathe out..."),
        (4, "[green]Hold..."),
    ],
}


app = typer.Typer()


def breath_phase(duration: int, message: str):
    """Breathing phase with a message."""
    for value in track(range(duration), description=message):
        time.sleep(1)


@app.command()
def presets():
    """Display available breathing patterns."""
    console = Console()
    console.print("Available breathing patterns:", style="bold")
    preset_manager: PresetManager = PresetManager()
    all_presets: dict[str, tuple[list[tuple[int, str]], str]] = (
        preset_manager.get_all_presets()
    )

    for pattern, (phases, preset_type) in all_presets.items():
        phases_display: list = []
        for duration, message in phases:
            phases_display.append(f"{duration}s {message}")
        phases_str = "[white], ".join(phases_display)
        console.print(f"  {pattern}: {phases_str} [white]({preset_type})")
    console.print(
        "\nYou can use these patterns with the --pattern option.", style="dim"
    )


@app.command("create-pattern")
def create_pattern(name: str):
    """Create a new breathing pattern interactively."""
    preset_manager = PresetManager()
    preset_manager.create_interactive_preset(name)


@app.command("delete-pattern")
def delete_pattern(name: str):
    """Delete a custom breathing pattern."""
    preset_manager = PresetManager()
    preset_manager.delete_preset(name)


@app.command("modify-pattern")
def modify_pattern(name: str):
    """Modify an existing custom breathing pattern."""
    preset_manager = PresetManager()
    preset_manager.modify_preset(name)


@app.command("stats")
def stats(
    detailed: Annotated[
        bool,
        typer.Option("--detailed", "-d", help="Show detailed stats with charts"),
    ] = False,
):
    """Display breathing session statistics."""
    stats_manager = StatsManager()
    if detailed:
        print(stats_manager.get_detailed_stats())
    else:
        print(stats_manager.get_display_stats())
        print("\nUse 'breath stats --detailed' for charts and advanced analytics.")


@app.command("export-stats")
def export_stats(
    format: Annotated[
        str,
        typer.Option(
            "--format", "-f", help="The format to export the stats to (json or csv)."
        ),
    ] = "json",
    output_path: Annotated[
        str, typer.Option("--output", "-o", help="The name of the exporting file.")
    ] = "",
):
    """Export breathing session statistics."""
    stats_manager = StatsManager()
    stats_manager.export_stats(format, output_path)


@app.command("start")
def breath(
    cycle: Annotated[
        int, typer.Option(help="The number of cycle you want to breathe.")
    ] = 4,
    pattern: Annotated[
        str, typer.Option(help="The pattern you want to breath with.")
    ] = "4-7-8",
):
    """Main function to start the breathing cycle."""
    print("Hello from deep-breathe-cli!")
    typer.confirm("Do you want to start a breathing cycle?", abort=True)
    if cycle < 1:
        print("Cycle must be at least 1. Setting to 1.")
        cycle = 1
    print(f"Starting a breathing cycle of {cycle} cycles...")
    time.sleep(2)

    preset_manager: PresetManager = PresetManager()
    all_presets: dict[str, tuple[list[tuple[int, str]], str]] = (
        preset_manager.get_all_presets()
    )

    if pattern not in all_presets:
        print(f"Pattern '{pattern}' not found. Using default pattern '4-7-8'.")
        pattern = "4-7-8"

    for cycle_number in range(cycle):
        os.system("clear")  # Clear the console for better visibility
        print(f"Cycle {cycle_number + 1} of {cycle}:")
        phases, _ = all_presets[pattern]
        for duration, message in phases:
            breath_phase(duration, message)
        os.system("clear")

    # Caclulate session duration
    phases, _ = all_presets[pattern]
    pattern_duration = sum(duration for duration, _ in phases)
    total_duration = cycle * pattern_duration

    stats_manager = StatsManager()
    stats_manager.add_session(pattern, cycle, total_duration)
    print("Cycle complete! Take a moment to relax.")


if __name__ == "__main__":
    # typer.run(main)
    app()
