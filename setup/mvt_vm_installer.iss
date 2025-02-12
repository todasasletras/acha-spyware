[Setup]
AppName=Ferramenta de Verficação Móvel
AppVersion=1.0
DefaultDirName={commonpf}\FVM
UninstallDisplayName=Desinstalação da Ferramenta de Verficação Móvel
OutputDir=userdocs:Inno Setup Output
OutputBaseFilename=FVM_Setup

[Tasks]
Name: "virtualbox"; Description: "Install VirtualBox"; GroupDescription: "Optional Components:";
Name: "extensionpack"; Description: "Install VirtualBox Extension Pack"; GroupDescription: "Optional Components:"; Flags: unchecked; 
Name: "ovaimport"; Description: "Download and Import OVA Appliance"; GroupDescription: "Optional Components:"; Flags: unchecked; 
Name: "shortcutsvm"; Description: "Create Desktop Shortcut to Virtual Machine"; GroupDescription: "Optional Components:"; Flags: unchecked; 

[Files]
Source: "YourAppFiles\*"; DestDir: "{app}";
Source: "VirtualBox-*.exe"; DestDir: "{tmp}"; DestName: "VirtualBox.exe"; Flags: dontcopy
Source: "Oracle_VM_VirtualBox_Extension_Pack-*.vbox-extpack"; DestDir: "{tmp}"; DestName: "ExtensionPack.vbox-extpack"; Flags: dontcopy

[Code]
// --- Constants ---
const
  VirtualBoxExeName = 'VirtualBox.exe';
  ExtensionPackName = 'ExtensionPack.vbox-extpack';
  OVADownloadURL = 'https://drive.google.com/uc?id=1jDc-UsDf-JoNSF4d0r-tC3hVN3xp6l1a&export=download'; // **REPLACE THIS WITH YOUR ACTUAL DIRECT DOWNLOAD LINK**
  OVATempFileName = 'mvt.ova';
  VBoxManagePath = 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'; // Default Path - Consider making this dynamic in real scenario
  VirtualBoxAppPath = 'C:\Program Files\Oracle\VirtualBox\VirtualBox.exe'; // Path to VirtualBox GUI App
  DefaultVMName = 'mvt'; // **REPLACE WITH YOUR DESIRED DEFAULT VM NAME** - OR Make Dynamic

// --- Function to Download File ---
function DownloadOVAFile(URL, LocalFileName: string): Boolean;
var
  Downloader: TDownloader;
  ResultCode: integer;
  Page: TWizardPage;
begin
  Result := False;
  Page := CreateCustomPage(wpInstalling, 'Downloading OVA Appliance', 'Please wait while the OVA appliance is downloaded.');
  try
    Downloader := TDownloader.Create(nil);
    try
      Downloader.Filename := LocalFileName;
      Downloader.URL := URL;
      Downloader.OnProgress := @DownloadProgress; // Optional - Implement DownloadProgress function for feedback
      Downloader.LogExceptions := True;

      WizardForm.ProgressGauge.Style := npbstMarquee; // Indeterminate progress
      WizardForm.ProgressGauge.Marquee := True;
      WizardForm.NextButton.Enabled := false; // Disable Next button during download

      try
        if not Downloader.Download then
        begin
          RaiseException('Error downloading OVA file: ' + Downloader.LastErrorMsg);
        end;
      except
        on E: Exception do
        begin
          MsgBox(E.Message, mbError, MB_OK);
          Result := False;
          Exit;
        end;
      end;

      WizardForm.ProgressGauge.Marquee := False;
      WizardForm.ProgressGauge.Style := npbstNormal;
      WizardForm.NextButton.Enabled := true; // Re-enable Next button

      Result := True;
    finally
      Downloader.Free;
    end;
  finally
    DestroyCustomPage(Page);
  end;
end;

// Optional: Implement Download Progress function if you want a progress bar (more complex)
procedure DownloadProgress(Sender: TDownloader; const Progress, ProgressMax: Int64);
begin
  // You can update a progress bar here if you want to show download progress.
  // For simplicity, this example uses an indeterminate progress bar during download.
end;

// --- Events ---
procedure CurStepDone(CurStep: TSetupStep);
var
  OVATempFilePath: string;
begin
  if CurStep = ssInstall then
  begin
    if WizardForm.TasksCheckBox.Checked[2] then // Index 2 corresponds to "ovaimport" task
    begin
      OVATempFilePath := ExpandConstant('{tmp}\' + OVATempFileName);

      // Download OVA file
      Log('Downloading OVA file from: ' + OVADownloadURL + ' to: ' + OVATempFilePath);
      if not DownloadOVAFile(OVADownloadURL, OVATempFilePath) then
      begin
        Log('OVA Download Failed.');
        // Optionally: Handle download failure more gracefully (e.g., message to user)
        // For this example, we'll just log the failure and continue setup.
      end else begin
        Log('OVA Download Successful.');
      end;
    end;
  end;
end;

procedure CurUninstallStepDone(CurUninstallStep: TUninstallStep);
var
  OVATempFilePath: string;
begin
  if CurUninstallStep = usUninstall then
  begin
    OVATempFilePath := ExpandConstant('{tmp}\' + OVATempFileName);
    // Cleanup downloaded OVA after uninstall (optional)
    if FileExists(OVATempFilePath) then
    begin
      Log('Deleting downloaded OVA file: ' + OVATempFilePath);
      DeleteFile(OVATempFilePath);
    end;
  end;
end;

[Run]
Filename: "{tmp}\VirtualBox.exe"; Parameters: "--silent"; Description: "Installing VirtualBox"; Flags: waituntilterminated runhidden; Check: WizardForm.TasksCheckBox.Checked[0]
Filename: "{code:GetVBoxManagePath}"; Parameters: "extpack install ""{tmp}\ExtensionPack.vbox-extpack"" --accept-license --replace"; Description: "Installing VirtualBox Extension Pack"; Flags: waituntilterminated runhidden; WorkingDir: "{code:GetVBoxManageDir}"; Check: WizardForm.TasksCheckBox.Checked[1]; RunOnceId: InstallExtensionPack
Filename: "{code:GetVBoxManagePath}"; Parameters: "import ""{tmp}\mvt.ova"""; Description: "Importing OVA Appliance into VirtualBox"; Flags: waituntilterminated runhidden; WorkingDir: "{code:GetVBoxManageDir}"; Check: WizardForm.TasksCheckBox.Checked[2]; RunOnceId: ImportOVAAppliance

