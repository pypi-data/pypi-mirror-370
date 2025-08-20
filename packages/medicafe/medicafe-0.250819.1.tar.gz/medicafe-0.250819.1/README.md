# MediCafe

MediCafe is a small toolkit that helps automate common Medisoft admin tasks. It has two parts:

- MediBot: automates routine data handling
- MediLink: moves claims and responses between payers and your system

The focus is simple: reduce manual steps, add reliable checks, and keep logs that make issues easy to trace.

## Features
- Command-line entry point: `medicafe`
- Basic claim routing and status checks
- Lightweight utilities for importing, validation, and file handling
- Works on older Python 3.4 installs and modern environments

## Install
Use pip:

```
pip install medicafe
```

If you are on a system with managed Python, you may need a virtual environment:

```
python3 -m venv .venv
. .venv/bin/activate
pip install medicafe
```

## Quick start
Run the main entry point:

```
medicafe --help
```

Or from Python:

```
python3 -m MediCafe --help
```

Common tasks:
- Download payer emails
- Submit or check claim status
- Run MediLink workflows

## Compatibility
- Python: 3.4+ (tested with legacy constraints), also runs on newer Python
- OS: Windows or Linux

## Project goals
- Keep the code straightforward and readable
- Respect older environments where needed
- Fail with clear, actionable messages

## License
MIT License. See `LICENSE`.

## Support
This is community-supported software. Open an issue on the project page if you run into a problem or have a small, concrete request. Please include your Python version, OS, and the exact command that failed.