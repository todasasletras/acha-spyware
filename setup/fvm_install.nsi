!include Sections.nsh
!include LogicLib.nsh
!include FileFunc.nsh
!include nsDialogs.nsh
#!include INetC.nsh

; --- General Setup ---
Name "Ferramenta de Verificação Móvel"
OutFile "FMV.exe"
InstallDir "$PROGRAMFILES\FMV"
UninstallText "Desinstalar Ferramenta de Verificação Móvel"

; --- Interface Settings ---
XPStyle on
InstallColors 4444FF FFFFFF ; Blue background with white text

; --- Variables ---
Var VirtualBoxInstallerPath
Var ExtensionPackPath
Var OVADownloadURL
Var OVATempFilePath
Var VBoxManageExePath
Var VirtualBoxExePath
Var DefaultVMName
Var SectionVirtualBox
Var SectionExtensionPack
Var SectionOVAImport
Var SectionShortcut

; --- Constants ---
!define VirtualBoxExeName "VirtualBox-7.1.0-164728-Win.exe"
!define ExtensionPackName "Oracle_VirtualBox_Extension_Pack-7.1.0.vbox-extpack"
!define OVATempFileName "Appliance.ova"
!define Default_VBoxManagePath "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
!define Default_VirtualBoxExePath "C:\Program Files\Oracle\VirtualBox\VirtualBox.exe"
!define Default_VMName "mvt" ; ** REPLACE WITH YOUR DESIRED DEFAULT VM NAME **
!define OVA_DOWNLOAD_LINK "https://drive.google.com/uc?id=1jDc-UsDf-JoNSF4d0r-tC3hVN3xp6l1a&export=download" ; ** REPLACE WITH YOUR ACTUAL DIRECT DOWNLOAD LINK **

; --- Section Definitions ---
SectionGroup "Optional Components"
    Section /o "Install VirtualBox" SEC_VIRTUALBOX
    SectionEnd

    Section /o "Install VirtualBox Extension Pack" SEC_EXTENSIONPACK
#        #SectionIn RO SEC_VIRTUALBOX ; Requires VirtualBox section to be selected or installed
    SectionEnd

    Section /o "Download and Import OVA Appliance" SEC_OVAIMPORT
#        #SectionIn RO SEC_VIRTUALBOX ; Requires VirtualBox section to be selected or installed
    SectionEnd

    Section /o "Create Desktop Shortcut to Virtual Machine" SEC_SHORTCUT
#5        #5SectionIn RO SEC_OVAIMPORT ; Requires OVA Import section to be selected
    SectionEnd
SectionGroupEnd

; --- Uninstall Section ---
Section "Uninstall" UNSEC_UNINSTALL
; --- Remove Shortcuts (Example - You may need to adapt based on how you named shortcuts dynamically) ---
    Delete "$DESKTOP\${Default_VMName}.lnk"

    ; --- Uninstall VirtualBox (Optional -  Potentially complex and might need admin rights) ---
    ;  This is left as an exercise as VirtualBox uninstallation is non-trivial and might require specific commands or detection.
    ;  Consider if you want to uninstall VirtualBox when your application uninstalls.

    ; --- Uninstall Application Files (if any) ---
    ; RMDir /r "$INSTDIR\YourAppFilesFolder" ; Example - replace with your app files folder

    ; --- Standard Uninstall cleanup ---
    Delete "$INSTDIR\Uninstall.exe"
    RMDir "$INSTDIR"

    MessageBox MB_OK "Uninstallation Complete."
SectionEnd


; --- Functions ---

Function DownloadOVA
    ${If} ${SectionIsSelected} ${SEC_OVAIMPORT}
        StrCpy $OVADownloadURL "${OVA_DOWNLOAD_LINK}" ; Set download URL from constant
        StrCpy $OVATempFilePath "$TEMP\${OVATempFileName}" ; Set temp file path

        InetC::get /URL "$OVADownloadURL" /OUT "$OVATempFilePath" /TIMEOUT 60000 ; 60 seconds timeout, adjust if needed
        Pop $0
        ${If} $0 != "OK"
            MessageBox MB_OK|MB_ICONSTOP "Error downloading OVA file. Please check your internet connection and try again."
            SetErrors ; Propagate error to abort installation if needed
        ${Else}
            MessageBox MB_OK "OVA file downloaded successfully to $OVATempFilePath"
        ${EndIf}
    ${EndIf}
