"""Complete fix for MainWindow.xaml - restore missing button section"""

xaml_path = r"d:\Projects\In progress\UniversalAnalyzer\ArchitectureVisualizerApp\MainWindow.xaml"

with open(xaml_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the corrupted section (around line 148-152)
# Look for the Border with FontFamily (which is wrong)
for i, line in enumerate(lines):
    if 'FontFamily="Consolas"' in line and 'FontSize="10"' in lines[i+1] if i+1 < len(lines) else False:
        if 'Border Background="#050308"' in lines[i-4] if i >= 4 else False:
            print(f"Found corrupted section at line {i+1}")
            
            # Replace lines 144-151 with the correct content
            correct_section = '''                                <Border Background="#050308" 
                                        BorderBrush="#9D4EDD" 
                                        BorderThickness="1" 
                                        CornerRadius="4" 
                                        Padding="12,8"
                                        Margin="0,0,0,15">
                                    <TextBlock x:Name="projectPathText" 
                                               Text="No project selected" 
                                               FontFamily="Consolas"
                                               FontSize="10"
                                               Foreground="#E8DCFF"
                                               TextWrapping="Wrap"/>
                                </Border>

                                <!-- Action Buttons -->
                                <UniformGrid Rows="2" Columns="2" Margin="0,15,0,0">
                                    <Button Content="📁 SELECT" 
                                            Style="{StaticResource SoftcurseButton}"
                                            Click="SelectProject_Click"
                                            Margin="0,0,5,5"/>
                                    <Button x:Name="analyzeButton"
                                            Content="🔍 ANALYZE" 
                                            Style="{StaticResource SoftcurseButton}"
                                            IsEnabled="False"
                                            Click="Analyze_Click"
                                            Margin="5,0,0,5"/>
                                    <Button x:Name="previewButton"
                                            Content="👁️ PREVIEW" 
                                            Style="{StaticResource SoftcurseButton}"
                                            IsEnabled="False"
                                            Click="Preview_Click"
                                            Margin="0,5,5,0"/>
                                    <Button x:Name="settingsButton"
                                            Content="⚙️ SETTINGS" 
                                            Style="{StaticResource SoftcurseButton}"
                                            Click="Settings_Click"
                                            Margin="5,5,0,0"/>
                                </UniformGrid>

                                <!-- Cache Option -->
                                <CheckBox x:Name="useCacheCheckbox"
                                          Content="Use Cache" 
                                          IsChecked="True"
                                          Foreground="#E8DCFF"
                                          FontFamily="Consolas"
                                          FontSize="10"
                                          Margin="0,15,0,0"/>
'''
            
            # Replace from line i-4 to i+2 (the corrupted section)
            start_line = i - 4
            end_line = i + 2
            
            new_lines = lines[:start_line] + [correct_section] + lines[end_line:]
            
            with open(xaml_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            print(f"✓ Fixed MainWindow.xaml - replaced lines {start_line+1} to {end_line+1}")
            print("✓ Added Settings button")
            break
else:
    print("Could not find the corrupted section")
