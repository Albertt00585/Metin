; Installer Metin (Inno Setup 6). Nu se ruleaza direct: build.ps1 il compileaza si ii da versiunea.
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={{6E3A2C1B-7F44-4B8D-9A51-3D2E8C0F4A77}
AppName=Metin
AppVersion={#AppVersion}
AppPublisher=Metin
DefaultDirName={localappdata}\Programs\Metin
DefaultGroupName=Metin
DisableProgramGroupPage=yes
DisableDirPage=yes
PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename=MetinSetup
SetupIconFile=assets\metin.ico
UninstallDisplayIcon={app}\Metin.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=force
RestartApplications=no

[Languages]
Name: "ro"; MessagesFile: "assets\Romanian.isl"

[Tasks]
Name: "desktopicon"; Description: "Creează o scurtătură pe Desktop"; GroupDescription: "Scurtături:"

[Files]
Source: "dist\Metin\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[InstallDelete]
; sterge fisierele versiunii vechi inainte de update
Type: filesandordirs; Name: "{app}\_internal"

[Icons]
Name: "{autoprograms}\Metin"; Filename: "{app}\Metin.exe"
Name: "{autodesktop}\Metin"; Filename: "{app}\Metin.exe"; Tasks: desktopicon

[Run]
; instalare normala: bifa "Porneste Metin" la final
Filename: "{app}\Metin.exe"; Description: "Pornește Metin"; Flags: nowait postinstall skipifsilent
; update automat (silentios): reporneste aplicatia singur
Filename: "{app}\Metin.exe"; Flags: nowait; Check: WizardSilent
