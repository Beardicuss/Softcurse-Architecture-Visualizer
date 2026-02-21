using System.Configuration;
using System.Data;
using System.Windows;

namespace ArchitectureVisualizerApp
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App : Application
    {
        public static StartupArgs ParsedArgs { get; private set; } = new StartupArgs();

        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            for (int i = 0; i < e.Args.Length; i++)
            {
                var arg = e.Args[i].ToLower();
                if (arg == "--path" && i + 1 < e.Args.Length)
                {
                    ParsedArgs.ProjectPath = e.Args[++i];
                }
                else if (arg == "--cache")
                {
                    ParsedArgs.UseCache = true;
                }
                else if (arg == "--no-cache")
                {
                    ParsedArgs.UseCache = false;
                }
                else if (arg == "--profile")
                {
                    ParsedArgs.Profile = true;
                }
                else if (arg == "--auto-analyze")
                {
                    ParsedArgs.AutoAnalyze = true;
                }
            }
        }
    }

    public class StartupArgs
    {
        public string? ProjectPath { get; set; }
        public bool UseCache { get; set; } = true;
        public bool AutoAnalyze { get; set; } = false;
        public bool Profile { get; set; } = false;
    }
}
