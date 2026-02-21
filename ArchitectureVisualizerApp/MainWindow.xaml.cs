using System;
using System.IO;
using System.Windows;
using System.Diagnostics;
using System.Threading.Tasks;
using System.Linq;
using Newtonsoft.Json.Linq;
using System.Text;

namespace ArchitectureVisualizerApp
{
    public partial class MainWindow : Window
    {
        private string? currentProjectPath;
        private string pythonPath = string.Empty;
        private string pythonScriptsPath = string.Empty;
        private string? lastHtmlPath;
        private PreviewWindow? previewWindow;
        private bool autoOpenPreview = true;
        private Process? apiProcess;

        public MainWindow()
        {
            try
            {
                InitializeComponent();
                Initialize();
                
                var args = App.ParsedArgs;
                if (args != null && (args.AutoAnalyze || !string.IsNullOrEmpty(args.ProjectPath)))
                {
                    ApplyStartupArgs(args);
                }

                Closed += MainWindow_Closed;
            }
            catch (Exception ex)
            {
                MessageBox.Show($"MainWindow Initialization Failed:\n{ex.Message}\nInner: {ex.InnerException?.Message}", "Fatal Error", MessageBoxButton.OK, MessageBoxImage.Error);
                Environment.Exit(1);
            }
        }

        private void Initialize()
        {
            pythonPath = FindPythonExecutable();
            pythonScriptsPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Assets", "Python");

            if (string.IsNullOrEmpty(pythonPath))
            {
                UpdateAnalysisLog("?? Python not found! Please install Python 3.8+");
            }
            else
            {
                UpdateAnalysisLog($"? Python detected: {pythonPath}");
            }
            
            statusText.Text = "Ready";
            UpdateAnalysisLog("Ready - Select a project to begin");
        }

        private void ApplyStartupArgs(StartupArgs args)
        {
            if (!string.IsNullOrEmpty(args.ProjectPath) && Directory.Exists(args.ProjectPath))
            {
                currentProjectPath = args.ProjectPath;
                projectPathText.Text = currentProjectPath;
                analyzeButton.IsEnabled = true;
                statusText.Text = $"Project selected: {Path.GetFileName(currentProjectPath)}";
                UpdateAnalysisLog($"? Project selected: {Path.GetFileName(currentProjectPath)}");
            }

            useCacheCheckbox.IsChecked = args.UseCache;
            profileCheckbox.IsChecked = args.Profile;

            if (args.AutoAnalyze && !string.IsNullOrEmpty(currentProjectPath))
            {
                Loaded += (s, e) => Analyze_Click(this, new RoutedEventArgs());
            }
        }

        private void MainWindow_Closed(object? sender, EventArgs e)
        {
            previewWindow?.Close();
            StopApiServer();
        }

        private void SelectProject_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new Microsoft.Win32.OpenFolderDialog { Title = "Select Project Folder" };

            if (dialog.ShowDialog() == true)
            {
                currentProjectPath = dialog.FolderName;
                projectPathText.Text = currentProjectPath;
                analyzeButton.IsEnabled = true;
                statusText.Text = $"Project selected: {Path.GetFileName(currentProjectPath)}";
                UpdateAnalysisLog($"? Project selected: {Path.GetFileName(currentProjectPath)}");
            }
        }