FunctionEnd


Function InstallVirtualBox
    ${If} ${SectionIsSelected} ${SEC_VIRTUALBOX}
        SetDetailsPrint textonly
        DetailPrint "Installing VirtualBox..."
        StrCpy $VirtualBoxInstallerPath "$TEMP\${VirtualBoxExeName}"

        ExecWait '"$VirtualBoxInstallerPath" /S' ; /S for silent install - Verify VirtualBox installer silent parameters

        ${If} ${Errors}
            MessageBox MB_OK|MB_ICONSTOP "VirtualBox installation failed. Please check the setup log."
            SetErrors ; Propagate error
        ${Else}
            DetailPrint "VirtualBox installation completed."
        ${EndIf}
    ${EndIf}
FunctionEnd


Function InstallExtensionPack
    ${If} ${SectionIsSelected} ${SEC_EXTENSIONPACK}
        ${If} ${SectionIsSelected} ${SEC_VIRTUALBOX} ; Check if VirtualBox section is selected or already installed
            SetDetailsPrint textonly
            DetailPrint "Installing VirtualBox Extension Pack..."
            StrCpy $ExtensionPackPath "$TEMP\${ExtensionPackName}"
            StrCpy $VBoxManageExePath "${Default_VBoxManagePath}" ; Use default path - consider making dynamic

            ExecWait '"$VBoxManageExePath" extpack install "$ExtensionPackPath" --accept-license --replace'

            ${If} ${Errors}
                MessageBox MB_OK|MB_ICONSTOP "VirtualBox Extension Pack installation failed. VirtualBox might not be installed or VBoxManage.exe not found."
                SetErrors
            ${Else}
                DetailPrint "VirtualBox Extension Pack installation completed."
            ${EndIf}
        ${Else}
            MessageBox MB_OK|MB_ICONINFORMATION "VirtualBox Extension Pack installation skipped because VirtualBox is not being installed."
        ${EndIf}
    ${EndIf}
FunctionEnd


Function ImportOVAAppliance
    ${If} ${SectionIsSelected} ${SEC_OVAIMPORT}
        ${If} ${SectionIsSelected} ${SEC_VIRTUALBOX} ; Ensure VirtualBox is being installed
            SetDetailsPrint textonly
            DetailPrint "Importing OVA Appliance into VirtualBox..."
            StrCpy $OVATempFilePath "$TEMP\${OVATempFileName}" ; Path to downloaded OVA
            StrCpy $VBoxManageExePath "${Default_VBoxManagePath}" ; Use default path - consider making dynamic
            StrCpy $DefaultVMName "${Default_VMName}" ; Get default VM name

            ExecWait '"$VBoxManageExePath" import "$OVATempFilePath"' ; Basic import command

            ${If} ${Errors}
                MessageBox MB_OK|MB_ICONSTOP "OVA Appliance import failed. VirtualBox might not be installed or OVA download failed."
                SetErrors
            ${Else}
                DetailPrint "OVA Appliance imported successfully."
            ${EndIf}
        ${Else}
            MessageBox MB_OK|MB_ICONINFORMATION "OVA Appliance import skipped because VirtualBox is not being installed."
        ${EndIf}
    ${EndIf}
FunctionEnd


Function CreateVMShortcut
    ${If} ${SectionIsSelected} ${SEC_SHORTCUT}
        ${If} ${SectionIsSelected} ${SEC_OVAIMPORT} ; Ensure OVA is imported
            SetDetailsPrint textonly
            DetailPrint "Creating Desktop Shortcut to Virtual Machine..."
            StrCpy $VirtualBoxExePath "${Default_VirtualBoxExePath}" ; Path to VirtualBox.exe
            StrCpy $DefaultVMName "${Default_VMName}" ; VM Name

            CreateShortCut "$DESKTOP\${DefaultVMName}.lnk" "$VirtualBoxExePath" "--startvm $\"$DefaultVMName$\"" "$VirtualBoxExePath" "" "" "" "" "Start ${DefaultVMName} Virtual Machine"

            ${If} ${Errors}
                MessageBox MB_OK|MB_ICONSTOP "Failed to create desktop shortcut to Virtual Machine."
                SetErrors
            ${Else}
                DetailPrint "Desktop shortcut to Virtual Machine created."
            ${EndIf}
        ${Else}
            MessageBox MB_OK|MB_ICONINFORMATION "Shortcut creation skipped because OVA Appliance is not being imported."
        ${EndIf}
    ${EndIf}
