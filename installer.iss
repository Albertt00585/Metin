; Installer Organizare Metin (Inno Setup 6). Nu se ruleaza direct: build.ps1 il compileaza si ii da versiunea.
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif
#define AppName "Organizare Metin"
#define AppExe "Organizare Metin.exe"

[Setup]
; AppId ramane acelasi ca la "Metin", ca instalarile vechi sa fie actualizate, nu dublate
AppId={{6E3A2C1B-7F44-4B8D-9A51-3D2E8C0F4A77}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppName}
DefaultDirName={localappdata}\Programs\{#AppName}
UsePreviousAppDir=no
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
DisableDirPage=yes
PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename=OrganizareMetinSetup
SetupIconFile=assets\metin.ico
UninstallDisplayIcon={app}\{#AppExe}
UninstallDisplayName={#AppName}
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
Source: "dist\{#AppName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[InstallDelete]
; sterge fisierele versiunii vechi inainte de update
Type: filesandordirs; Name: "{app}\_internal"
; curatenie dupa redenumirea din "Metin": folderul si scurtaturile vechi
Type: filesandordirs; Name: "{localappdata}\Programs\Metin"
Type: files; Name: "{autodesktop}\Metin.lnk"
Type: files; Name: "{autoprograms}\Metin.lnk"

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
; instalare normala: bifa "Porneste Organizare Metin" la final
Filename: "{app}\{#AppExe}"; Description: "Pornește {#AppName}"; Flags: nowait postinstall skipifsilent
; update silentios din versiunea 1.0.0 veche (butonul "Actualizează"): reporneste aplicatia.
; Versiunile noi instaleaza update-ul la inchidere cu /norelaunch=1, deci nu repornesc nimic.
Filename: "{app}\{#AppExe}"; Flags: nowait; Check: ShouldRelaunch

[Code]
function ShouldRelaunch: Boolean;
begin
  Result := WizardSilent and (ExpandConstant('{param:norelaunch|0}') <> '1');
end;
