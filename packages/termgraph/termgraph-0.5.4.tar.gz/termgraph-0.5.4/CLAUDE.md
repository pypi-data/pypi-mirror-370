# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Termgraph is a Python command-line tool that draws basic graphs in the terminal. It supports various graph types including bar graphs, histograms, calendar heatmaps, stacked charts, and multi-variable visualizations with color support and emoji tick marks.

The tool can read data from files or stdin and output ASCII-based graphs directly to the terminal.

## Commands

### Development
- `make test` - Run tests using pytest
- `make build` - Build distribution packages (requires `wheel` package)
- `make clean` - Remove build artifacts from dist/
- `make publish` - Publish to PyPI (requires `twine` package)

### Testing
- `py.test tests/` - Run the test suite
- `tests/coverage-report.sh` - Generate coverage report and open in browser (requires `coverage` package)

### Installation Requirements
- Python 3.7+
- Dependencies: `colorama` (specified in setup.py)
- Test dependencies: `pytest`, `pytest-sugar`

## Architecture

### Core Structure
- `termgraph/termgraph.py` - Main entry point with CLI argument parsing and core graph rendering logic
- `termgraph/module.py` - Object-oriented refactored classes (Data, Args, Chart, HorizontalChart, BarChart)  
- `termgraph/utils.py` - Utility functions for number formatting
- `termgraph/__init__.py` - Package initialization, imports from termgraph module

### Key Components

**termgraph.py** contains the original procedural implementation with:
- CLI argument parsing via `init_args()`
- Data reading from files/stdin via `read_data()`
- Multiple graph types: horizontal bars, vertical bars, stacked, histograms, calendar heatmaps
- Color support using ANSI escape codes
- Normalization and scaling logic

**module.py** contains a refactored OOP approach with:
- `Data` class - Handles data validation, min/max finding, label management
- `Args` class - Manages chart configuration options
- `Chart` base class - Common functionality like normalization and header printing
- `HorizontalChart` and `BarChart` classes - Specific chart implementations

### Data Format
- Input: CSV or space-separated files with labels in first column, numeric data in subsequent columns
- Categories can be specified with lines starting with "@"
- Supports stdin input with filename "-"

### Graph Types
- Horizontal/vertical bar charts
- Multi-variable charts with same or different scales
- Stacked bar charts  
- Histograms with configurable bins
- Calendar heatmaps for date-based data

The codebase shows both the original implementation (termgraph.py) and an in-progress refactor to OOP patterns (module.py), with the main entry point still using the original procedural code.