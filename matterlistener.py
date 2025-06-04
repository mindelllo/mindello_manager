from zeroconf import Zeroconf, ServiceListener
from typing import Any
from scapy.all import srp, conf
from scapy.layers.l2 import Ether, ARP
import requests
from requests.auth import HTTPBasicAuth

class MatterListener(ServiceListener):
    def __init__(self):
        self.devices: list[dict[str, Any]] = []

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        pass  # Não necessário para listagem

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        pass  # Não necessário para listagem

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        if info:
            try:
                addresses = info.parsed_addresses()
            except Exception:
                addresses = []
            address = addresses[0] if addresses else 'N/A'
            # Captura o MAC address usando scapy
            mac_address: str = 'N/A'
            sn: str = 'N/A'
            if address != 'N/A':
                try:
                    conf.verb = 0  # Silencia a saída do scapy
                    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=address), timeout=2, retry=1)
                    for _, rcv in ans:
                        mac_address = rcv.sprintf("%Ether.src%")
                        break
                except Exception:
                    pass
            # Verifica se há um servidor HTTP na porta 80 e tenta autenticar
            http_on_80 = False
            http_auth_ok = False
            http_status = None
            if address != 'N/A' and mac_address != 'N/A' and len(mac_address.split(':')) == 6:
                try:
                    # Gera a senha: FALLR1-XXXXXXXX (XXXXXXXX = 4 últimos octetos do MAC, sem ':', maiúsculo)
                    mac_parts = mac_address.split(':')
                    last4 = ''.join([p.upper() for p in mac_parts[2:]])
                    sn = f'FALLR1-{last4}'
                    url = f'http://{address}:80/'
                    response = requests.get(url, auth=HTTPBasicAuth('admin', sn), timeout=2)
                    http_on_80 = True
                    http_status = response.status_code
                    if response.status_code == 200:
                        http_auth_ok = True
                except Exception:
                    http_on_80 = False
            device = {
                'name': name,
                'address': address,
                'sn': sn,
                'port': getattr(info, 'port', 'N/A'),
                'mac_address': mac_address,
                'http_on_80': http_on_80,
                'http_auth_ok': http_auth_ok,
                'http_status': http_status
            }
            if http_auth_ok:
                # Evita duplicatas: só adiciona se não existir pelo endereço MAC
                if not any(d['mac_address'] == mac_address for d in self.devices):
                    self.devices.append(device)
                    print(f"FALL-R1 encontrado: http://{device['address']} | SN: {device['sn']}")
