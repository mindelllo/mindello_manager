"""Main module for detecting and listing Matter devices on the local network.

This script checks for administrative/root privileges, sets up logging, and
initializes a Zeroconf service browser to detect Matter devices on the local
network using the MatterListener class.
"""

import logging
import os
import platform
import sys

from colorlog import ColoredFormatter
from zeroconf import ServiceBrowser, Zeroconf

from .matterlistener import MatterListener

_LOGGER = logging.getLogger("main")

LOG_FORMAT = (
    "%(asctime)s.%(msecs)03d %(levelname)s (%(threadName)s) [%(name)s] %(message)s"
)


def main() -> None:
    """Detect and list Matter devices on the local network.

    Checks for administrative/root privileges, configures logging, and starts
    a Zeroconf service browser to discover Matter devices. The function blocks
    until the user presses Enter or interrupts with Ctrl+C.
    """
    # Verifica se está rodando como root/admin de forma agnóstica
    is_admin: bool = False
    if platform.system() == "Windows":
        try:
            import ctypes

            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0  # type: ignore  # noqa: PGH003
        except OSError:
            is_admin = False
            _LOGGER.warning(
                "Este script precisa ser executado como administrador."
                " Tentando reiniciar com privilégios...",
            )
            try:
                # Reinvoca o script com privilégios de admin no Windows
                params = " ".join([f'"{arg}"' for arg in sys.argv])
                ctypes.windll.shell32.ShellExecuteW(  # type: ignore  # noqa: PGH003
                    None,
                    "runas",
                    sys.executable,
                    params,
                    None,
                    1,
                )
            except Exception:
                _LOGGER.exception(
                    "Falha ao tentar obter privilégios de administrador. Saindo...",
                )
            sys.exit(1)
    else:
        is_admin = os.geteuid() == 0
        if not is_admin:
            _LOGGER.warning(
                "Este script precisa ser executado como root. "
                "Tentando reiniciar com sudo...",
            )
            try:
                os.execvp("sudo", ["sudo", sys.executable, *sys.argv])  # noqa: S606, S607
            except Exception:
                _LOGGER.exception(
                    "Falha ao tentar obter privilégios de root. Saindo...",
                )
            sys.exit(1)
    _LOGGER.info("Procurando dispositivos Matter na rede local...")
    zeroconf = Zeroconf()
    listener = MatterListener()
    # O tipo de serviço padrão para Matter é _matter._tcp.local.
    ServiceBrowser(zeroconf, "_matter._tcp.local.", listener)
    try:
        input("Pressione Enter para encerrar a busca...\n")
    except KeyboardInterrupt:
        pass
    finally:
        _LOGGER.info("Busca finalizada.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fmt = LOG_FORMAT
    colorfmt = f"%(log_color)s{fmt}%(reset)s"
    logging.getLogger().handlers[0].setFormatter(
        ColoredFormatter(
            colorfmt,
            datefmt="%Y-%m-%d %H:%M:%S",
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red",
            },
        ),
    )
    main()
