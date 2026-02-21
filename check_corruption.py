"""Restore MainWindow.xaml.cs from backup and remove visualizeButton reference"""
import shutil

# First, let's check if there's a backup
cs_file = r"d:\Projects\In progress\UniversalAnalyzer\ArchitectureVisualizerApp\MainWindow.xaml.cs"

# Read the corrupted file to see what we have
with open(cs_file, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Current file length: {len(content)} characters")
print(f"Number of lines: {content.count(chr(10))}")

# Check if file is severely corrupted
if len(content) < 10000:
    print("File appears to be severely corrupted (too short)")
    print("Need to restore from a working version")
else:
    print("File length seems reasonable, attempting targeted fix")
