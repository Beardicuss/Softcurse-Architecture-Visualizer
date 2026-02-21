using System;
using System.IO;
using System.Linq;
using System.Windows;
using System.Collections.Generic;
using Microsoft.Win32;

namespace ArchitectureVisualizerApp
{
    public partial class SettingsWindow : Window
    {
        private string? configFilePath;
        
        public SettingsWindow()
        {
            InitializeComponent();
            LoadDefaultSettings();
        }
        
        private void LoadDefaultSettings()
        {
            // Default exclude directories
            var defaultExcludes = new[]
            {
                "venv",
                ".venv",
                "env",
                "node_modules",
                ".git",
                "__pycache__",
                "build",
                "dist",
                "target",
                "bin",
                "obj",
                "packages",
                ".vs",
                ".idea",
                ".vscode"
            };
            
            excludeDirsTextBox.Text = string.Join(Environment.NewLine, defaultExcludes);
            maxDepthTextBox.Text = "10";
            cacheEnabledCheckBox.IsChecked = true;
            profilingEnabledCheckBox.IsChecked = false;
            enableLanguageFilterCheckBox.IsChecked = false;
        }
        
        private void EnableLanguageFilter_Checked(object sender, RoutedEventArgs e)
        {
            languageFilterTextBox.IsEnabled = true;
        }
        
        private void EnableLanguageFilter_Unchecked(object sender, RoutedEventArgs e)
        {
            languageFilterTextBox.IsEnabled = false;
            languageFilterTextBox.Text = "";
        }
        
        private void LoadConfig_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new OpenFileDialog
            {
                Title = "Load Configuration File",
                Filter = "YAML Files (*.yml;*.yaml)|*.yml;*.yaml|All Files (*.*)|*.*",
                DefaultExt = ".yml"
            };
            
