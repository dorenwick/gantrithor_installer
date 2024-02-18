; Include necessary NSIS macros
!include "MUI2.nsh"
!include "WinMessages.nsh"
!include "LogicLib.nsh"

; Define constants or variables
!define MyAppName "Gantrithor"
!define MyAppRegKey "Software\MyCompany\${MyAppName}"

; Function to create registry entries
Function CreateRegistryEntries
    ; Create a key in HKCU (HKEY_CURRENT_USER)
    WriteRegStr HKCU "${MyAppRegKey}" "InstallPath" "$INSTDIR"

    ; Example of writing other data types
    WriteRegDWORD HKCU "${MyAppRegKey}" "ExampleDWORD" 0x00000001

    ; Create file associations, if applicable
    WriteRegStr HKCR ".myext" "" "MyAppFile"
    WriteRegStr HKCR "MyAppFile" "" "My Application File"

    ; More registry entries as needed
FunctionEnd

; Function to delete registry entries
Function DeleteRegistryEntries
    ; Delete a key and all its subkeys and values
    DeleteRegKey HKCU "${MyAppRegKey}"

    ; Remove file associations, if applicable
    DeleteRegKey HKCR ".myext"
    DeleteRegKey HKCR "MyAppFile"

    ; More registry deletion as needed
FunctionEnd