FunctionEnd


; --- Install Sections Calls ---
Section SEC_VIRTUALBOX
    Call InstallVirtualBox
SectionEnd

Section SEC_EXTENSIONPACK
    Call InstallExtensionPack
SectionEnd

Section SEC_OVAIMPORT
    Call DownloadOVA
    Call ImportOVAAppliance
SectionEnd

Section SEC_SHORTCUT
    Call CreateVMShortcut
SectionEnd


; --- Files Section ---
Section "Files and Resources"
    SetOutPath "$TEMP" ; Extract to Temp folder
    File "${VirtualBoxExeName}"  ; Place VirtualBox installer in the same directory as NSIS script
    File "${ExtensionPackName}" ; Place Extension Pack in the same directory as NSIS script
SectionEnd


; --- Uninstaller Section Calls (Adjust as needed) ---
Section UNSEC_UNINSTALL
    ; --- Remove Shortcuts (Example - You may need to adapt based on how you named shortcuts dynamically) ---
    Delete "$DESKTOP\${Default_VMName}.lnk"

    ; --- Uninstall VirtualBox (Optional -  Potentially complex and might need admin rights) ---
    ;  This is left as an exercise as VirtualBox uninstallation is non-trivial and might require specific commands or detection.
    ;  Consider if you want to uninstall VirtualBox when your application uninstalls.

    ; --- Uninstall Application Files (if any) ---
    ; RMDir /r "$INSTDIR\YourAppFilesFolder" ; Example - replace with your app files folder

    ; --- Standard Uninstall cleanup ---
    Delete "$INSTDIR\Uninstall.exe"
    RMDir "$INSTDIR"

    MessageBox MB_OK "Uninstallation Complete."
SectionEnd


; --- MUI Settings (Optional - For a more modern UI - Requires MUI2.nsh) ---
; !include MUI2.nsh
; !insertmacro MUI_PAGE_WELCOME
; !insertmacro MUI_PAGE_COMPONENTS
; !insertmacro MUI_PAGE_DIRECTORY
; !insertmacro MUI_PAGE_INSTFILES
; !insertmacro MUI_PAGE_FINISH
; !insertmacro MUI_UNPAGE_WELCOME
; !insertmacro MUI_UNPAGE_CONFIRM
; !insertmacro MUI_UNPAGE_UNINSTFILES
; !insertmacro MUI_UNPAGE_FINISH


; --- Startup Section ---
Section "" SectionStartup
SectionEnd

Function .onInit
    ; --- Initialize Variables ---
    StrCpy $VirtualBoxInstallerPath "$TEMP\${VirtualBoxExeName}"
    StrCpy $ExtensionPackPath "$TEMP\${ExtensionPackName}"
    StrCpy $OVADownloadURL "${OVA_DOWNLOAD_LINK}"
    StrCpy $OVATempFilePath "$TEMP\${OVATempFileName}"
    StrCpy $VBoxManageExePath "${Default_VBoxManagePath}"
    StrCpy $VirtualBoxExePath "${Default_VirtualBoxExePath}"
    StrCpy $DefaultVMName "${Default_VMName}"

    ; --- Check if VirtualBox is already installed (Example - Simple Registry Check) ---
    ReadRegStr $0 HKLM "SOFTWARE\Oracle\VirtualBox" ""
    ${If} $0 != ""
        ; VirtualBox seems to be installed - You can adjust section selection logic here if needed
        SectionSetFlags ${SEC_VIRTUALBOX} ${SF_RO} ; Make VirtualBox section read-only (installed already)
        SectionSetInstTypes ${SEC_EXTENSIONPACK} ${SF_RO} ; Extension pack only installable if VirtualBox is "installed" or being installed.
        SectionSetInstTypes ${SEC_OVAIMPORT} ${SF_SELECTED}
        SectionSetInstTypes ${SEC_SHORTCUT} ${SF_SELECTED}
    ${EndIf}

FunctionEnd