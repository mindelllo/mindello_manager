"""MatterListener module.

detects and lists Matter devices on the local network using Zeroconf and Scapy.
"""

import logging
from typing import Any

import requests
from requests.auth import HTTPBasicAuth
from scapy.all import conf, srp
from scapy.error import Scapy_Exception
from scapy.layers.l2 import ARP, Ether
from zeroconf import ServiceListener, Zeroconf

HTTP_STATUS_OK = 200

_LOGGER = logging.getLogger("matterlistener")


class MatterListener(ServiceListener):
    """Listener for detecting and listing Matter devices on the local network.

    This class listens for Zeroconf service events and attempts to identify
    Matter devices by probing their network information and HTTP authentication.
    Detected devices are stored in the `devices` attribute as dictionaries
    containing relevant information such as name, address, MAC address, and
    authentication status.
    """

    def __init__(self) -> None:
        """Initialize the MatterListener with an empty devices list."""
        self.devices: list[dict[str, Any]] = []

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        """Handle removal of a Zeroconf service (not needed for listing).

        Args:
            zc (Zeroconf): The Zeroconf instance.
            type_ (str): The service type.
            name (str): The service name.

        """

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        """Handle update of a Zeroconf service (not implemented).

        Args:
            zc (Zeroconf): The Zeroconf instance.
            type_ (str): The service type.
            name (str): The service name.

        """

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        """Handle addition of a Zeroconf service and attempt to identify device.

        Args:
            zc (Zeroconf): The Zeroconf instance.
            type_ (str): The service type.
            name (str): The service name.

        """
        info = zc.get_service_info(type_, name)
        if info is None:
            _LOGGER.warning("Informação do serviço %s não encontrada", name)
            return

        try:
            addresses = info.parsed_addresses()
        except (AttributeError, ValueError):
            addresses = []
        address = addresses[0] if addresses else "N/A"

        mac_address: str = "N/A"
        sn: str = "N/A"
        if address != "N/A":
            try:
                conf.verb = 0
                ans, _ = srp(
                    Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=address),
                    timeout=2,
                    retry=1,
                )
                for _, rcv in ans:
                    mac_address = rcv.sprintf("%Ether.src%")
                    break
            except Scapy_Exception as e:
                _LOGGER.warning("Erro ao obter MAC address para %s: %s", address, e)

        http_on_80 = False
        http_auth_ok = False
        http_status = 0
        if (
            address != "N/A"
            and mac_address != "N/A"
            and len(mac_address.split(":")) == 6  # noqa: PLR2004
        ):
            try:
                mac_parts = mac_address.split(":")
                last4 = "".join([p.upper() for p in mac_parts[2:]])
                sn = f"FALLR1-{last4}"
                url = f"http://{address}:80/"
                response = requests.get(
                    url,
                    auth=HTTPBasicAuth("admin", sn),
                    timeout=2,
                )
                if response.status_code == requests.codes["ok"]:
                    http_auth_ok = True

            except requests.RequestException:
                http_on_80 = False
        device: dict[str, str | bool | int] = {
            "name": name,
            "address": address,
            "sn": sn,
            "port": getattr(info, "port", "N/A"),
            "mac_address": mac_address,
            "http_on_80": http_on_80,
            "http_auth_ok": http_auth_ok,
            "http_status": http_status,
        }

        if http_auth_ok and not any(
            d["mac_address"] == mac_address for d in self.devices
        ):
            self.devices.append(device)
            _LOGGER.info(
                "FALL-R1 encontrado: http://%s | SN: %s",
                device["address"],
                device["sn"],
            )
