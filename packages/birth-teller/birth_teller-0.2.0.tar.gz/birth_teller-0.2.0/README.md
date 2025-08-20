# Birth Teller

[![PyPI version](https://img.shields.io/pypi/v/birth-teller.svg)](https://pypi.org/project/birth-teller/)
[![License](https://img.shields.io/pypi/l/birth-teller.svg)](https://github.com/exeebit/birth-teller/blob/main/LICENSE)

**Birth Teller** is a lightweight Python library and optional CLI tool that calculates your age, birthday details, and the day of the week you were born. It supports full month names, 3-letter abbreviations, and numeric month input. Perfect for Python projects, scripts, or Django apps.

---

## Features

- Compute age in **years, months, weeks, days, hours, minutes, and seconds**  
- Determine the **day of the week** for any birthdate  
- Supports **full month names**, **3-letter abbreviations**, and **numeric month input**  
- Optional **CLI** for quick terminal usage  
- Fully **importable as a Python library** for projects like Django  

---

## Installation

```bash
pip install birth-teller
```

## Library Usage (Python / Django / Scripts)

```bash
from birth_teller import BTM

# Create an instance
btm = BTM()

# Get birthday information
info = btm.information(8, "feb", 1999)

print(f"You were born on {info['weekDay']}")
print(f"Age in years: {info['years']}")
print(f"Age in days: {info['days']}")
```

### Using different month formats
```bash
# Full month name
info = btm.information(8, "February", 1999)

# 3-letter abbreviation
info = btm.information(8, "feb", 1999)

# Numeric month
info = btm.information(8, 2, 1999)
```
> [!NOTE]
> Works anywhere in Python, including Django views, scripts, or APIs.

### CLI Usage (Optional)
```bash
birth-teller --name Emran --day 8 --month feb --year 1999 // or
birth-teller -n Emran -d 8 -m feb -y 1999
```
### Example Output (CLI)

```bash
You were born on MONDAY
Years: 26
Days: 9690
Weeks: 1384
Zodiac Sign: Capricorn

```
