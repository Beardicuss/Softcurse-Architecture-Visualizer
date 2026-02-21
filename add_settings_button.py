"""Add Settings button to MainWindow.xaml properly"""

xaml_path = r"d:\Projects\In progress\UniversalAnalyzer\ArchitectureVisualizerApp\MainWindow.xaml"

with open(xaml_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if Settings button already exists
if 'settingsButton' in content or 'SETTINGS' in content:
    print("Settings button already exists or file contains SETTINGS")
else:
    # Find the UniformGrid with buttons and add Settings button
    # Look for the visualizeButton and add settingsButton after it
    
    if 'visualizeButton' in content:
        # Find the closing tag of visualizeButton
        visualize_end = content.find('Margin="5,5,0,0"/>', content.find('visualizeButton'))
        
        if visualize_end > 0:
            # Add Settings button after visualizeButton
            settings_button = '''
                                    <Button x:Name="settingsButton"
                                            Content="⚙️ SETTINGS" 
                                            Style="{StaticResource SoftcurseButton}"
                                            Click="Settings_Click"
                                            Margin="5,5,0,0"/>'''
            
            # Insert after the visualizeButton closing tag
            insert_pos = visualize_end + len('Margin="5,5,0,0"/>')
            content = content[:insert_pos] + settings_button + content[insert_pos:]
            
            with open(xaml_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✓ Added Settings button to MainWindow.xaml")
        else:
            print("Could not find visualizeButton margin")
    else:
        print("Could not find visualizeButton in XAML")

print("Done!")