        private async void Analyze_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(currentProjectPath))
            {
                MessageBox.Show("Please select a project first", "No Project", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            if (string.IsNullOrEmpty(pythonPath))
            {
                MessageBox.Show("Python executable not found!", "Python Not Found", MessageBoxButton.OK, MessageBoxImage.Error);
                return;
            }

            try
            {
                progressBar.Visibility = Visibility.Visible;
                statusText.Text = "Analyzing...";
                analyzeButton.IsEnabled = false;
                
                UpdateAnalysisLog("?? Starting analysis...");
                UpdateAnalysisLog($"?? Scanning: {Path.GetFileName(currentProjectPath)}");

                var jsonResult = await AnalyzeProjectAsync(currentProjectPath);
                var data = JObject.Parse(jsonResult);
                
                UpdateAnalysisLog("? Building dependency graph");
                DisplayResults(data);

                statusText.Text = "Analysis complete!";
                UpdateAnalysisLog("? Analysis complete!");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}", "Analysis Failed", MessageBoxButton.OK, MessageBoxImage.Error);
                statusText.Text = "Analysis failed";
                UpdateAnalysisLog($"? Analysis failed: {ex.Message}");
            }
            finally
            {
                progressBar.Visibility = Visibility.Collapsed;
                analyzeButton.IsEnabled = true;
            }
        }

        private async Task<string> AnalyzeProjectAsync(string projectPath)
        {
            var outputFile = Path.Combine(Path.GetTempPath(), $"analysis_{Guid.NewGuid()}.json");
            var exportScript = Path.Combine(pythonScriptsPath, "export_json.py");
            var useCache = useCacheCheckbox.IsChecked == true ? "--cache" : "";
            var useProfile = profileCheckbox.IsChecked == true ? "--profile" : "";

            var arguments = pythonPath == "py" 
                ? $"-3 \"{exportScript}\" \"{projectPath}\" -o \"{outputFile}\" {useCache} {useProfile}"
                : $"\"{exportScript}\" \"{projectPath}\" -o \"{outputFile}\" {useCache} {useProfile}";

            var startInfo = new ProcessStartInfo
            {
                FileName = pythonPath,
                Arguments = arguments,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                WorkingDirectory = pythonScriptsPath
            };

            using var process = new Process { StartInfo = startInfo };
            var stderrBuilder = new StringBuilder();
            
            // Stream stderr for progress updates AND capture for error reporting
            process.ErrorDataReceived += (s, e) =>
            {
                if (!string.IsNullOrEmpty(e.Data))
                {
                    stderrBuilder.AppendLine(e.Data);
                    Dispatcher.Invoke(() =>
                    {
                        if (e.Data.Contains("[INFO]"))
                            UpdateAnalysisLog(e.Data.Replace("[INFO]", "").Trim());
                        else if (e.Data.Contains("[GPU]"))
                            UpdateAnalysisLog("?? " + e.Data.Replace("[GPU]", "").Trim());
                    });
                }
            };
            
            process.Start();
            process.BeginErrorReadLine();

            // Read stdout to prevent buffer deadlock
            var outputTask = process.StandardOutput.ReadToEndAsync();
            
            // Add 5-minute timeout
            var timeoutTask = Task.Delay(TimeSpan.FromMinutes(5));
            var processTask = process.WaitForExitAsync();
            
            var completedTask = await Task.WhenAny(processTask, timeoutTask);
            if (completedTask == timeoutTask)
            {
                process.Kill();
                throw new TimeoutException("Analysis timed out after 5 minutes. Try reducing max_depth or excluding more directories.");
            }

            await processTask;
            var output = await outputTask;

            if (process.ExitCode != 0)
            {
                var stderr = stderrBuilder.ToString();
                var errorMsg = !string.IsNullOrWhiteSpace(stderr) ? stderr : output;
                
                // Filter for relevant error lines if too long
                if (errorMsg.Length > 1000)
                {
                    var lines = errorMsg.Split('\n');
                    var relevantLines = lines.Where(l => !l.Contains("[INFO]") && !l.Contains("[GPU]")).TakeLast(20);
                    errorMsg = string.Join("\n", relevantLines);
                }
                
                throw new Exception($"Python failed (Exit Code {process.ExitCode}):\n{errorMsg}");
            }

            if (!File.Exists(outputFile))
                throw new Exception("Output file not created");

            return await File.ReadAllTextAsync(outputFile);
        }

        private void DisplayResults(JObject data)
        {
            statsPanel.Visibility = Visibility.Visible;
            
            var metadata = data["metadata"];
            var metrics = data["metrics"];
            var analysis = data["analysis"];

            if (metadata != null)
            {
                totalFilesText.Text = metadata["total_files"]?.ToString() ?? "0";
                var langs = metadata["languages"]?.ToObject<string[]>();
                if (langs != null && langs.Length > 0)
                    languagesText.Text = string.Join(", ", langs);
            }

            if (metrics != null)
            {
                totalLinksText.Text = metrics["total_links"]?.ToString() ?? "0";
            }

            if (analysis != null)
            {
                var healthScore = analysis["health_score"]?.ToString() ?? "N/A";
                var cyclesCount = analysis["cycles"]?["count"]?.ToString() ?? "0";
                var godModulesCount = analysis["god_modules"]?["count"]?.ToString() ?? "0";
                var orphansCount = analysis["orphans"]?["count"]?.ToString() ?? "0";
                
                UpdateAnalysisLog($"?? Architecture Health Score: {healthScore}/100");
                
                if (int.TryParse(cyclesCount, out int cycles) && cycles > 0)
                    UpdateAnalysisLog($"??  Circular Dependencies: {cycles} cycle(s) detected");
                
                if (int.TryParse(godModulesCount, out int godModules) && godModules > 0)
                    UpdateAnalysisLog($"??  God Modules: {godModules} module(s) with >15 connections");
                
                if (int.TryParse(orphansCount, out int orphans) && orphans > 0)
                    UpdateAnalysisLog($"??  Orphaned Modules: {orphans} disconnected module(s)");
                
                try
                {
                    if (healthScoreText != null)
                    {
                        healthScoreText.Text = healthScore;
                        
                        if (int.TryParse(healthScore, out int score))
                        {
                            if (score >= 80)
                                healthScoreText.Foreground = new System.Windows.Media.SolidColorBrush(
                                    (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#4CAF50"));
                            else if (score >= 60)
                                healthScoreText.Foreground = new System.Windows.Media.SolidColorBrush(
                                    (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#FFA500"));
                            else
                                healthScoreText.Foreground = new System.Windows.Media.SolidColorBrush(
                                    (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#F44336"));
                        }
                    }
                }
                catch { }
            }

            GenerateVisualization(data);
            analyzeButton.IsEnabled = true;
            previewButton.IsEnabled = true;
        }
        
        private void GenerateVisualization(JObject data)
        {
            var projectName = currentProjectPath != null ? Path.GetFileName(currentProjectPath) : "Project";
            
            var jsonFile = Path.Combine(Path.GetTempPath(), $"data_{Guid.NewGuid()}.json");
            File.WriteAllText(jsonFile, data.ToString(), Encoding.UTF8);
            
            var cssPath = Path.Combine(pythonScriptsPath, "ui", "static", "css", "style.css");
            var jsPath = Path.Combine(pythonScriptsPath, "ui", "static", "js", "visualizer.js");
            var templatePath = Path.Combine(pythonScriptsPath, "ui", "templates", "index.html");
            
            string html;
            if (File.Exists(templatePath) && File.Exists(cssPath) && File.Exists(jsPath))
            {
                html = File.ReadAllText(templatePath);
                var css = File.ReadAllText(cssPath);
                var js = File.ReadAllText(jsPath);
                
                html = html.Replace("{{PROJECT_NAME}}", projectName);
                html = html.Replace("{{LANG_BADGES}}", "");
                html = html.Replace("{{CSS}}", css);
                html = html.Replace("{{DATA}}", File.ReadAllText(jsonFile));
                html = html.Replace("{{JS}}", js);
            }
            else
            {
                html = CreateFallbackHTML(projectName, jsonFile);
            }
            
            lastHtmlPath = Path.Combine(Path.GetTempPath(), $"viz_{Guid.NewGuid()}.html");
            File.WriteAllText(lastHtmlPath, html, Encoding.UTF8);
            
            if (autoOpenPreview && previewWindow == null)
                ShowPreviewWindow();
            
            UpdatePreviewWindow(html);
            UpdateAnalysisLog("? Visualization generated");
        }
        
        private void UpdatePreviewWindow(string htmlContent)
        {
            if (previewWindow != null && previewWindow.IsLoaded)
                previewWindow.UpdateContent(htmlContent);
        }
        
        private void ShowPreviewWindow()
        {
            if (previewWindow == null || !previewWindow.IsLoaded)
            {
                previewWindow = new PreviewWindow();
                
                previewWindow.HoverElement += (s, htmlSnippet) => Debug.WriteLine($"Preview hover: {htmlSnippet}");
                previewWindow.ClickElement += (s, htmlSnippet) => Debug.WriteLine($"Preview click: {htmlSnippet}");
                previewWindow.Closed += (s, e) =>
                {
                    previewWindow = null;
                    previewButton.Content = "??? PREVIEW";
                };
                
                previewWindow.Show();
                previewButton.Content = "??? HIDE";
                UpdateAnalysisLog("? Preview window opened");
                
                // Reload content if available
                if (!string.IsNullOrEmpty(lastHtmlPath) && File.Exists(lastHtmlPath))
                {
                    try
                    {
                        var html = File.ReadAllText(lastHtmlPath);
                        UpdatePreviewWindow(html);
                    }
                    catch (Exception ex)
                    {
                        Debug.WriteLine($"Failed to reload preview: {ex.Message}");
                    }
                }
            }
            else
            {
                previewWindow.Activate();
            }
        }
        
        private void Preview_Click(object sender, RoutedEventArgs e)
        {
            if (previewWindow == null || !previewWindow.IsLoaded)
                ShowPreviewWindow();
            else
            {
                previewWindow.Close();
                previewWindow = null;
                previewButton.Content = "??? PREVIEW";
            }
        }
        
        private void UpdateAnalysisLog(string message)
        {
            var timestamp = DateTime.Now.ToString("HH:mm:ss");
            var currentLog = analysisLogText.Text;
            
            if (string.IsNullOrEmpty(currentLog) || currentLog == "Ready - Select a project to begin")
                analysisLogText.Text = $"[{timestamp}] {message}";
            else
                analysisLogText.Text = $"{currentLog}\n[{timestamp}] {message}";
        }
        
        private string CreateFallbackHTML(string projectName, string jsonFile)
        {
            var sb = new StringBuilder();
            sb.AppendLine("<!DOCTYPE html><html><head><meta charset='UTF-8'>");
            sb.AppendLine($"<title>{projectName}</title>");
            sb.AppendLine("<style>body{margin:0;background:#020617;color:#e2e8f0;font-family:Consolas,monospace;}</style>");
            sb.AppendLine("</head><body>");
            sb.AppendLine("<div id='graph' style='width:100vw;height:100vh;'></div>");
            sb.AppendLine("<script src='https://d3js.org/d3.v7.min.js'></script>");
            sb.AppendLine("<script>");
            sb.AppendLine($"fetch('{jsonFile.Replace("\\", "/")}').then(r=>r.json()).then(data=>{{");
            sb.AppendLine("const w=window.innerWidth,h=window.innerHeight;");
            sb.AppendLine("const svg=d3.select('#graph').append('svg').attr('width',w).attr('height',h);");
            sb.AppendLine("const g=svg.append('g');");
            sb.AppendLine("svg.call(d3.zoom().on('zoom',e=>g.attr('transform',e.transform)));");
            sb.AppendLine("const sim=d3.forceSimulation(data.nodes).force('link',d3.forceLink(data.links).id(d=>d.id)).force('charge',d3.forceManyBody().strength(-300)).force('center',d3.forceCenter(w/2,h/2));");
            sb.AppendLine("const link=g.append('g').selectAll('line').data(data.links).join('line').attr('stroke','#334155');");
            sb.AppendLine("const node=g.append('g').selectAll('circle').data(data.nodes).join('circle').attr('r',5).attr('fill','#38bdf8');");
            sb.AppendLine("sim.on('tick',()=>{link.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y).attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);node.attr('cx',d=>d.x).attr('cy',d=>d.y);});");
            // Add resize listener
            sb.AppendLine("window.addEventListener('resize', () => {");
            sb.AppendLine("  const w = window.innerWidth;");
            sb.AppendLine("  const h = window.innerHeight;");
            sb.AppendLine("  svg.attr('width', w).attr('height', h);");
            sb.AppendLine("  sim.force('center', d3.forceCenter(w / 2, h / 2));");
            sb.AppendLine("  sim.alpha(0.3).restart();");
            sb.AppendLine("});");
            sb.AppendLine("});");
            sb.AppendLine("</script></body></html>");
            return sb.ToString();
        }

        private string FindPythonExecutable()
        {
            try
            {
                var pyStartInfo = new ProcessStartInfo
                {
                    FileName = "py",
                    Arguments = "-3 --version",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    CreateNoWindow = true
                };

                using var pyProcess = Process.Start(pyStartInfo);
                if (pyProcess != null)
                {
                    pyProcess.WaitForExit();
                    if (pyProcess.ExitCode == 0)
                        return "py";
                }
            }
            catch { }

            var paths = new[]
            {
                @"C:\Users\DanTe\Desktop\Graph_separated\venv\Scripts\python.exe",
                @"C:\Python312\python.exe",
                @"C:\Python311\python.exe",
                @"C:\Python310\python.exe"
            };

            foreach (var path in paths)
                if (File.Exists(path)) return path;

            try
            {
                var startInfo = new ProcessStartInfo
                {
                    FileName = "where",
                    Arguments = "python",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    CreateNoWindow = true
                };

                using var process = Process.Start(startInfo);
                if (process != null)
                {
                    var output = process.StandardOutput.ReadToEnd();
                    process.WaitForExit();
                    if (process.ExitCode == 0 && !string.IsNullOrWhiteSpace(output))
                        return output.Split('\n')[0].Trim();
                }
            }
            catch { }
            
            return string.Empty;
        }

        private void StartApiServer()
        {
            try
            {
                var apiScript = Path.Combine(pythonScriptsPath, "api_server.py");
                
                var startInfo = new ProcessStartInfo
                {
                    FileName = pythonPath,
                    Arguments = pythonPath == "py" ? $"-3 \"{apiScript}\"" : $"\"{apiScript}\"",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true,
                    WorkingDirectory = pythonScriptsPath
                };

                apiProcess = new Process { StartInfo = startInfo };
                apiProcess.Start();
                
                apiServerButton.Content = "STOP API";
                apiStatusIndicator.Fill = new System.Windows.Media.SolidColorBrush(
                    (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#4CAF50"));
                apiStatusText.Text = "ONLINE";
                apiStatusText.Foreground = new System.Windows.Media.SolidColorBrush(
                    (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#4CAF50"));
                
                UpdateAnalysisLog("? API Server started on port 5000");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to start API server: {ex.Message}");
                apiServerButton.IsChecked = false;
            }
        }

        private void StopApiServer()
        {
            try
            {
                if (apiProcess != null && !apiProcess.HasExited)
                {
                    apiProcess.Kill();
                    apiProcess = null;
                }

                apiServerButton.Content = "START API";
                apiStatusIndicator.Fill = new System.Windows.Media.SolidColorBrush(
                    (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#333333"));
                apiStatusText.Text = "OFFLINE";
                apiStatusText.Foreground = new System.Windows.Media.SolidColorBrush(
                    (System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#666666"));
                
                UpdateAnalysisLog("?? API Server stopped");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Error stopping API server: {ex.Message}");
            }
        }

        private void ApiServer_Click(object sender, RoutedEventArgs e)
        {
            if (apiServerButton.IsChecked == true)
            {
                StartApiServer();
            }
            else
            {
                StopApiServer();
            }
        }

        private void Settings_Click(object sender, RoutedEventArgs e)
        {
            var settingsWindow = new SettingsWindow();
            settingsWindow.Owner = this;
            settingsWindow.ShowDialog();
        }

        private void Minimize_Click(object sender, RoutedEventArgs e)
        {
            WindowState = WindowState.Minimized;
        }

        private void Maximize_Click(object sender, RoutedEventArgs e)
        {
            WindowState = WindowState == WindowState.Maximized ? WindowState.Normal : WindowState.Maximized;
        }

        private void Close_Click(object sender, RoutedEventArgs e)
        {
            StopApiServer();
            Close();
        }
}

}
