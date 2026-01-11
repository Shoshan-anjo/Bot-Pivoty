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
SetupIconFile=assets\LogoIconoDino.ico
; El ejecutable final generado por PyInstaller
OutputBaseFilename=Pivoty_Installer_v1.0.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; Imágenes personalizadas del Dinosaurio (Ahora en PNG con transparencia)
WizardImageFile=assets\WelcomeDinoSinFondo.png
WizardSmallImageFile=assets\ThanksDinoSinFondo.png


[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Dirs]
Name: "{app}\logs"; Permissions: users-full
Name: "{app}\config"; Permissions: users-full

[Files]
; Archivo principal
Source: "dist\Pivoty.exe"; DestDir: "{app}"; Flags: ignoreversion
; Carpetas de configuración esenciales (vacías o por defecto)
Source: "config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "assets\LogoIconoDino.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env"; DestDir: "{app}"; Flags: ignoreversion; Permissions: users-full
; Crear carpeta de logs vacía
Source: "logs\*"; DestDir: "{app}\logs"; Flags: ignoreversion recursesubdirs createallsubdirs



[Icons]
Name: "{group}\Pivoty"; Filename: "{app}\Pivoty.exe"; IconFilename: "{app}\LogoIconoDino.ico"
Name: "{autodesktop}\Pivoty"; Filename: "{app}\Pivoty.exe"; Tasks: desktopicon; IconFilename: "{app}\LogoIconoDino.ico"

[Run]
Filename: "{app}\Pivoty.exe"; Description: "{cm:LaunchProgram,Pivoty}"; Flags: nowait postinstall skipifsilent
