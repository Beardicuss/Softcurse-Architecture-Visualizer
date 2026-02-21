"""Carefully fix MainWindow.xaml.cs by removing visualizeButton reference"""

cs_file = r"d:\Projects\In progress\UniversalAnalyzer\ArchitectureVisualizerApp\MainWindow.xaml.cs"

# Read the file
with open(cs_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Find and remove the visualizeButton line
new_lines = []
removed_count = 0

for i, line in enumerate(lines):
    # Skip lines that reference visualizeButton
    if 'visualizeButton' in line:
        print(f"Removing line {i+1}: {line.strip()}")
        removed_count += 1
        continue
    new_lines.append(line)

print(f"Removed {removed_count} lines")
print(f"New line count: {len(new_lines)}")

# Write back
with open(cs_file, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✓ File fixed!")
