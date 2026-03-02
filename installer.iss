[Setup]
AppName=Video Editor
AppVersion=1.0
AppPublisher=Your Name
DefaultDirName={autopf}\VideoEditor
DefaultGroupName=Video Editor
OutputDir=dist
OutputBaseFilename=VideoEditor_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
Source: "dist\VideoEditor\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\Video Editor"; Filename: "{app}\VideoEditor.exe"
Name: "{group}\Uninstall Video Editor"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Video Editor"; Filename: "{app}\VideoEditor.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\VideoEditor.exe"; Description: "Launch Video Editor"; Flags: nowait postinstall skipifsilent
