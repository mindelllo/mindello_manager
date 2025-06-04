# Mindello Manager: Matter Device Scanner

Este projeto é um aplicativo Python que detecta e lista dispositivos Matter presentes na rede local.

## Como funciona
- Utiliza bibliotecas Python para descoberta de dispositivos Matter (ex: chip-tool, py-matter, zeroconf, etc).
- Lista os dispositivos encontrados no terminal.

## Como executar
1. Crie e ative o ambiente virtual:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Execute o app:
   ```bash
   python main.py
   ```

## Dependências
- Python 3.8+
- py-matter (ou alternativa)
- zeroconf

## Observações
- Certifique-se de estar na mesma rede dos dispositivos Matter.
- Caso não encontre dispositivos, verifique se eles estão ligados e acessíveis.
