# Deep Breath CLI

![PyPI version](https://badge.fury.io/py/deep-breath-cli.svg)
![Python versions](https://img.shields.io/pypi/pyversions/deep-breath-cli.svg)
![Build Status](https://github.com/weart99/deep-breath-cli/actions/workflows/ci.yml/badge.svg)
![Publication Status](https://github.com/weart99/deep-breath-cli/actions/workflows/publish.yml/badge.svg)
![License](https://img.shields.io/pypi/l/deep-breath-cli.svg)

**Deep Breath CLI** is a command-line tool designed to help you relax, regain focus, and boost your energy—right from your terminal.

## 🌬️ What is Deep Breath CLI?

Whether you're coding, studying, or just need a quick break, Deep Breath CLI offers guided breathing exercises with visual progress bars and calming colors. With simple commands, you can access different breathing patterns to help you reset and recharge.

## 🚀 Features

- Multiple breathing patterns (4-7-8, Box breathing)
- Visual progress bars with calming colors
- Customizable session lengths and cycles
- **Track your progress with detailed statistics**
- **Create, modify, and delete custom breathing patterns**
- Clear, distraction-free interface
- Easy preset management

## 🛠️ Installation

Install from PyPI:

```bash
pip install deep-breath-cli
```

## ⚡️ Usage

### Start a breathing session

```bash
# Default session (4 cycles of 4-7-8 pattern)
breath start

# Custom number of cycles
breath start --cycle 8

# Different breathing pattern
breath start --pattern "4-4-4-4"

# Use a custom pattern
breath start --pattern "my-custom"

# Combined options
breath start --cycle 6 --pattern "4-4-4-4"
```

### View available patterns (including custom ones)

```bash
breath presets
```

Output:

```plaintext
Available breathing patterns:
  4-7-8: 4s Breathe in..., 7s Hold..., 8s Breathe out... (built-in)
  4-4-4-4: 4s Breathe in..., 4s Hold..., 4s Breathe out..., 4s Hold... (built-in)
  my-custom: 3s Breathe in..., 5s Hold..., 4s Breathe out... (custom)

You can use these patterns with the --pattern option.
```

## Track your progress

Monitor your breathing journey with detailed statistics:

```bash
# Basic stats overview
breath stats
```

Example output:

```plaintext
Your Breathing Stats
            Total sessions: 7
            Total time: 2 minutes
            Favorite pattern: 4-4-4-4 (2 sessions)
            Current streak: 2 days

Use 'breath stats --detailed' for charts and advanced analytics.
```

## Advanced statistics

The `--detailed` flag shows beautiful ASCII charts including:

- **Sessions over last 7 days**: Visual timeline of your daily practice
- **Pattern usage distribution**: See which breathing techniques you use most

```bash
# Detailed view with beautiful ASCII charts
breath stats --detailed
```

## Export your statistics

Export your breathing data for external analysis or backup:

```bash
# Export complete data as JSON
breath export-stats --format json

# Export session data as CSV
breath export-stats --format csv

# Custom output file
breath export-stats --format json --output my_backup.json
```

**CSV Export includes:** Date, Pattern, Cycles, Duration (seconds)  
**JSON Export includes:** Complete statistics with all session details

## Custom patterns

Create your own breathing patterns tailored to your needs:

### Create a new pattern

```bash
breath create-pattern "my-custom"
```

This will guide you through an interactive process to define each phase of your breathing pattern.

### Modify an existing pattern

```bash
breath modify-pattern "my-custom"
```

### Delete a pattern

```bash
breath delete-pattern "my-custom"
```

### Get help

```bash
breath --help
breath start --help
```

## 🌟 Breathing Patterns

- **4-7-8**: Relaxation pattern (inhale 4s, hold 7s, exhale 8s)
- **4-4-4-4**: Box breathing for focus (inhale 4s, hold 4s, exhale 4s, hold 4s)
- **Custom patterns**: Create your own with any number of phases and durations

## 🤔 Why use Deep Breath CLI?

- **Quick:** Take a break without leaving your terminal
- **Effective:** Scientifically-backed breathing techniques
- **Customizable:** Choose the pattern and duration that fits your needs
- **Progress tracking:** Monitor your breathing journey with detailed statistics
- **Distraction-free:** Clear your mind with simple, focused interface

## 🛠️ Development

### Setup (with uv, which I used to develop this package)

```bash
git clone https://github.com/weart99/deep-breath-cli
cd deep-breath-cli
uv sync --extra dev
```

### Running tests

```bash
uv run pytest tests/ --cov=src
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure they pass
5. Submit a pull request

## 📄 License

[MIT Licence](https://choosealicense.com/licenses/mit/)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

## Authors

[@weart99](https://www.github.com/weart99)

---

Take a deep breath, and let's get started! 🌬️
