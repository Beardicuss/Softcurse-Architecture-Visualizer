[Setup]
AppName=Softcurse Architecture Visualizer
AppVersion=1.0.1
DefaultDirName={autopf}\Softcurse Architecture Visualizer
DefaultGroupName=Softcurse Architecture Visualizer
OutputDir=d:\Projects\In progress\UniversalAnalyzer\ArchitectureVisualizerApp\output
OutputBaseFilename=ArchitectureVisualizerSetup
SetupIconFile=d:\Projects\In progress\UniversalAnalyzer\Softcurse Architecture Visualizer\ui\new logo.ico
Compression=lzma
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "d:\Projects\In progress\UniversalAnalyzer\ArchitectureVisualizerApp\publish\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "d:\Projects\In progress\UniversalAnalyzer\Softcurse Architecture Visualizer\ui\new logo.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Softcurse Architecture Visualizer"; Filename: "{app}\ArchitectureVisualizerApp.exe"; IconFilename: "{app}\new logo.ico"
Name: "{autodesktop}\Softcurse Architecture Visualizer"; Filename: "{app}\ArchitectureVisualizerApp.exe"; Tasks: desktopicon; IconFilename: "{app}\new logo.ico"

[Run]
Filename: "{app}\ArchitectureVisualizerApp.exe"; Description: "{cm:LaunchProgram,Softcurse Architecture Visualizer}"; Flags: nowait postinstall skipifsilent
