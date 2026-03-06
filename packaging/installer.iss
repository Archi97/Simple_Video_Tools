[Setup]
AppName=Simple Video Tools
AppVersion=1.0
AppPublisher=Tyombo
DefaultDirName={autopf}\SimpleVideoTools
DefaultGroupName=Simple Video Tools
OutputDir=..\dist
OutputBaseFilename=SimpleVideoTools_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
Source: "..\dist\SimpleVideoTools\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\Simple Video Tools"; Filename: "{app}\SimpleVideoTools.exe"
Name: "{group}\Uninstall Simple Video Tools"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Simple Video Tools"; Filename: "{app}\SimpleVideoTools.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SimpleVideoTools.exe"; Description: "Launch Simple Video Tools"; Flags: nowait postinstall skipifsilent
