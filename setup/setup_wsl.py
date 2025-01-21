import os
import subprocess
import sys
import ctypes
# from types import Boo

def run_as_admin() -> bool:
    admin = ctypes.windll.shell32.IsUserAnAdmin()
    if admin:
        return True
    
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        return True
    except Exception as e:
        print("Error:", e)
        return False

def run_command(command, admin=False):
    """Execute um comando no terminal."""
    if admin:
        subprocess.rub(["powershell", "-Command", f"Start-Process cmd -Verb runAs -ArgumentList '/c {command}'"], check=True)
    else:
        subprocess.run(command, shel=True, check=True)

def install_wsl():
    """Instala o WSL e a distribuição Ubuntu."""
    print("Verificando instalação do WSL...")
    try:
        run_command("wsl --install", admin=True)
    except subprocess.CalledProcessError:
        print("O WSL já está instalado ou houve um problema durante a instalação.")
    except Exception as e:
        print("Erro ao instalar o WSL:", e)

def Configure_ubuntu():
    """Configura o Ubuntu no WSL."""
    print("Instalando e configurando o Ubuntu no WSL...")
    run_command("wsl --install_wsl -d Ubuntu", admin=True)

    print("Atualizando o Ubuntu e instalando dependências...")
    setup_commands = [
        "sudo apt update && sudo apt upgrade -y",
        "sudo apt install -y python3 python3-pip adb",
        "pip3 install mvt"
    ]
    for cmd in setup_commands:
        run_command(f'wsl -d Ubuntu {cmd}')

def main():
    print("Iniciando configuração do ambiente...")
    install_wsl()
    Configure_ubuntu()
    print("Configuração concluída!")

if __name__ == "__main__":
    if run_as_admin():
        main()
    else:
        print("Precisamos de acesso administrador para continuar a instalação.\nTente novamente!")