!include "MUI2.nsh"
!include "x64.nsh"

; Define the name of the installer
OutFile "GantrithorInstaller.exe"

; Define the installer icon
; Icon "app_icon.ico"

; Define the version of the installer
!define GantrithorVersion "1.0.0"

; The text that shows up in the title bar
Name "Gantrithor Installer v${GantrithorVersion}"

; Request application privileges for Windows Vista and newer
RequestExecutionLevel admin

; Default installation directory logic
Function .onInit
    ${If} ${RunningX64}
        StrCpy $INSTDIR "$PROGRAMFILES64\Gantrithor"
    ${Else}
        StrCpy $INSTDIR "$PROGRAMFILES\Gantrithor"
    ${EndIf}
FunctionEnd

; Pages
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Section "Install"

    ; Set the output path to the selected installation directory
    SetOutPath $INSTDIR

    ; Include Main directory and its contents, excluding 'excluded' directory
    File /r /x "excluded" "Gantrithor\*.*"

    ; Create the _internal directory
    ; SetOutPath $INSTDIR\_internal
    ; CreateDirectory $INSTDIR\_internal

    ; Create the internal torch directory
    ; SetOutPath $INSTDIR\_internal\torch
    ; CreateDirectory $INSTDIR\_internal\torch


    ; Copy contents from "ToMain" into the installed "_internal" directory
    CopyFiles /SILENT "Gantrithor\excluded\ToMain\*.*" "$INSTDIR\_internal"

    ; Custom logic to copy the entire "torch" directory into the "_internal" directory
    CopyFiles /SILENT "Gantrithor\excluded\torch\*.*" "$INSTDIR\_internal\torch"

    ; Write the installation path to a configuration file or the registry
    WriteRegStr HKCU "Software\Gantrithor" "InstallDir" $INSTDIR

    ; Create a shortcut on the desktop
    CreateShortCut "$DESKTOP\Gantrithor.lnk" "$INSTDIR\Gantrithor.exe"

    ; Create a shortcut in the start menu
    CreateDirectory "$SMPROGRAMS\Gantrithor"
    CreateShortCut "$SMPROGRAMS\Gantrithor\Gantrithor.lnk" "$INSTDIR\Gantrithor.exe"

    ; Write the uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

Section "Uninstall"
    ; Remove the installed files
    Delete "$INSTDIR\Gantrithor.exe"

    ; Remove the shortcuts
    Delete "$DESKTOP\Gantrithor.lnk"
    Delete "$SMPROGRAMS\Gantrithor\Gantrithor.lnk"
    RMDir "$SMPROGRAMS\Gantrithor"

    ; Remove the installation directory
    RMDir /r "$INSTDIR"

SectionEnd
