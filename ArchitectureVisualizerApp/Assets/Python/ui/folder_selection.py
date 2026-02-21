"""
Folder selection UI components for GUI and console.
"""

import json
import tkinter as tk
from tkinter import filedialog
from pathlib import Path


# -------------------------------------------------------------------
# UI: FOLDER SELECTION
# -------------------------------------------------------------------

def select_folder_gui():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    folder_path = filedialog.askdirectory(
        title="Select Project Folder to Analyze",
        mustexist=True
    )

    root.destroy()
    return folder_path


def select_folder_console():
    print("\n" + "=" * 70)
    print("PROJECT ARCHITECTURE VISUALIZER - FOLDER SELECTION")
    print("=" * 70)

    recent_file = Path.home() / ".arch_visualizer_recent.json"
    recent_projects = []

    if recent_file.exists():
        try:
            with recent_file.open('r', encoding="utf-8") as f:
                recent_projects = json.load(f)
        except Exception:
            pass

    print("\nOptions:")
    print("  1. Enter folder path manually")
    print("  2. Use GUI folder picker")

    if recent_projects:
        print("  3. Select from recent projects:")
        for i, proj in enumerate(recent_projects[:5], 1):
            print(f"     {i}. {proj}")

    print("\n" + "=" * 70)
    choice = input("\nYour choice (1/2" + ("/3" if recent_projects else "") + "): ").strip()

    if choice == "1":
        path = input("\nEnter full path to project folder: ").strip().strip('"').strip("'")
        return path
    elif choice == "2":
        return select_folder_gui()
    elif choice == "3" and recent_projects:
        proj_choice = input(f"\nSelect project (1-{min(5, len(recent_projects))}): ").strip()
        try:
            idx = int(proj_choice) - 1
            if 0 <= idx < min(5, len(recent_projects)):
                return recent_projects[idx]
        except Exception:
            pass
        print("[ERROR] Invalid selection")
        return None
    else:
        print("[ERROR] Invalid choice")
        return None


def save_recent_project(project_path):
    recent_file = Path.home() / ".arch_visualizer_recent.json"
    recent_projects = []

    if recent_file.exists():
        try:
            with recent_file.open('r', encoding="utf-8") as f:
                recent_projects = json.load(f)
        except Exception:
            pass

    project_path = str(project_path)
    if project_path in recent_projects:
        recent_projects.remove(project_path)
    recent_projects.insert(0, project_path)
    recent_projects = recent_projects[:10]

    try:
        with recent_file.open('w', encoding="utf-8") as f:
            json.dump(recent_projects, f, indent=2)
    except Exception:
        pass
