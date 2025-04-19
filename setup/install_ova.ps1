#Requires -RunAsAdministrator

<#
.SINOPSE
    Instala o VirtualBox, o Extension Pack, importa um OVA, cria uma pasta
    e cria um atalho na área de trabalho para iniciar a VM como administrador.

.DESCRIÇÃO
    Este script automatiza a configuração de um ambiente VirtualBox:
    1. Verifica privilégios de Administrador.
    2. Faz o download do VirtualBox, Extension Pack e de um arquivo OVA.
    3. Instala o VirtualBox silenciosamente.
    4. Instala o VirtualBox Extension Pack (pode exigir aceitação manual da licença).
    5. Importa o arquivo OVA para o VirtualBox.
    6. Cria a pasta C:\mvt.
    7. Cria um atalho na área de trabalho para iniciar a VM importada como administrador.

.NOTAS
    Versão: 1.0
    Requisitos: PowerShell 5.1 ou superior, conexão com a Internet.
    Execute este script como Administrador.
#>

# --- Configuração ---
$vboxInstallerUrl = "https://download.virtualbox.org/virtualbox/7.1.0/VirtualBox-7.1.0-164728-Win.exe" # Exemplo de URL - Use o correto
$vboxExtPackUrl = "https://download.virtualbox.org/virtualbox/7.1.0/Oracle_VirtualBox_Extension_Pack-7.1.0-164728.vbox-extpack" # Exemplo de URL - Use o correto
$ovaUrl = "https://drive.usercontent.google.com/download?id=1jDc-UsDf-JoNSF4d0r-tC3hVN3xp6l1a&export=download&confirm=t&uuid=950085c4-9f84-45dd-b231-3a1195e83de2" 

# --- Outras Configurações ---
$vmName = "MVT" # Escolha um nome para sua VM importada
$targetFolder = "C:\mvt"
$downloadDir = Join-Path $env:TEMP "vbox_setup_downloads"
$vboxInstallPath = "C:\Program Files\Oracle\VirtualBox"
$vboxManageExe = Join-Path $vboxInstallPath "VBoxManage.exe"
$ovaFileName = "MVT.ova"
# --- Fim da Configuração ---

# --- Funções Auxiliares ---

