import json
import typer
from pathlib import Path


class PresetManager:
    def __init__(self):
        """Initialize the preset manager and load existing presets."""
        self.config_dir = Path.home() / ".config" / "deep-breath-cli"
        self.presets_file = self.config_dir / "presets.json"
        self.custom_presets = self._load_presets()

    def _load_presets(self) -> dict[str, list[tuple[int, str]]]:
        """Load presets from JSON file or create default structure."""
        if not self.presets_file.exists():
            print("No custom presets found, creating an empty presets file.")
            self.config_dir.mkdir(parents=True, exist_ok=True)
            default_data: dict = {}
            # Save default presets
            with open(self.presets_file, "w") as f:
                json.dump(default_data, f, indent=2)
            return default_data
        else:
            # Load existing presets
            try:
                with open(self.presets_file, "r") as f:
                    data = json.load(f)
                    # Convert JSON lists back to tuples
                    return {
                        name: [tuple(phase) for phase in phases]
                        for name, phases in data.items()
                    }
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading presets file: {e}")
                print("Creating fresh presets file.")
                return {}

    def _save_presets(self) -> None:
        """Save custom presets to JSON file."""
        try:
            # Convert tuples to lists for JSON serialization
            json_data = {
                name: list(phases) for name, phases in self.custom_presets.items()
            }
            with open(self.presets_file, "w") as f:
                json.dump(json_data, f, indent=2)
        except IOError as e:
            print(f"Error saving presets file: {e}")

    def _create_phases(self) -> list[tuple[int, str]]:
        """Create phases through interactive prompts."""
        # Ask for the number of phases
        num_phases = typer.prompt("How many phases do you want?", type=int)
        if num_phases <= 0:
            print("Number of phases must be greater than 0.")
            return []

        # Create each phase interactively
        phases = []
        phase_types = {
            "1": "[blue]Breathe in...",
            "2": "[green]Hold...",
            "3": "[dark_orange]Breathe out...",
        }

        for i in range(num_phases):
            print(f"\nPhase {i + 1}:")
            print("Choose the type of phase:")
            for key, value in phase_types.items():
                print(f"{key}: {value}")
            phase_type = typer.prompt(
                "Enter the number corresponding to the phase type: ", type=str
            )
            if phase_type not in phase_types:
                print("Invalid choice, please try again.")
                return []

            # Get duration for the selected phase type
            duration = typer.prompt(
                "Enter the duration for this phase (in seconds): ", type=int
            )
            if duration <= 0:
                print("Duration must be greater than 0.")
                return []

            phases.append((duration, phase_types[phase_type]))

        return phases

    def create_interactive_preset(self, name: str) -> bool:
        """Create a new preset through interactive prompts."""
        # Check if preset already exists
        if name in self.custom_presets:
            print(f"Preset '{name}' already exists.")
            print(
                f"Please choose a different name or modify it with 'breath modify-pattern --name {name}'"
            )
            return False

        print(f"Creating new breathing pattern: {name}")

        # Create phases using the factored method
        phases = self._create_phases()
        if not phases:  # If error in _create_phases
            return False

        # Save the new preset
        self.custom_presets[name] = phases
        self._save_presets()
        print(f"Pattern '{name}' created successfully!")
        return True

    def get_all_presets(self) -> dict[str, tuple[list[tuple[int, str]], str]]:
        """Get both built-in and custom presets."""
        from .breath import PATTERNS  # Importing here to avoid circular import issues

        all_presets: dict[str, tuple[list[tuple[int, str]], str]] = {}

        # Add built-in patterns
        for name, phases in PATTERNS.items():
            all_presets[name] = (phases, "built-in")

        # Add custom patterns
        for name, phases in self.custom_presets.items():
            all_presets[name] = (phases, "custom")

        return all_presets

    def delete_preset(self, name: str) -> bool:
        """Delete a custom preset."""
        if name not in self.custom_presets:
            print(f"Preset '{name}' does not exist.")
            return False

        # Confirm deletion
        confirm: bool = typer.confirm(
            f"Are you sure you want to delete the preset '{name}'?"
        )
        if not confirm:
            print("Deletion cancelled.")
            return False

        del self.custom_presets[name]
        self._save_presets()
        print(f"Preset '{name}' deleted successfully.")
        return True

    def modify_preset(self, name: str) -> bool:
        """Modify an existing custom preset."""
        if name not in self.custom_presets:
            print(f"Preset '{name}' does not exist.")
            return False

        # Display current pattern
        current_phases = self.custom_presets[name]
        print(f"Current pattern '{name}':")
        for i, (duration, message) in enumerate(current_phases, 1):
            print(f" Phase {i}: {duration}s {message}")

        # Confirm modification
        confirm = typer.confirm(f"Do you want to modify the preset '{name}'?")
        if not confirm:
            print("Modification cancelled.")
            return False

        print(f"Recreating pattern: {name}")

        # Create new phases using the factored method
        phases = self._create_phases()
        if not phases:  # If error in _create_phases
            return False

        # Update the preset
        self.custom_presets[name] = phases
        self._save_presets()
        print(f"Pattern '{name}' modified successfully!")
        return True