            if (dialog.ShowDialog() == true)
            {
                try
                {
                    configFilePath = dialog.FileName;
                    LoadConfigFromFile(configFilePath);
                    MessageBox.Show($"Configuration loaded from:\n{configFilePath}", 
                                  "Success", 
                                  MessageBoxButton.OK, 
                                  MessageBoxImage.Information);
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Failed to load configuration:\n{ex.Message}", 
                                  "Error", 
                                  MessageBoxButton.OK, 
                                  MessageBoxImage.Error);
                }
            }
        }
        
        private void LoadConfigFromFile(string filePath)
        {
            // Simple YAML parser for our config format
            var lines = File.ReadAllLines(filePath);
            var excludeDirs = new List<string>();
            var languages = new List<string>();
            bool inExcludeSection = false;
            bool inLanguageSection = false;
            
            foreach (var line in lines)
            {
                var trimmed = line.Trim();
                
                // Skip comments and empty lines
                if (trimmed.StartsWith("#") || string.IsNullOrWhiteSpace(trimmed))
                    continue;
                
                // Check for sections
                if (trimmed == "exclude_dirs:")
                {
                    inExcludeSection = true;
                    inLanguageSection = false;
                    continue;
                }
                else if (trimmed == "languages:")
                {
                    inLanguageSection = true;
                    inExcludeSection = false;
                    continue;
                }
                else if (trimmed.StartsWith("max_depth:"))
                {
                    var value = trimmed.Split(':')[1].Trim();
                    maxDepthTextBox.Text = value;
                    inExcludeSection = false;
                    inLanguageSection = false;
                    continue;
                }
                else if (trimmed.Contains(":") && !trimmed.StartsWith("-"))
                {
                    // New section started
                    inExcludeSection = false;
                    inLanguageSection = false;
                    
                    // Check for performance settings
                    if (trimmed.StartsWith("cache_enabled:"))
                    {
                        var value = trimmed.Split(':')[1].Trim().ToLower();
                        cacheEnabledCheckBox.IsChecked = value == "true";
                    }
                    else if (trimmed.StartsWith("profiling:"))
                    {
                        var value = trimmed.Split(':')[1].Trim().ToLower();
                        profilingEnabledCheckBox.IsChecked = value == "true";
                    }
                    continue;
                }
                
                // Parse list items
                if (trimmed.StartsWith("-"))
                {
                    var value = trimmed.Substring(1).Trim();
                    if (inExcludeSection)
                        excludeDirs.Add(value);
                    else if (inLanguageSection)
                        languages.Add(value);
                }
            }
            
            // Update UI
            if (excludeDirs.Any())
                excludeDirsTextBox.Text = string.Join(Environment.NewLine, excludeDirs);
            
            if (languages.Any())
            {
                enableLanguageFilterCheckBox.IsChecked = true;
                languageFilterTextBox.Text = string.Join(Environment.NewLine, languages);
            }
        }
        
        private void Save_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                // Validate max depth
                if (!int.TryParse(maxDepthTextBox.Text, out int maxDepth) || maxDepth < 1 || maxDepth > 100)
                {
                    MessageBox.Show("Maximum depth must be between 1 and 100\n\nNote: This is directory nesting level (e.g., src/core/utils = 3), not file count.\nMost projects need 10-20 levels.", 
                                  "Validation Error", 
                                  MessageBoxButton.OK, 
                                  MessageBoxImage.Warning);
                    return;
                }
                
                // Ask where to save
                var dialog = new SaveFileDialog
                {
                    Title = "Save Configuration File",
                    Filter = "YAML Files (*.yml)|*.yml|All Files (*.*)|*.*",
                    DefaultExt = ".yml",
                    FileName = ".visualizer.yml"
                };
                
                if (dialog.ShowDialog() == true)
                {
                    SaveConfigToFile(dialog.FileName);
                    configFilePath = dialog.FileName;
                    
                    MessageBox.Show($"Configuration saved to:\n{dialog.FileName}\n\nPlace this file in your project root to use it automatically.", 
                                  "Success", 
                                  MessageBoxButton.OK, 
                                  MessageBoxImage.Information);
                    
                    DialogResult = true;
                    Close();
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to save configuration:\n{ex.Message}", 
                              "Error", 
                              MessageBoxButton.OK, 
                              MessageBoxImage.Error);
            }
        }
        
        private void SaveConfigToFile(string filePath)
        {
            using var writer = new StreamWriter(filePath);
            
            writer.WriteLine("# Architecture Visualizer Configuration");
            writer.WriteLine("# Generated: " + DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"));
            writer.WriteLine();
            
            // Exclude directories
            writer.WriteLine("# Directories to exclude from analysis");
            writer.WriteLine("exclude_dirs:");
            var excludeDirs = excludeDirsTextBox.Text
                .Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries)
                .Select(d => d.Trim())
                .Where(d => !string.IsNullOrWhiteSpace(d));
            
            foreach (var dir in excludeDirs)
            {
                writer.WriteLine($"  - {dir}");
            }
            writer.WriteLine();
            
            // Max depth
            writer.WriteLine("# Maximum directory depth to scan");
            writer.WriteLine($"max_depth: {maxDepthTextBox.Text}");
            writer.WriteLine();
            
            // Language filter
            if (enableLanguageFilterCheckBox.IsChecked == true && !string.IsNullOrWhiteSpace(languageFilterTextBox.Text))
            {
                writer.WriteLine("# Languages to analyze (remove this section to analyze all)");
                writer.WriteLine("languages:");
                var languages = languageFilterTextBox.Text
                    .Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries)
                    .Select(l => l.Trim())
                    .Where(l => !string.IsNullOrWhiteSpace(l));
                
                foreach (var lang in languages)
                {
                    writer.WriteLine($"  - {lang}");
                }
                writer.WriteLine();
            }
            
            // Performance settings
            writer.WriteLine("# Performance settings");
            writer.WriteLine("performance:");
            writer.WriteLine($"  cache_enabled: {(cacheEnabledCheckBox.IsChecked == true ? "true" : "false")}");
            writer.WriteLine($"  profiling: {(profilingEnabledCheckBox.IsChecked == true ? "true" : "false")}");
        }
        
        private void Cancel_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
            Close();
        }
    }
}
