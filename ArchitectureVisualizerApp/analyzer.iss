; ══════════════════════════════════════════════════════════════════
; Softcurse Architecture Visualizer — Inno Setup Installer Script
; Version 2.0.0
; Copyright (c) 2026 Softcurse Corp. All rights reserved.
; ══════════════════════════════════════════════════════════════════

#define MyAppName "Softcurse Architecture Visualizer"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "Softcurse Corp."
#define MyAppURL "https://github.com/Beardicuss/Softcurse-Architecture-Visualizer"
#define MyAppExeName "ArchitectureVisualizerApp.exe"
#define MyAppAssocName "Architecture Project"
#define MyAppCopyright "Copyright (c) 2026 Softcurse Corp."

[Setup]
AppId={{B8E3F1A0-7C4D-4B2E-9A5F-1D3E6C8B9F20}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright={#MyAppCopyright}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Setup
VersionInfoCopyright={#MyAppCopyright}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=d:\Dev\Projects\Web\UniversalAnalyzer\ArchitectureVisualizerApp\output
OutputBaseFilename=SoftcurseArchitectureVisualizerSetup_v{#MyAppVersion}
SetupIconFile=d:\Dev\Projects\Web\UniversalAnalyzer\ArchitectureVisualizerApp\Assets\ui\arch.ico
UninstallDisplayIcon={app}\arch.ico
UninstallDisplayName={#MyAppName}
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
DisableProgramGroupPage=yes
DisableWelcomePage=no
PrivilegesRequired=admin
MinVersion=10.0.17763
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Main published application (self-contained .NET 8)
Source: "d:\Dev\Projects\Web\UniversalAnalyzer\ArchitectureVisualizerApp\publish\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Application icon
Source: "d:\Dev\Projects\Web\UniversalAnalyzer\ArchitectureVisualizerApp\Assets\ui\arch.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\arch.ico"; Comment: "Launch {#MyAppName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; IconFilename: "{app}\arch.ico"

; Desktop shortcut
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\arch.ico"; Comment: "Launch {#MyAppName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
