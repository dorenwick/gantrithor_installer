!include "MUI2.nsh"
!include "x64.nsh"
!include "LogicLib.nsh"

Icon "icon_gantrithor_2.ico"
!define MUI_UNICON "icon_gantrithor_2.ico"
OutFile "GantrithorInstaller.exe"
!define GantrithorVersion "1.0.0"
Name "Gantrithor Installer v${GantrithorVersion}"
RequestExecutionLevel admin

Function .onInit
    ${If} ${RunningX64}
        StrCpy $INSTDIR "$PROGRAMFILES64\Gantrithor"
    ${Else}
        StrCpy $INSTDIR "$PROGRAMFILES\Gantrithor"
    ${EndIf}

    ReadRegStr $R0 HKCU "Software\Gantrithor" "InstallDir"
    ${If} $R0 != ""
        ExecWait '"$R0\Uninstall.exe" /S'
    ${EndIf}
FunctionEnd

!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Section "Install"
    SetOutPath $INSTDIR
    File "Gantrithor\Gantrithor.exe"	
    File /r /x "excluded" "Gantrithor\*.*"
    SetOutPath $INSTDIR\_internal
    CreateDirectory $INSTDIR\_internal
    SetOutPath $INSTDIR\_internal\torch
    CreateDirectory $INSTDIR\_internal\torch
    CopyFiles /SILENT "$EXEDIR\Gantrithor\excluded\ToMain\*.*" "$INSTDIR\_internal"
    CopyFiles /SILENT "$EXEDIR\Gantrithor\excluded\torch\*.*" "$INSTDIR\_internal\torch"
    WriteRegStr HKCU "Software\Gantrithor" "InstallDir" $INSTDIR
    SetOutPath $APPDATA\Gantrithor
    CreateDirectory $APPDATA\Gantrithor\data
    IfFileExists "$APPDATA\Gantrithor\data\*.*" 0 +2
    RMDir /r "$APPDATA\Gantrithor\data"
    CopyFiles /SILENT "$EXEDIR\Gantrithor\data\*.*" "$APPDATA\Gantrithor\data"
    CreateShortCut "$DESKTOP\Gantrithor.lnk" "$INSTDIR\Gantrithor.exe" "" "icon_gantrithor_2.ico"
    CreateDirectory "$SMPROGRAMS\Gantrithor"
    CreateShortCut "$SMPROGRAMS\Gantrithor\Gantrithor.lnk" "$INSTDIR\Gantrithor.exe"
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Gantrithor" "DisplayName" "Gantrithor"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Gantrithor" "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Gantrithor" "DisplayIcon" "$INSTDIR\icon_gantrithor_2.ico"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Gantrithor" "DisplayVersion" "${GantrithorVersion}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Gantrithor" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Gantrithor" "NoRepair" 1

    # Add Gantrithor to the Windows Firewall for both private and public connections
    ${If} ${RunningX64}
    	ExecWait '"$SYSDIR\Netsh.exe" advfirewall firewall add rule name="Gantrithor" dir=in action=allow program="$INSTDIR\Gantrithor.exe" enable=yes profile=private,public' $0	
    ${Else}
    	ExecWait '"$WINDIR\System32\Netsh.exe" advfirewall firewall add rule name="Gantrithor" dir=in action=allow program="$INSTDIR\Gantrithor.exe" enable=yes profile=private,public' $0
    ${EndIf}
	${If} $0 != 0
    MessageBox MB_ICONEXCLAMATION "Failed to add Gantrithor to the Windows Firewall for both private and public connections. Please add it manually."
    ${EndIf}

SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\Gantrithor.exe"
    Delete "$DESKTOP\Gantrithor.lnk"
    Delete "$SMPROGRAMS\Gantrithor\Gantrithor.lnk"
    RMDir "$SMPROGRAMS\Gantrithor"
    RMDir /r "$INSTDIR"
    DeleteRegKey HKCU "Software\Gantrithor"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Gantrithor"
    # Remove Gantrithor from the Windows Firewall
    ${If} ${RunningX64}
        ExecWait '"$SYSDIR\Netsh.exe" advfirewall firewall delete rule name="Gantrithor" program="$INSTDIR\Gantrithor.exe"'
    ${Else}
        ExecWait '"$WINDIR\System32\Netsh.exe" advfirewall firewall delete rule name="Gantrithor" program="$INSTDIR\Gantrithor.exe"'
    ${EndIf}		
SectionEnd
