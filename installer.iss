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
; update silentios din versiunea 1.0.0 (butonul "Actualizează"): reporneste aplicatia.
; Versiunile noi instaleaza update-ul la inchidere cu /norelaunch=1, deci nu repornesc nimic.
Filename: "{app}\Metin.exe"; Flags: nowait; Check: ShouldRelaunch

[Code]
function ShouldRelaunch: Boolean;
begin
  Result := WizardSilent and (ExpandConstant('{param:norelaunch|0}') <> '1');
end;
