"""Fix MainWindow.xaml.cs lines 193-195 corruption"""

cs_file = r"d:\Projects\In progress\UniversalAnalyzer\ArchitectureVisualizerApp\MainWindow.xaml.cs"

# Read the file
with open(cs_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# The correct replacement for lines 193-195 (indices 192-194)
correct_lines = [
    "                                healthScoreText.Foreground = new System.Windows.Media.SolidColorBrush(\r\n",
    "                                    (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(\"#4CAF50\"));\r\n",
    "                            else if (score >= 60)\r\n",
    "                                healthScoreText.Foreground = new System.Windows.Media.SolidColorBrush(\r\n",
    "                                    (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(\"#FFA500\"));\r\n",
    "                            else\r\n",
    "                                healthScoreText.Foreground = new System.Windows.Media.SolidColorBrush(\r\n",
    "                                    (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString(\"#F44336\"));\r\n",
    "                        }\r\n",
    "                    }\r\n",
    "                }\r\n",
    "                catch { }\r\n",
    "            }\r\n",
    "\r\n",
    "            GenerateVisualization(data);\r\n",
    "            analyzeButton.IsEnabled = true;\r\n",
    "            previewButton.IsEnabled = true;\r\n",
    "        }\r\n",
    "        \r\n",
    "        private void GenerateVisualization(JObject data)\r\n",
    "        {\r\n",
    "            var projectName = currentProjectPath != null ? Path.GetFileName(currentProjectPath) : \"Project\";\r\n",
    "            \r\n",
    "            var jsonFile = Path.Combine(Path.GetTempPath(), $\"data_{Guid.NewGuid()}.json\");\r\n",
    "            File.WriteAllText(jsonFile, data.ToString(), Encoding.UTF8);\r\n",
    "            \r\n",
    "            var cssPath = Path.Combine(pythonScriptsPath, \"ui\", \"static\", \"css\", \"style.css\");\r\n",
    "            var jsPath = Path.Combine(pythonScriptsPath, \"ui\", \"static\", \"js\", \"visualizer.js\");\r\n",
    "            var templatePath = Path.Combine(pythonScriptsPath, \"ui\", \"templates\", \"index.html\");\r\n",
    "            \r\n",
    "            string html;\r\n",
    "            if (File.Exists(templatePath) && File.Exists(cssPath) && File.Exists(jsPath))\r\n",
    "            {\r\n",
    "                html = File.ReadAllText(templatePath);\r\n",
    "                var css = File.ReadAllText(cssPath);\r\n",
    "                var js = File.ReadAllText(jsPath);\r\n",
    "                \r\n",
    "                html = html.Replace(\"{{PROJECT_NAME}}\", projectName);\r\n",
    "                html = html.Replace(\"{{LANG_BADGES}}\", \"\");\r\n",
    "                html = html.Replace(\"{{CSS}}\", css);\r\n",
    "                html = html.Replace(\"{{DATA}}\", File.ReadAllText(jsonFile));\r\n",
    "                html = html.Replace(\"{{JS}}\", js);\r\n",
    "            }\r\n",
    "            else\r\n",
    "            {\r\n",
    "                html = CreateFallbackHTML(projectName, jsonFile);\r\n",
    "            }\r\n",
    "            \r\n",
    "            lastHtmlPath = Path.Combine(Path.GetTempPath(), $\"viz_{Guid.NewGuid()}.html\");\r\n",
    "            File.WriteAllText(lastHtmlPath, html, Encoding.UTF8);\r\n",
    "            \r\n",
    "            if (autoOpenPreview && previewWindow == null)\r\n",
    "                ShowPreviewWindow();\r\n",
    "            \r\n",
    "            UpdatePreviewWindow(html);\r\n",
    "            UpdateAnalysisLog(\"✓ Visualization generated\");\r\n",
    "        }\r\n",
    "        \r\n",
    "        private void UpdatePreviewWindow(string htmlContent)\r\n",
    "        {\r\n",
    "            if (previewWindow != null && previewWindow.IsLoaded)\r\n",
]

# Replace lines 192-194 (indices) with the correct lines
new_lines = lines[:192] + correct_lines + lines[195:]

print(f"Original lines: {len(lines)}")
print(f"New lines: {len(new_lines)}")

# Write back
with open(cs_file, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✓ File fixed!")
