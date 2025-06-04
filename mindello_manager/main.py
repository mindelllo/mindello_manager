import requests
from requests.auth import HTTPBasicAuth
from zeroconf import Zeroconf, ServiceBrowser, ServiceListener
from typing import Any
from scapy.all import srp, conf
from scapy.layers.l2 import Ether, ARP
import os
import sys
import platform
from .matterlistener import MatterListener

def main():
    # Verifica se está rodando como root/admin de forma agnóstica
    is_admin: bool = False
    if platform.system() == "Windows":
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0  # type: ignore
        except Exception:
            is_admin = False
        if not is_admin:
            print("Este script precisa ser executado como administrador. Tentando reiniciar com privilégios...")
            try:
                # Reinvoca o script com privilégios de admin no Windows
                params = ' '.join([f'\"{arg}\"' for arg in sys.argv])
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            except Exception:
                print("Falha ao tentar obter privilégios de administrador. Saindo...")
            sys.exit(1)
    else:
        is_admin = (os.geteuid() == 0)
        if not is_admin:
            print("Este script precisa ser executado como root. Tentando reiniciar com sudo...")
            try:
                os.execvp('sudo', ['sudo', sys.executable] + sys.argv)
            except Exception:
                print("Falha ao tentar obter privilégios de root. Saindo...")
            sys.exit(1)
    print("Procurando dispositivos Matter na rede local...")
    zeroconf = Zeroconf()
    listener = MatterListener()
    # O tipo de serviço padrão para Matter é _matter._tcp.local.
    browser = ServiceBrowser(zeroconf, "_matter._tcp.local.", listener)
    try:
        input("Pressione Enter para encerrar a busca...\n")
    except KeyboardInterrupt:
        pass
    finally:
        zeroconf.close()
        print("Busca finalizada.")

if __name__ == "__main__":
    main()
