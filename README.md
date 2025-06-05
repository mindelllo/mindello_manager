# Mindello Manager: Matter Device Scanner

This project is a Python application that detects and lists Matter devices present on the local network.

## How it works

- Uses Python libraries to discover Matter devices (e.g., chip-tool, py-matter, zeroconf, etc).
- Lists the devices found in the terminal.

## How to run

1. Create and activate the virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   python main.py
   ```

## Dependencies

- Python 3.8+
- py-matter (or alternative)
- zeroconf

## Notes

- Make sure you are on the same network as the Matter devices.
- If you do not find devices, check if they are turned on and accessible.
