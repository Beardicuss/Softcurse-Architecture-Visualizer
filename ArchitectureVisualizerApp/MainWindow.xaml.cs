using System;
using System.IO;
using System.Windows;
using Microsoft.Web.WebView2.Core;

namespace ArchitectureVisualizerApp
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();

            // Set window icon from file (avoids XAML pack URI issues)
            var iconPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Assets", "ui", "arch.ico");
            if (File.Exists(iconPath))
            {
                Icon = new System.Windows.Media.Imaging.BitmapImage(new Uri(iconPath, UriKind.Absolute));
            }

            InitializeWebView();
        }

        private async void InitializeWebView()
        {
            try
            {
                // Initialize WebView2 with environment options to allow mixed content (HTTPS -> HTTP)
                var options = new CoreWebView2EnvironmentOptions { AdditionalBrowserArguments = "--allow-running-insecure-content" };
                var userDataFolder = Path.Combine(Path.GetTempPath(), "SoftcurseVisualizer");
                var env = await CoreWebView2Environment.CreateAsync(null, userDataFolder, options);
                await webView.EnsureCoreWebView2Async(env);

                // Configure WebView2 settings
                var settings = webView.CoreWebView2.Settings;
                settings.AreDevToolsEnabled = true;
                settings.IsStatusBarEnabled = false;
                settings.AreDefaultContextMenusEnabled = false;

                // Set transparent background
                webView.DefaultBackgroundColor = System.Drawing.Color.FromArgb(0, 2, 2, 2);

                // Set required headers for SharedArrayBuffer (LadybugDB WASM needs this)
                webView.CoreWebView2.WebResourceResponseReceived += (s, e) => { };

                // Navigate to the built Vite app
                var distPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Assets", "WebApp", "dist");
                var indexPath = Path.Combine(distPath, "index.html");

                if (File.Exists(indexPath))
                {
                    // Use virtual host mapping for proper CORS and module loading
                    webView.CoreWebView2.SetVirtualHostNameToFolderMapping(
                        "softcurse.local",
                        distPath,
                        CoreWebView2HostResourceAccessKind.Allow);

                    webView.CoreWebView2.Navigate("https://softcurse.local/index.html");
                }
                else
                {
                    // Fallback message
                    webView.CoreWebView2.NavigateToString(@"
                        <html>
                        <body style='background:#020202;color:#0ff;font-family:Consolas;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;'>
                            <div style='text-align:center;'>
                                <h1 style='color:#0ff;text-shadow:0 0 20px #08f;'>SOFTCURSE VISUALIZER</h1>
                                <p style='color:#08f;'>Web app not found. Run <code style='color:#0ff;'>npm run build</code> in Assets/WebApp/</p>
                                <p style='color:#555;font-size:12px;'>Expected: " + indexPath.Replace("\\", "\\\\") + @"</p>
                            </div>
                        </body>
                        </html>");
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to initialize WebView2:\n{ex.Message}", 
                    "WebView2 Error", MessageBoxButton.OK, MessageBoxImage.Error);
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
            webView?.Dispose();
            Close();
        }
    }
}
