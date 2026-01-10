; Script de instalación para Pivoty
; Desarrollado para automatización profesional de Excel

[Setup]
AppId={{shohan-pivoty-bot-2026}}
AppName=Pivoty
AppVersion=1.0.0
AppPublisher=Shohan
DefaultDirName={autopf}\Pivoty
DefaultGroupName=Pivoty
AllowNoIcons=yes
; El icono del instalador
SetupIconFile=LogoIconoDino.ico
; El ejecutable final generado por PyInstaller
OutputBaseFilename=Pivoty_Installer_v1.0.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; Imágenes personalizadas del Dinosaurio (Deben ser BMP)
WizardImageFile=WelcomeDino.bmp
WizardSmallImageFile=ThanksDino.bmp


[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Archivo principal
Source: "dist\Pivoty.exe"; DestDir: "{app}"; Flags: ignoreversion
; Carpetas de configuración esenciales (vacías o por defecto)
Source: "config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "LogoIconoDino.ico"; DestDir: "{app}"; Flags: ignoreversion
; Crear carpeta de logs vacía
Source: "logs\*"; DestDir: "{app}\logs"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Pivoty"; Filename: "{app}\Pivoty.exe"; IconFilename: "{app}\LogoIconoDino.ico"
Name: "{autodesktop}\Pivoty"; Filename: "{app}\Pivoty.exe"; Tasks: desktopicon; IconFilename: "{app}\LogoIconoDino.ico"

[Run]
Filename: "{app}\Pivoty.exe"; Description: "{cm:LaunchProgram,Pivoty}"; Flags: nowait postinstall skipifsilent
