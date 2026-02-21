# Softcurse Architecture Visualizer

A powerful, hybrid WPF/Python application that analyzes and visualizes codebase architectures across multiple languages (C#, Python, JavaScript, XML, XAML). Features GPU-accelerated node layouts, real-time dependency tracking, cycle detection, and interactive UI.

## Features

- **Multi-Language Support**: Automatically scans `.cs`, `.py`, `.js`, `.xaml`, and `.xml`.
- **Advanced Architecture Analysis**:
  - Automatically identifies "God Modules" (modules with excessively high in/out degree).
  - Detects architectural cycles and cyclic dependencies.
  - Computes global health and maintainability scores.
- **GPU Acceleration**: Utilizes PyTorch (CUDA/ROCm) if available to compute complex force-directed graph layouts thousands of times faster than CPU alone. Falls back to highly optimized CPU threading.
- **Background API Server**: A standalone Flask API (`api_server.py`) offloads heavy JSON generation from the main UI thread.
- **Interactive Visualizer**: Custom Javascript DAG implementation allowing user interactions, filters, language grouping, and node searches.
- **Configuration Engine**: Use `.visualizer.yml` to set project-specific ignore directories, deep exclusion rules, and limits.
- **Performance Profiling**: Built-in `cProfile` hooks to benchmark file I/O operations and build optimization strategies directly mapped to the UI logs.

## Quick Start

1. **Launch the Application**: Run `ArchitectureVisualizerApp.exe`.
2. **Select Project**: Click `📁 SELECT` to pick a source code directory.
3. **Analyze**: Click `🔍 ANALYZE` or optionally start the API server with `START API`.
4. **Preview**: After the JSON is generated, the `👁️ PREVIEW` button opens the interactive graph map.
5. **Observe Logs**: The metrics panel automatically updates with file counts, isolated modules, graph cycles, and the global architecture health score.

## Command Line Interface

You can launch the visualizer directly from your terminal or CI/CD pipelines to pre-load configurations.

```powershell
# Auto-select a project, disable cache, enable profiling, and automatically trigger analysis
.\ArchitectureVisualizerApp.exe --path "C:\Code\MyProject" --no-cache --profile --auto-analyze
```

### Supported Flags:
- `--path <dir>`: Pre-load a project directory.
- `--cache`: Use incremental AST caching (Default).
- `--no-cache`: Force a complete structural re-evaluation of every file.
- `--profile`: Output raw `cProfile` stats into the application analysis log.
- `--auto-analyze`: Begin architecture scanning immediately upon application startup.

## Requirements

The WPF Application manages its own local Python instance for analysis. If you wish to use the GPU layout accelerator, ensure you have PyTorch installed:

- NVIDIA: `pip install torch`
- AMD: `pip install torch-rocm`

Otherwise, standard compilation requires the included `Assets/Python/requirements.txt` which bundles `Flask`, `PyYAML`, and standard AST parsers.

## License

Softcurse Proprietary - All Rights Reserved.
