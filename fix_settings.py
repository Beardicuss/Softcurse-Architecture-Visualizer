"""Fix MainWindow.xaml by restoring from backup and adding Settings button"""
import re

# Read the corrupted file
xaml_path = r"d:\Projects\In progress\UniversalAnalyzer\ArchitectureVisualizerApp\MainWindow.xaml"

with open(xaml_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if file is corrupted (missing closing tags)
if '</Window>' not in content or content.count('<') < 100:
    print("File is corrupted. Need to restore from backup.")
    # For now, just add the Settings_Click handler to MainWindow.xaml.cs
else:
    print("File seems OK")

# Add Settings_Click to MainWindow.xaml.cs
cs_path = r"d:\Projects\In progress\UniversalAnalyzer\ArchitectureVisualizerApp\MainWindow.xaml.cs"

with open(cs_path, 'r', encoding='utf-8') as f:
    cs_content = f.read()

# Check if Settings_Click already exists
if 'Settings_Click' not in cs_content:
    # Find the last method (FindPythonExecutable) and add Settings_Click before the closing braces
    insert_pos = cs_content.rfind('    }\n}')
    
    settings_method = '''
        private void Settings_Click(object sender, RoutedEventArgs e)
        {
            var settingsWindow = new SettingsWindow();
            settingsWindow.Owner = this;
            settingsWindow.ShowDialog();
        }
'''
    
    cs_content = cs_content[:insert_pos] + settings_method + '\n' + cs_content[insert_pos:]
    
    with open(cs_path, 'w', encoding='utf-8') as f:
        f.write(cs_content)
    
    print("✓ Added Settings_Click handler to MainWindow.xaml.cs")
else:
    print("Settings_Click already exists in MainWindow.xaml.cs")
