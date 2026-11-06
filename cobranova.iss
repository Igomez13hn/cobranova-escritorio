[Setup]
AppId={{A7B3E1C4-6D20-4F55-9A18-0C4E7B2D91AA}
AppName=Cobranova 360
AppVersion=1.0.0
AppPublisher=Cobranova
DefaultDirName={autopf}\Cobranova 360
DefaultGroupName=Cobranova 360
OutputDir=installer-out
OutputBaseFilename=Cobranova360-Setup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
PrivilegesRequired=admin
UninstallDisplayIcon={app}\Cobranova.exe

[Files]
Source: "build\cobranova_host.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Cobranova 360"; Filename: "{app}\Cobranova.exe"
Name: "{autodesktop}\Cobranova 360"; Filename: "{app}\Cobranova.exe"

[Run]
Filename: "netsh"; Parameters: "advfirewall firewall add rule name=""Cobranova 360"" dir=in action=allow program=""{app}\Cobranova.exe"" enable=yes profile=private"; Flags: runhidden
Filename: "{app}\Cobranova.exe"; Description: "Abrir Cobranova 360"; Flags: postinstall nowait skipifsilent
