import json
import plotext as plt
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any


class StatsManager:
    def __init__(self):
        """Initialize the stats manager and load existing stats."""
        self.config_dir = Path.home() / ".config" / "deep-breath-cli"
        self.stats_file = self.config_dir / "stats.json"
        self.data = self._load_stats()

    def _load_stats(self) -> dict[str, Any]:
        """Load stats from JSON file or create default structure."""
        if not self.stats_file.exists():
            print("Stats file not found, creating default stats.")
            self.config_dir.mkdir(parents=True, exist_ok=True)
            default_data = {
                "total_sessions": 0,
                "total_time_seconds": 0,
                "patterns_used": {"4-7-8": 0, "4-4-4-4": 0},
                "sessions": [],
                "streaks": {"current": 0, "longest": 0},
            }
            # Save default data
            with open(self.stats_file, "w") as f:
                json.dump(default_data, f, indent=2)
            return default_data
        else:
            # Load existing stats
            try:
                with open(self.stats_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading stats file: {e}")
                print("Creating fresh stats file.")
                # Recreate the stats file if there's an error
                return self._load_stats()

    def _save_stats(self) -> None:
        """Save current stats to JSON file."""
        try:
            with open(self.stats_file, "w") as f:
                json.dump(self.data, f, indent=2)
        except IOError as e:
            print(f"Error saving stats file: {e}")

    def add_session(self, pattern: str, cycles: int, duration_seconds: int) -> None:
        """Add a completed breathing session to stats."""
        # Add session data to the sessions list
        session = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "pattern": pattern,
            "cycles": cycles,
            "duration_seconds": duration_seconds,
        }
        self.data["sessions"].append(session)
        # Increment total sessions and time
        self.data["total_sessions"] += 1
        self.data["total_time_seconds"] += duration_seconds
        # Increment pattern usage
        # self.data["patterns_used"][pattern] = self.data["patterns_used"].get(pattern, 0) + 1
        if pattern in self.data["patterns_used"]:
            self.data["patterns_used"][pattern] += 1
        else:
            self.data["patterns_used"][pattern] = 1
        # Update streaks
        current_streak = self._calculate_streak()
        self.data["streaks"]["current"] = current_streak
        if current_streak > self.data["streaks"]["longest"]:
            self.data["streaks"]["longest"] = current_streak
        # Save updated stats
        self._save_stats()

    def get_display_stats(self) -> str:
        """Format stats for display in terminal."""
        if self.data["total_sessions"] == 0:
            return "No breathing sessions recorded yet.\nStart your first session with 'breath start' to begin tracking your progress!"

        # Calculate total time in a user-friendly format
        total_time_seconds = self.data["total_time_seconds"]
        total_time_minutes = total_time_seconds // 60

        if total_time_minutes < 1:
            time_display = f"{total_time_seconds} seconds"
        elif total_time_minutes < 60:
            time_display = f"{total_time_minutes} minutes"
        else:
            hours = total_time_minutes // 60
            minutes = total_time_minutes % 60
            time_display = f"{hours}h {minutes}min"

        # Get the favorite pattern
        if self.data["patterns_used"]:
            favorite_pattern = max(
                self.data["patterns_used"], key=self.data["patterns_used"].get
            )
            favorite_count = self.data["patterns_used"][favorite_pattern]

        return f"""Your Breathing Stats
            Total sessions: {self.data["total_sessions"]}
            Total time: {time_display}
            Favorite pattern: {favorite_pattern} ({favorite_count} sessions)
            Current streak: {self.data["streaks"]["current"]} days (Longest: {self.data["streaks"]["longest"]} days)"""

    def _calculate_streak(self) -> int:
        """Calculate current streak of consecutive days."""
        if not self.data["sessions"]:
            return 0  # No sessions means no streak

        # Get the unique dates from sessions
        session_dates = set(session["date"] for session in self.data["sessions"])

        # Check if the last session was today
        today = datetime.now().date()

        streak = 0
        current_date = today

        # Check backwards day by day for consecutive sessions
        while current_date.strftime("%Y-%m-%d") in session_dates:
            streak += 1
            current_date = current_date - timedelta(days=1)

        return streak

    def _generate_sessions_chart(self) -> str:
        """Generate ASCII chart of sessions in last 7 days."""

        # Get last 7 days
        today = datetime.now().date()
        last_week = [
            (today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)
        ]

        # Count sessions per day
        daily_counts = []
        day_labels = []

        for day in last_week:
            count = sum(
                1 for session in self.data["sessions"] if session["date"] == day
            )
            daily_counts.append(count)
            # Format label (Mon, Tue, etc.)
            day_obj = datetime.strptime(day, "%Y-%m-%d")
            day_labels.append(day_obj.strftime("%a"))

        # Generate chart with plotext
        plt.clear_data()

        # Color personalization
        plt.canvas_color("black")  # Background color
        plt.axes_color("black")  # Axes color
        plt.ticks_color("white")  # Graduations

        plt.bar(day_labels, daily_counts, color="cyan+")
        plt.title("Sessions Last 7 Days")
        plt.plot_size(50, 10)  # Chart width

        chart_string = plt.build()
        plt.clear_data()

        return chart_string

    def _generate_patterns_chart(self) -> str:
        """Generate ASCII chart of pattern usage."""
        if not self.data["patterns_used"]:
            return "No pattern data available."

        # Préparer les données
        patterns = list(self.data["patterns_used"].keys())
        counts = list(self.data["patterns_used"].values())

        # Generate chart
        plt.clear_data()
        plt.canvas_color("black")
        plt.axes_color("black")
        plt.ticks_color("white")

        plt.bar(patterns, counts, color="cyan+")
        plt.title("Pattern Usage")
        plt.plot_size(50, 8)

        chart_string = plt.build()
        plt.clear_data()
        return chart_string

    def get_detailed_stats(self) -> str:
        """Format detailed stats with charts for display in terminal."""
        basic = self.get_display_stats()

        # Add graphics
        sessions_chart = self._generate_sessions_chart()
        patterns_chart = self._generate_patterns_chart()
        return f"{basic}\n\n{sessions_chart}\n\n{patterns_chart}"

    def export_stats(self, format: str = "json", output_path: str = "") -> None:
        """Export stats to JSON or CSV format."""
        if format not in ["json", "csv"]:
            print("Invalid format. Please choose 'json' or 'csv'.")
            return

        # Generate the default filename
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"breathing_stats_{timestamp}.{format}"

        try:
            if format == "json":
                self._export_json(output_path)
            elif format == "csv":
                self._export_csv(output_path)

            print(f"Stats exported to: {output_path}")
        except Exception as e:
            print(f"Error exporting stats: {e}")

    def _export_json(self, output_path: str) -> None:
        """Export sessions data as JSON."""
        with open(output_path, "w") as f:
            json.dump(self.data, f, indent=2)

    def _export_csv(self, output_path: str) -> None:
        """Export sessions data as CSV."""
        import csv

        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            # Headers
            writer.writerow(["Date", "Pattern", "Cycles", "Duration (seconds)"])

            # Data rows
            for session in self.data["sessions"]:
                writer.writerow(
                    [
                        session["date"],
                        session["pattern"],
                        session["cycles"],
                        session["duration_seconds"],
                    ]
                )
