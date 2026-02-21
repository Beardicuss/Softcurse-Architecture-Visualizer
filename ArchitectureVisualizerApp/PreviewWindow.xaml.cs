using System;
using System.IO;
using System.Text;
using System.Windows;
using System.Windows.Media.Animation;
using Microsoft.Web.WebView2.Core;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace ArchitectureVisualizerApp
{
    public partial class PreviewWindow : Window
    {
        private string previewHtmlTemplate = string.Empty;
        private bool isWebViewReady = false;

        public event EventHandler<string>? HoverElement;
        public event EventHandler<string>? ClickElement;

        public PreviewWindow()
        {
            InitializeComponent();
            InitializeAsync();
            
            // Pulsing animation for status dot
            var pulseAnimation = new DoubleAnimation
            {
                From = 1.0,
                To = 0.3,
                Duration = TimeSpan.FromSeconds(1.4),
                AutoReverse = true,
                RepeatBehavior = RepeatBehavior.Forever
            };
            statusDot.BeginAnimation(OpacityProperty, pulseAnimation);
        }

        private async void InitializeAsync()
        {
            try
            {
                await webView.EnsureCoreWebView2Async();
                
                // Enable JavaScript and allow local content - CRITICAL for D3.js visualization
                webView.CoreWebView2.Settings.IsScriptEnabled = true;
                webView.CoreWebView2.Settings.AreDefaultScriptDialogsEnabled = true;
                webView.CoreWebView2.Settings.IsWebMessageEnabled = true;
                
                // Set up message handler for preview → main communication
                webView.CoreWebView2.WebMessageReceived += OnWebMessageReceived;
                
                // Load the preview template
                LoadPreviewTemplate();
                
                isWebViewReady = true;
                statusText.Text = "RENDER: ACTIVE";
            }
            catch (Exception ex)
            {
                MessageBox.Show($"WebView2 initialization failed: {ex.Message}", 
                    "Preview Error", MessageBoxButton.OK, MessageBoxImage.Error);
                statusText.Text = "RENDER: FAILED";
            }
        }

        private void LoadPreviewTemplate()
        {
            // Don't load template here - wait for UpdateContent() to provide the visualization
            // This prevents showing the "Waiting for visualization data..." message
            isWebViewReady = true;
        }

        private void OnWebMessageReceived(object? sender, CoreWebView2WebMessageReceivedEventArgs e)
        {
            try
            {
                var json = e.WebMessageAsJson;
                var message = JObject.Parse(json);
                
                var type = message["type"]?.ToString();
                var htmlSnippet = message["htmlSnippet"]?.ToString() ?? string.Empty;

                switch (type)
                {
                    case "hover":
                        HoverElement?.Invoke(this, htmlSnippet);
                        break;
                    case "unhover":
                        HoverElement?.Invoke(this, string.Empty);
                        break;
                    case "highlight":
                        ClickElement?.Invoke(this, htmlSnippet);
                        break;
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Message handling error: {ex.Message}");
            }
        }

        public async void UpdateContent(string htmlContent)
        {
            if (!isWebViewReady)
            {
                await webView.EnsureCoreWebView2Async();
                isWebViewReady = true;
            }

            try
            {
                // Save HTML to a temporary file and navigate to it
                // This works better than NavigateToString for complex JavaScript like D3.js
                var tempFile = Path.Combine(Path.GetTempPath(), $"preview_{Guid.NewGuid()}.html");
                File.WriteAllText(tempFile, htmlContent, Encoding.UTF8);
                
                webView.Source = new Uri(tempFile);
                statusText.Text = "RENDER: UPDATED";
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Content update error: {ex.Message}");
                statusText.Text = "RENDER: ERROR";
            }
        }

        public async void SendEditorHover(string htmlSnippet)
        {
            if (!isWebViewReady) return;

            try
            {
                var message = new
                {
                    type = "editorHover",
                    htmlSnippet = htmlSnippet
                };

                var json = JsonConvert.SerializeObject(message);
                await webView.CoreWebView2.ExecuteScriptAsync(
                    $"window.dispatchEvent(new MessageEvent('message', {{ data: {json} }}));"
                );
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Editor hover send error: {ex.Message}");
            }
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
            Close();
        }
    }
}
