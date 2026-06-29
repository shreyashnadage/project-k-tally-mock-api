; Inno Setup script for Tally Data Simulator
; Run: "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\setup.iss

#define AppName "Tally Data Simulator"
#define AppVersion "1.0.0"
#define AppPublisher "Project K"
#define AppURL "http://localhost:9001"
#define AppExeName "TallySimulator.exe"
#define BuildDir "..\dist\TallySimulator"

[Setup]
AppId={{A8C4F2D1-9E3B-4F7A-B2C6-D5E8F1A3B4C7}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
DefaultDirName={autopf}\TallySimulator
DefaultGroupName={#AppName}
OutputDir=..\dist
OutputBaseFilename=TallySimulator-Setup
SetupIconFile=
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName={#AppName}
; Don't clean up AppData on uninstall (preserve simulations DB)
UninstallDisplayIcon={app}\{#AppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"
Name: "startupicon"; Description: "Start automatically with Windows"; GroupDescription: "Additional options:"; Flags: unchecked

[Files]
; Copy entire PyInstaller output folder
Source: "{#BuildDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Comment: "Start Tally Data Simulator (ports 9000 + 9001)"
Name: "{group}\Open in Browser"; Filename: "http://localhost:9001"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon; Comment: "Start Tally Data Simulator"

[Run]
; Option to launch after install
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName} now"; Flags: nowait postinstall skipifsilent

[Registry]
; Startup with Windows (optional task)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "TallySimulator"; ValueData: """{app}\{#AppExeName}"""; Flags: uninsdeletevalue; Tasks: startupicon

[UninstallDelete]
; Clean up any log files created by the app
Type: files; Name: "{app}\*.log"
