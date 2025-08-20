# PyTTD - Python OpenTTD Client Library

[![PyPI version](https://img.shields.io/pypi/v/pyttd.svg)](https://pypi.org/project/pyttd/)
[![Python versions](https://img.shields.io/pypi/pyversions/pyttd.svg)](https://pypi.org/project/pyttd/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Finally, a Python client library for connecting to [OpenTTD](https://www.openttd.org/) servers **as a player**, issuing **commands**, observing **game state** and **parsing maps**! Create bots, manage companies, and interact with OpenTTD games programmatically  **with real-time data** and **without admin port access**.

## Features

| Feature                         | Status                                                                   | Remarks
|---------------------------------|--------------------------------------------------------------------------|------------------------------------------
| Multiplayer protocol            | ![Done](https://img.shields.io/badge/status-done-brightgreen)            | -                                       |
| Commands                        | ![Done](https://img.shields.io/badge/status-done-brightgreen)            | Might have missed something             |
| Game state                      | ![Done](https://img.shields.io/badge/status-done-brightgreen)            | Might have missed something             |
| Save file parsing               | ![In Progress](https://img.shields.io/badge/status-in%20progress-yellow) | Game data and companies work            |
| High level functions            | ![In Progress](https://img.shields.io/badge/status-in%20progress-yellow) | Helpers for common high-level tasks     |

## Requirements

- **Python**: 3.11 or higher
- **OpenTTD Server**: Tested with 14.1

## Installation

### From PyPI (Recommended)

```bash
pip install pyttd
```

### From Source

```bash
git clone https://github.com/mssc89/pyttd.git
cd pyttd
pip install -e .
```

## Quick Start

```python
from pyttd import OpenTTDClient

# Connect to OpenTTD server
client = OpenTTDClient("127.0.0.1", 3979, player_name="MyBot")
client.connect()

# Get real-time game information
game_info = client.get_game_info()
print(f"Game Year: {game_info['current_year']}")
print(f"Companies: {game_info['companies']}/{game_info['companies_max']}")
print(f"Clients: {game_info['clients']}/{game_info['clients_max']}")

# Company management
if client.get_our_company():
    finances = client.get_company_finances()
    print(f"Money: £{finances['money']:,}")
    print(f"Loan: £{finances['loan']:,}")
    
    # Take a loan and send a status message
    client.increase_loan(50000)
    client.send_chat("Bot taking loan for expansion!")

# Clean disconnect
client.disconnect()
```

### Save File Parsing

PyTTD includes a save file parser module that can extract detailed game data from OpenTTD save files.

```python
from pyttd import load_save_file

# Parse a save file
game_data = load_save_file("path/to/savefile.sav")

# Access parsed data
print(f"Save version: {game_data['meta']['save_version']}")
print(f"Map size: {game_data['statistics']['map_size']}")
print(f"Companies: {game_data['statistics']['companies_count']}")

# Company information with financial data
for company in game_data['companies']:
    print(f"{company['name']}: £{company['money']:,} (AI: {company['is_ai']})")
    
# Game date and economy
date = game_data['game']['date']['calendar_date']
print(f"Game date: {date['year']}-{date['month']}-{date['day']}")

economy = game_data['game']['economy']
print(f"Interest rate: {economy['interest_rate']}%")
```

## Examples

### Data Monitor
```bash
python examples/data_display.py
```
Displays all available real-time game state information.

### Chat Bot
```bash
python examples/chat_bot.py  
```
Basic example showing connection, company creation, and chat interaction.

### Company Manager
```bash
python examples/manager_bot.py
```
Demonstrates company management features and financial tracking.

### Financial Manager
```bash
python examples/finance_bot.py
```
Interactive financial management with chat-based commands.

### Save File Parser
```bash
python examples/save_file_parser.py path/to/savefile.sav
```
Parse OpenTTD save files to extract game data including companies, map information, and economic data. All in a clean JSON file!

## API Reference

### OpenTTDClient

The main client class for connecting to OpenTTD servers.

```python
client = OpenTTDClient(
    server="127.0.0.1",        # Server IP address
    port=3979,                 # Server port  
    player_name="MyBot",       # Your bot's name
    company_name="MyCompany"   # Company name (auto-created)
)
```

#### Connection Methods
- `client.connect()` - Connect to server and join game
- `client.disconnect()` - Clean disconnect from server
- `client.is_connected()` - Check connection status

#### Game Information
- `client.get_game_info()` - Game state information
- `client.get_map_info()` - Map size and terrain data  
- `client.get_economic_status()` - Economic indicators

#### Company Management
- `client.get_companies()` - List all companies
- `client.get_our_company()` - Our company information
- `client.get_company_finances()` - Financial data
- `client.get_company_performance()` - Performance metrics

#### Financial Operations
- `client.increase_loan(amount)` - Increase company loan
- `client.decrease_loan(amount)` - Decrease company loan  
- `client.give_money(amount, company)` - Transfer money
- `client.can_afford(amount)` - Check affordability

#### Company Customization
- `client.rename_company(name)` - Change company name
- `client.rename_president(name)` - Change manager name
- `client.set_company_colour(scheme, primary, colour)` - Change colors

#### Communication
- `client.send_chat(message)` - Send public chat message
- `client.send_chat_to_company(message, company_id)` - Company chat

#### Maps
TODO: describe it here


## Development

### Setting up Development Environment

```bash
git clone https://github.com/mssc89/pyttd.git
cd pyttd

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black pyttd/
flake8 pyttd/

# Type checking
mypy pyttd/
```

## Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/mssc89/pyttd/issues)
- **Documentation**: [Full API documentation](https://github.com/mssc89/pyttd#readme)
- **Examples**: [Comprehensive examples](https://github.com/mssc89/pyttd/tree/main/examples)
