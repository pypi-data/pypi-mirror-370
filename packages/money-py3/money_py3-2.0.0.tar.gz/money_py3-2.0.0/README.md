# Money-Py3: Modern Python Money Library

A modern Python 3.9+ money handling library with currency exchange support and optional locale-aware formatting.

This is a modernized fork of the original [`money`](https://github.com/carlospalol/money) package by **Carlos Palol**, completely rewritten for Python 3.9+ with all Python 2 compatibility code removed.

## Features

- **Python 3.9+ only** - Modern, clean codebase
- **Decimal precision** - No floating-point arithmetic errors
- **Currency exchange** - Extensible exchange rate backends
- **Locale-aware formatting** - Optional CLDR formatting via Babel
- **Immutable objects** - Thread-safe money objects
- **Type hints ready** - Modern Python development

## Installation

### Using pip:
```bash
pip install money-py3
```

For locale-aware formatting support:
```bash
pip install money-py3[formatting]
```

### Using Poetry:
```bash
poetry add money-py3
```

For locale-aware formatting support:
```bash
poetry add money-py3[formatting]
```

## Quick Start

```python
from money import Money, XMoney, xrates
from money.exchange import SimpleBackend
from decimal import Decimal

# Basic usage
price = Money('10.50', 'USD')
tax = Money('0.98', 'USD')
total = price + tax
print(total)  # USD 11.48

# Currency exchange
xrates.install(SimpleBackend)
xrates.base = 'USD'
xrates.setrate('EUR', Decimal('0.85'))

eur_total = total.to('EUR')
print(eur_total)  # EUR 9.76

# XMoney with automatic conversion
x1 = XMoney('10', 'USD')
x2 = XMoney('5', 'EUR')  
result = x1 + x2  # Automatically converts EUR to USD
print(result)  # USD 15.88
```

## Requirements

- Python 3.9+
- `packaging` (automatically installed)
- `babel` (optional, for formatting)

## License

MIT License - see original project for details.

## Credits

This package is based on the original [`money`](https://github.com/carlospalol/money) library by **Carlos Palol** (carlos.palol@awarepixel.com), modernized for Python 3.9+.

### Original Project
- **Author**: Carlos Palol
- **Original Repository**: https://github.com/carlospalol/money
- **License**: MIT

### Modernization by Fever
This modernized version is maintained by **Fever** (https://github.com/feverup/).

**Changes made**:
- Removed all Python 2 compatibility code (six library)
- Updated to use modern Python 3.9+ features
- Replaced deprecated imports with current alternatives
- Improved packaging configuration
- Updated dependencies to current versions

**Contact**: engineering@feverup.com