# Softcurse Architecture Visualizer - User Guide

This guide explains how to effectively use the visualizer to explore and diagnose your code structural dependencies.

## 1. Getting Started

1. Open **ArchitectureVisualizerApp.exe**.
2. Click **📁 SELECT** in the PROJECT CONTROL panel.
3. Browse to the root of your application (e.g., `C:/Src/MyProject`).
4. Wait for the file-discovery stats to appear in the log.

## 2. Running an Analysis

You have two methods to run an analysis:

### Quick Analysis (Recommended)
Click **🔍 ANALYZE**. The application will launch a background Python process using `export_json.py`, track its progress via standard error, and output `analysis_<guid>.json` into your Temp folder.

### API Mode (For remote hosts or detached servers)
Click **START API**. This launches `api_server.py` as a local Flask instance on port `5000`. You can then hit the analyze endpoint asynchronously without freezing your local UI thread.

## 3. Controlling Performance

If your project is huge (1000+ files), analysis can take minutes.
- **Use Cache**: Keeps an incremental abstract syntax tree of previous runs. Only re-parses modified files.
- **Profile Analysis**: Check this to output `cProfile` statistics into the user console block. It benchmarks all AST components.

## 4. Visualizing Data

After analyzing, hit **👁️ PREVIEW**.
You will be greeted with an interactive D3.js/Vis.js node graph.
- **Zoom / Pan**: Scroll your mouse wheel or drag the canvas.
- **Drag Nodes**: Left click and drag any architectural node.
- **Filters**: On the left panel, you can filter by `Language` (e.g., Hide all `XML` config files).
- **Edge Weight**: Edges denote imports. Thicker edges indicate stronger coupling between those two files.
- **Isolates**: Check "Hide Isolated Nodes" to remove files that import nothing and are imported by nothing.

## 5. Interpreting Metrics & Health

The metrics panel will highlight your architecture score out of 100.
- **Green (80-100)**: Excellent modularity. Few cyclic imports. High separation of concerns.
- **Orange (50-79)**: Warning. Start refactoring tight couplings.
- **Red (0-49)**: Danger. You likely have massive "God Modules" or widespread cycle loops. The log will explicitly name your God Modules (files with 10+ dependents).

## 6. Advanced Configuration

Click **⚙️ SETTINGS** to manually adjust the `.visualizer.yml` rulebook.
You can:
- Increase or decrease maximum nested folder depth limits.
- Add folders to `exclude_dirs` (e.g., `node_modules`, `bin`, `.git`).
- Exclude file extensions from AST parsing.
