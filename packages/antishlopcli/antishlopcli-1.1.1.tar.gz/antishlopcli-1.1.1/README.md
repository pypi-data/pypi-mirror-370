# AntishlopCLI

AI-powered security vulnerability scanner for source code.

## Installation

```bash
pip install antishlopcli
```

## Quick Start

1. Set your OpenAI API key:
```bash
antishlop --set-key sk-your-openai-api-key-here
```

2. Scan your code:
```bash
antishlop /path/to/your/code
```

## Features

- Pattern detection for common vulnerabilities
- AI-powered context analysis 
- OWASP/CWE compliance mapping
- JSON output for automation

## Usage

```bash
# Scan current directory
antishlop .

# JSON output
antishlop --output json ./src
```

## Requirements

- Python 3.8+
- OpenAI API key

## Disclaimer

This tool is provided "AS IS" for educational and defensive security purposes only. The author is not liable for any damages, legal issues, or consequences arising from its use. Users are solely responsible for ensuring they have proper authorization before scanning any codebase and for complying with all applicable laws and regulations.

## License

MIT License - see LICENSE file for details.