Function Test-IsAdmin {
    $currentUser = New-Object Security.Principal.WindowsPrincipal $([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
}

Function Download-FileWithProgress {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Url,
        [Parameter(Mandatory=$true)]
        [string]$DestinationFolder,
        [Parameter(Mandatory=$true)]
        [string]$FileName
    )

    $destinationPath = Join-Path $DestinationFolder $FileName
    Write-Host "Baixando $FileName de $Url..." -ForegroundColor Yellow

    # Garante que o diretório de destino existe
    if (-not (Test-Path $DestinationFolder -PathType Container)) {
        Write-Verbose "Criando diretório de download: $DestinationFolder"
        New-Item -Path $DestinationFolder -ItemType Directory -Force | Out-Null
    }

    # Usa BITS para melhor manuseio de arquivos grandes e progresso
    try {
        Import-Module BitsTransfer -ErrorAction Stop
        Write-Host "Iniciando transferência BITS..."
        Start-BitsTransfer -Source $Url -Destination $destinationPath -Asynchronous -DisplayName "Baixando $FileName" | Out-Null

        $job = Get-BitsTransfer -Name "Baixando $FileName"
        while ($job.JobState -in @("Transferring", "Connecting")) {
            $percentComplete = [math]::Round(($job.BytesTransferred / $job.BytesTotal) * 100)
            $mbTransferred = [math]::Round($job.BytesTransferred / 1MB, 2)
            $mbTotal = [math]::Round($job.BytesTotal / 1MB, 2)
            Write-Progress -Activity "Baixando $FileName" -Status "$percentComplete% Completo ($mbTransferred MB / $mbTotal MB)" -PercentComplete $percentComplete
            Start-Sleep -Seconds 1
        }
        Write-Progress -Activity "Baixando $FileName" -Completed

        if ($job.JobState -eq "Transferred") {
            Complete-BitsTransfer -BitsJob $job
            Write-Host "`nDownload concluído: $destinationPath" -ForegroundColor Green
            return $destinationPath
        } else {
            Write-Error "O trabalho BITS falhou ou foi cancelado. Estado: $($job.JobState)"
            Remove-BitsTransfer -BitsJob $job -Confirm:$false
            return $null
        }
    } catch {
        Write-Warning "Módulo de Transferência BITS não disponível ou falhou: $($_.Exception.Message). Usando Invoke-WebRequest (sem barra de progresso)."
        try {
            Invoke-WebRequest -Uri $Url -OutFile $destinationPath -TimeoutSec 300 # Timeout de 5 minutos
            Write-Host "Download concluído (via Invoke-WebRequest): $destinationPath" -ForegroundColor Green
            return $destinationPath
        } catch {
            Write-Error "Erro ao baixar $FileName usando Invoke-WebRequest: $($_.Exception.Message)"
            return $null
        }
    }
}

Function Run-Process {
    param(
        [Parameter(Mandatory=$true)]
        [string]$FilePath,
        [string]$ArgumentList,
        [switch]$Wait = $true,
        [switch]$HideWindow = $false # Adicionada opção para ocultar janelas de console para instalações silenciosas
    )

    Write-Host "Executando: $FilePath $ArgumentList" -ForegroundColor Cyan
    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = $FilePath
    $startInfo.Arguments = $ArgumentList
    $startInfo.UseShellExecute = $true # Necessário para /S frequentemente, e para elevação posterior, se necessário

    if ($HideWindow) {
        $startInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
    }

    try {
        $process = [System.Diagnostics.Process]::Start($startInfo)
        if ($process -ne $null -and $Wait) {
            Write-Host "Aguardando a conclusão do processo..."
            $process.WaitForExit()
            Write-Host "Processo saiu com código: $($process.ExitCode)"
            # Verifica códigos de sucesso comuns
            if ($process.ExitCode -ne 0) {
                 # Adicione outros códigos de sucesso conhecidos, se necessário, por exemplo, 3010 para reinicialização necessária
                 if ($process.ExitCode -ne 3010) {
                    Write-Warning "Processo saiu com código diferente de zero: $($process.ExitCode). Verifique os logs se a instalação falhou."
                    # Considere lançar um erro aqui se um código diferente de zero sempre significar falha
                    # throw "Processo falhou com código de saída $($process.ExitCode)"
                 } else {
                    Write-Warning "Processo requer reinicialização (Código de Saída 3010)."
                 }
            }
            return $process.ExitCode # Retorna código de saída
        } elseif ($process -eq $null) {
            Write-Error "Falha ao iniciar o processo: $FilePath"
            return -1 # Indica falha
        }
        return 0 # Indica sucesso se não estiver aguardando ou se o processo foi iniciado corretamente
    } catch {
        Write-Error "Erro ao executar o processo '$FilePath': $($_.Exception.Message)"
        return -1 # Indica falha
    }
}

# --- Lógica Principal do Script ---

# 1. Verifica privilégios de Administrador (Tratado por #Requires -RunAsAdministrator no topo)
# Se não for executado como administrador, o PowerShell solicitará ou falhará antes da execução do script.
Write-Host "Executando com privilégios de Administrador." -ForegroundColor Green

# 2. Baixar Arquivos
Write-Host "`n--- Baixando Arquivos (para $downloadDir) ---" -ForegroundColor Magenta
$vboxInstallerPath = Download-FileWithProgress -Url $vboxInstallerUrl -DestinationFolder $downloadDir -FileName ($vboxInstallerUrl -split '/')[-1]
$vboxExtPackPath = Download-FileWithProgress -Url $vboxExtPackUrl -DestinationFolder $downloadDir -FileName ($vboxExtPackUrl -split '/')[-1]
$ovaPath = Download-FileWithProgress -Url $ovaUrl -DestinationFolder $downloadDir -FileName $ovaFileName

if (-not ($vboxInstallerPath -and $vboxExtPackPath -and $ovaPath)) {
    Write-Error "Um ou mais downloads falharam. Saindo."
    # Opcional: Adicione limpeza aqui se desejado, mesmo em caso de falha
    if (Test-Path $downloadDir -PathType Container) { Remove-Item -Path $downloadDir -Recurse -Force }
    exit 1
}

# 3. Instalar VirtualBox
Write-Host "`n--- Instalando VirtualBox ---" -ForegroundColor Magenta
# Use /S para instalação silenciosa. Pode precisar de outros parâmetros dependendo da versão do instalador.
$installExitCode = Run-Process -FilePath $vboxInstallerPath -ArgumentList "/S" -Wait -HideWindow
# Verificação básica - VBoxManage deve existir após a instalação
Start-Sleep -Seconds 10 # Dá mais tempo para o instalador concluir tarefas em segundo plano
if (-not (Test-Path $vboxManageExe -PathType Leaf)) {
     Write-Error "A instalação do VirtualBox pode ter falhado (VBoxManage.exe não encontrado no local esperado: $vboxManageExe). Código de Saída: $installExitCode. Saindo."
     exit 1
} else {
     Write-Host "Comando de instalação do VirtualBox concluído. VBoxManage encontrado." -ForegroundColor Green
}


# 4. Instalar VirtualBox Extension Pack
Write-Host "`n--- Instalando VirtualBox Extension Pack ---" -ForegroundColor Magenta
if (-not (Test-Path $vboxManageExe -PathType Leaf)) {
    Write-Error "VBoxManage.exe não encontrado em $vboxManageExe. Não é possível instalar o Extension Pack. Pulando."
} else {
    Write-Host "Tentando instalar o Extension Pack: $vboxExtPackPath"
    Write-Host "NOTA: Você pode ver uma janela separada ou um prompt para aceitar o contrato de licença." -ForegroundColor Yellow
    # Tenta instalação silenciosa primeiro (pode ou não funcionar dependendo da versão do VBox)
    # Usar --accept-license=... é preferível se sua versão do VBox suportar
    # $extInstallArgs = "extpack install --replace --accept-license=sha256_of_license_text `"$vboxExtPackPath`"" # Exemplo se o hash da licença for conhecido/suportado
    $extInstallArgs = "extpack install --replace `"$vboxExtPackPath`"" # Abordagem padrão

    # Executa VBoxManage. Pode aparecer uma GUI para a licença.
    # Não usamos -HideWindow aqui para que o usuário possa ver o prompt da licença, se aparecer.
    $extPackExitCode = Run-Process -FilePath $vboxManageExe -ArgumentList $extInstallArgs -Wait

    # Verifica se o pack está listado (verificação básica)
    $extPacks = & $vboxManageExe list extpacks
    if ($extPacks -match ([System.IO.Path]::GetFileNameWithoutExtension($vboxExtPackPath) -replace '_',' ')) {
         Write-Host "VirtualBox Extension Pack instalado com sucesso." -ForegroundColor Green
    } else {
         Write-Warning "Comando de instalação do Extension Pack concluído (Código de Saída: $extPackExitCode), mas a verificação falhou ou a licença pode precisar de aceitação manual."
         Write-Warning "Por favor, verifique a GUI do VirtualBox (Arquivo -> Ferramentas -> Gerenciador de Extension Pack) para confirmar."
    }
}

# 5. Importar OVA
Write-Host "`n--- Importando OVA ---" -ForegroundColor Magenta
if (-not (Test-Path $vboxManageExe -PathType Leaf)) {
    Write-Error "VBoxManage.exe não encontrado em $vboxManageExe. Não é possível importar OVA. Pulando."
} elseif (-not (Test-Path $ovaPath -PathType Leaf)) {
    Write-Error "Arquivo OVA não encontrado em $ovaPath. Não é possível importar. Pulando."
} else {
    Write-Host "Importando OVA '$((Get-Item $ovaPath).Name)' como VM '$vmName'..."
    # Adicione outras opções como --memory, --cpus se necessário: --vsys 0 --memory 2048 --cpus 2
    $importArgs = "import `"$ovaPath`" --vsys 0 --vmname `"$vmName`""
    $importExitCode = Run-Process -FilePath $vboxManageExe -ArgumentList $importArgs -Wait

    # Verifica a importação verificando se a VM existe
    $vmList = & $vboxManageExe list vms
    if ($vmList -match """$vmName""") {
        Write-Host "OVA importado com sucesso como '$vmName'." -ForegroundColor Green
    } else {
        Write-Error "Comando de importação do OVA concluído (Código de Saída: $importExitCode), mas a VM '$vmName' não foi encontrada na lista. Importação falhou."
        # Opcional: Saia se a importação for crítica
        # exit 1
    }
}

# 6. Criar Pasta de Destino
Write-Host "`n--- Criando Pasta de Destino ---" -ForegroundColor Magenta
try {
    if (-not (Test-Path $targetFolder -PathType Container)) {
        New-Item -Path $targetFolder -ItemType Directory -Force | Out-Null
        Write-Host "Pasta criada: $targetFolder" -ForegroundColor Green
    } else {
        Write-Host "Pasta já existe: $targetFolder" -ForegroundColor Green
    }
} catch {
    Write-Error "Falha ao criar pasta ${targetFolder}: $($_.Exception.Message)"
    # Opcional: Saia se a pasta for crítica
    # exit 1
}

# 7. Criar Atalho na Área de Trabalho
Write-Host "`n--- Criando Atalho na Área de Trabalho ---" -ForegroundColor Magenta
if (-not (Test-Path $vboxManageExe -PathType Leaf)) {
    Write-Error "VBoxManage.exe não encontrado em $vboxManageExe. Não é possível criar atalho."
} else {
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = Join-Path $desktopPath "$vmName.lnk"
    $targetExe = "powershell.exe"
    # Escapa aspas cuidadosamente para o comando aninhado
    $arguments = "-Command `"Start-Process -FilePath '$vboxManageExe' -ArgumentList 'startvm', '$vmName' -Verb RunAs`""
    $iconLocation = Join-Path $vboxInstallPath "VirtualBox.exe,0" # Índice de ícone 0

    try {
        $wshell = New-Object -ComObject WScript.Shell
        $shortcut = $wshell.CreateShortcut($shortcutPath)
        $shortcut.TargetPath = $targetExe
        $shortcut.Arguments = $arguments
        $shortcut.IconLocation = $iconLocation
        $shortcut.Description = "Iniciar VM do VirtualBox $vmName como Administrador"
        # $shortcut.WorkingDirectory = $vboxInstallPath # Opcional: Defina o diretório de trabalho, se necessário
        $shortcut.Save()

        Write-Host "Atalho criado com sucesso em: $shortcutPath" -ForegroundColor Green
        Write-Host "Nota: Iniciar o atalho acionará um prompt UAC para direitos de administrador." -ForegroundColor Yellow
    } catch {
        Write-Error "Erro ao criar atalho: $($_.Exception.Message)"
    }
}

# 8. Limpeza
Write-Host "`n--- Limpando arquivos baixados ---" -ForegroundColor Magenta
if (Test-Path $downloadDir -PathType Container) {
    Write-Host "Removendo diretório de download temporário: $downloadDir"
    Remove-Item -Path $downloadDir -Recurse -Force -ErrorAction SilentlyContinue
    if (Test-Path $downloadDir -PathType Container) {
         Write-Warning "Não foi possível remover completamente o diretório de download temporário: $downloadDir"
    } else {
         Write-Host "Limpeza bem-sucedida." -ForegroundColor Green
    }
} else {
    Write-Host "Diretório de download não encontrado, pulando limpeza."
}

Write-Host "`n------------------------------------" -ForegroundColor Cyan
Write-Host "Processo de configuração concluído!" -ForegroundColor Cyan
Write-Host "VM '$vmName' deve estar importada (verifique no VirtualBox)." -ForegroundColor Cyan
Write-Host "Pasta '$targetFolder' criada." -ForegroundColor Cyan
Write-Host "Atalho '$vmName.lnk' criado na sua área de trabalho (requer admin para executar)." -ForegroundColor Cyan
Write-Host "------------------------------------" -ForegroundColor Cyan
