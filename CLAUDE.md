# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Python 3.10 coursework project for the ROSIS master's programme at FERI. Exercises are organized in subdirectories named `vajaX/` (e.g. `vaja1/`, `vaja2/`).

## Environment

Activate the virtual environment before running anything:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run a script:

```powershell
python main.py
python vaja1\solution.py
```

Install dependencies when needed:

```powershell
pip install <package>
pip freeze > requirements.txt
```

There is no test runner, linter, or build tool configured yet. Add them per-exercise as the course progresses.