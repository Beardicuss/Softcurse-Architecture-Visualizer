"""Fix UpdatePreviewWindow method completion"""

cs_file = r"d:\Projects\In progress\UniversalAnalyzer\ArchitectureVisualizerApp\MainWindow.xaml.cs"

# Read the file
with open(cs_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix lines 251-254 - complete the UpdatePreviewWindow method
# Replace lines 251-254 (indices 250-253) with the correct implementation
correct_lines = [
    "        private void UpdatePreviewWindow(string htmlContent)\r\n",
    "        {\r\n",
    "            if (previewWindow != null && previewWindow.IsLoaded)\r\n",
    "                previewWindow.UpdateContent(htmlContent);\r\n",
    "        }\r\n",
    "        \r\n",
]

# Replace lines 250-253 with correct lines
new_lines = lines[:250] + correct_lines + lines[254:]

print(f"Original lines: {len(lines)}")
print(f"New lines: {len(new_lines)}")

# Write back
with open(cs_file, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✓ UpdatePreviewWindow method fixed!")
