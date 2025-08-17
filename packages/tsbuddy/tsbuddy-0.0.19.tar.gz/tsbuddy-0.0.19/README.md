![tsbuddy Avatar](https://raw.githubusercontent.com/bgbyte/tsbuddy/main/tsbuddy-img.png)

# Tech Support Buddy (`tsbuddy`)

[![PyPI version](https://badge.fury.io/py/tsbuddy.svg?cache=0)](https://badge.fury.io/py/tsbuddy)
<!-- Add other badges as appropriate: build status, coverage, etc. -->
<!-- e.g., [![Build Status](https://travis-ci.org/YOUR_USERNAME/tsbuddy.svg?branch=main)](https://travis-ci.org/YOUR_USERNAME/tsbuddy) -->

Tech Support Buddy is a versatile Python module built to improve network engineers' productivity. It provides a suite of Python utilities designed to efficiently diagnose technical issues, help resolve them, and facilitate automation. The main() function parses raw text into structured data, enabling automation and data-driven decision-making.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Example: Parsing Temperature Data](#example-1-parsing-temperature-data)
  - [SSH Example: Parsing System Information from SSH Command Output](#example-2-parsing-system-information-from-ssh-command-output)
  - [aosdl CLI Command](#aosdl-cli-command)
- [Future Enhancements (Ideas)](#future-enhancements-examples)
- [Contributing](#contributing)
- [Changelog](#changelog)

## Overview

Dealing with raw text output can be tedious and time-consuming. `tsbuddy` parsing aims to simplify this by providing tools to:

1.  **Extract** relevant sections from log files or command output.
2.  **Parse** this raw text into structured Python objects.
3.  **Enable** programmatic analysis and decision-making based on the parsed data.

This allows you to quickly turn unstructured command output into actionable insights. This package currently supports Alcatel-Lucent Enterprise's OmniSwitch. 

## Key Features

*   **Log Section Extraction:** Easily isolate specific command output or sections from larger support files.
*   **Structured Data Parsing:** Convert unstructured command output into Python objects for easy manipulation. (Examples below).
*   **Simplified Diagnostics:** Build custom logic on top of parsed data to automate checks, generate reports, trigger alerts or actions.
*   **Developer-Friendly:** Designed to be easily integrated into existing Python scripts and workflows.

## 🛎️ tsbuddy Interactive Menu & CLI Tools

Tech Support Buddy (`tsbuddy`) now includes an interactive menu and several CLI tools for common network support tasks. You can run the menu or any tool directly from the command line.

## Interactive Menu

Run the menu to access all major features:

```bash
tsbuddy
```

You'll see a menu like:

```
   ( ^_^)ノ  Hey there, tsbuddy is at your service!

 Skip this menu by running the CLI commands directly (in parentheses below), e.g. `ts-extract`.

=== 🛎️  ===
1. Get GA Build & Upgrade (aosga)
2. Run tech support gatherer (ts-get)
3. Run tech_support_complete.tar Extractor (ts-extract)
4. Run tech_support.log to CSV Converter (ts-csv)
5. Run swlog parser to CSV & JSON (ts-log)
6. Run AOS Upgrader (aosup)
7. Run AOS Downloader (aosdl)
8. Show help info

0. Exit  (つ﹏<)
```

Select an option by number, or run the CLI commands directly as shown in parentheses.

## CLI Commands

Each menu option is also available as a CLI command:

- `aosup` — Run AOS Upgrader
- `aosga` — Run GA Build Lookup
- `aosdl` — Run AOS Downloader
- `ts-extract` — Extract tech_support_complete.tar
- `ts-log` — Parse swlog to CSV & JSON
- `ts-csv` — Convert tech_support.log to CSV
- `ts-get` — Collect tech support file from a switch via SSH and download it to your local machine

### `ts-get` Command

The `ts-get` command connects to a switch via SSH, runs the tech support command, and downloads the resulting `tech_support_complete.tar` file to your local directory. It will prompt for device IP, username, and password, and will automatically handle file backup and cleanup on the device.

Example:
```bash
ts-get
```

Sample session:
```
Enter device IP [exit]: 10.1.1.1
Enter username for 10.1.1.1 [admin]: admin
Enter password for 10.1.1.1 [switch]:
Getting SN of 10.1.1.1.
Backing up existing file for 10.1.1.1
Downloaded existing tech_support_complete.tar as tech_support_complete_<serial>_<timestamp>_old.tar (size: 1234567 bytes)
Removed tech_support_complete.tar from /flash/
Connecting to 10.1.1.1 via SSH to run the tech support command
Command sent to switch
The file is still generating. Please wait...
The tech support files is ready. Beginning download
Downloaded new tech support file of size 2345678 bytes for 10.1.1.1
Removed tech_support_complete.tar from /flash/
Finished
```

The downloaded file will be named with the device serial number and timestamp for easy identification.

## Installation

You can install `tsbuddy` via pip:

```bash
pip install tsbuddy
```

## Usage

tsbuddy can be run directly from your preferred terminal. The command ts-csv will search for tech_support.log in your current directory & output its contents to a CSV.

```powershell
(venv) admin:~/tech_support_complete$ ts-csv
✅ CSV exported to parsed_sections_2025-05-30_220933.csv
```

Here's a basic example demonstrating how to use `tsbuddy` within Python to parse temperature information from command output. 

## Example 1: Parsing Temperature Data

For this example, we will use a file named `tech_support.log` in your working directory.

**1. Import `tsbuddy` and `pprint`:**

```python
import tsbuddy as ts
from pprint import pprint
```

**2. Read your log file:**

(For this example, we'll simulate reading from the file. `tsbuddy` itself can work on any source of text.)

```python
# Example content for 'tech_support.log' stored in the file_text variable
# This would typically be read from the actual file
file_text = """
Some initial lines...
show system, show chassis, etc

show temperature
Chassis/Device   Current Range      Danger Thresh Status
---------------- ------- ---------- ------ ------ ---------------
1/CMMA       47      15 to 60   68     60     UNDER THRESHOLD
3/CMMA       46      15 to 60   68     60     UNDER THRESHOLD
4/CMMA       46      15 to 60   68     60     UNDER THRESHOLD


Some other lines...
show ip interface, etc
...
"""
```
<!-- # If you were reading from a file:
# file = "tech_support.log"
# with open(file, encoding='utf-8') as f:
#     file_text = f.read()
-->

**3. Extract the relevant section:**

The `extract_section` function helps you get the raw text for a specific command or section.

```python
# Extract the section containing "show temperature" output
temp_section_text = ts.extract_section(file_text, "show temperature")

# print("--- Raw Extracted Text ---")
# print(temp_section_text)
## Seen above, without other section output
```

**4. Parse the raw text into a structured format:**

`tsbuddy` provides parsers for specific commands. Here, we use `parse_temperature`.

```python
# Parse the raw temperature text to structured data
parsed_temps = ts.parse_temperature(temp_section_text)

print("--- Parsed Temperature Data ---")
pprint(parsed_temps, sort_dicts=False)
```

This will output:

```
--- Parsed Temperature Data ---
[{'Chassis/Device': '1/CMMA',
  'Current': '47',
  'Range': '15 to 60',
  'Danger': '68',
  'Thresh': '60',
  'Status': 'UNDER THRESHOLD'},
 {'Chassis/Device': '3/CMMA',
  'Current': '46',
  'Range': '15 to 60',
  'Danger': '68',
  'Thresh': '60',
  'Status': 'UNDER THRESHOLD'},
 {'Chassis/Device': '4/CMMA',
  'Current': '46',
  'Range': '15 to 60',
  'Danger': '68',
  'Thresh': '60',
  'Status': 'UNDER THRESHOLD'}]
```

**5. Work with the structured data:**

Now that the data is structured, you can easily access and process specific fields.

```python
# Request data from specific fields
print("\n--- Device Statuses ---")
for chassis in parsed_temps:
    print(chassis["Status"])
```

Output:

```
--- Device Statuses ---
UNDER THRESHOLD
UNDER THRESHOLD
UNDER THRESHOLD
```

**6. Add custom logic:**

You can build more complex logic based on the values of specific fields.

```python
print("\n--- Devices with Current Temperature greater than 46°C ---")
for chassis in parsed_temps:
    if int(chassis["Current"]) > 46:
        print(chassis["Chassis/Device"] + " is greater than 46°C")
```
<!--        pprint(chassis, sort_dicts=False)
-->

Output:

```
--- Devices with Current Temperature greater than 46°C ---
1/CMMA is greater than 46°C
```
<!--
{'Chassis/Device': '1/CMMA',
 'Current': '47',
 'Range': '15 to 60',
 'Danger': '68',
 'Thresh': '60',
 'Status': 'UNDER THRESHOLD'}
-->


## Example 2: Parsing System Information from SSH Command Output

This example shows how to use `tsbuddy` to parse the output of a command executed over SSH.

**1. Import necessary modules:**

```python
import tsbuddy as ts
import subprocess as sp
from pprint import pprint
```

**2. Execute the SSH command:**

We'll use `subprocess.run` to execute an SSH command and capture its output.

```python
# We will extract data from the "show system" command
command = 'ssh admin@10.255.121.24 "show system"'
result = sp.run(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE, text=True, check=True, timeout=30)

# The result object provides the stdout with the command output as raw text.
print("--- CompletedProcess Object ---")
print(result)
```

Expected output for `print(result)` (will vary based on your actual SSH output):
```
--- CompletedProcess Object ---
CompletedProcess(args='ssh admin@10.255.121.24 "show system"', returncode=0, stdout='System:\n  Description:  Alcatel-Lucent Enterprise OS6900-X40 8.9.94.R04 GA, March 28, 2024.,\n  Object ID:    1.3.6.1.4.1.6486.801.1.1.2.1.10.1.2,\n  Up Time:      120 days 21 hours 29 minutes and 0 seconds,\n  Contact:      Alcatel-Lucent Enterprise, https://www.al-enterprise.com,\n  Name:         OS6900-X40,\n  Location:     Unknown,\n  Services:     78,\n  Date & Time:  MON JUN 02 2025 19:23:22 (UTC)\nFlash Space:\n    Primary CMM:\n      Available (bytes):  1440706560,\n      Comments         :  None\n\n', stderr='')
```

**3. Access the raw output (`stdout`):**

```python
# Here is the stdout raw text
print("\n--- Raw stdout from SSH Command ---")
print(result.stdout)
```

Expected `result.stdout` (will vary based on your actual SSH output):
```
--- Raw stdout from SSH Command ---
System:
  Description:  Alcatel-Lucent Enterprise OS6900-X40 8.9.94.R04 GA, March 28, 2024.,
  Object ID:    1.3.6.1.4.1.6486.801.1.1.2.1.10.1.2,
  Up Time:      120 days 21 hours 29 minutes and 0 seconds,
  Contact:      Alcatel-Lucent Enterprise, https://www.al-enterprise.com,
  Name:         OS6900-X40,
  Location:     Unknown,
  Services:     78,
  Date & Time:  MON JUN 02 2025 19:23:22 (UTC)
Flash Space:
    Primary CMM:
      Available (bytes):  1440706560,
      Comments         :  None

```

**4. Parse the output using `tsbuddy`:**

```python
# Lets parse it and see the result
system_info = ts.parse_system(result.stdout)

print("\n--- Parsed System Information ---")
pprint(system_info, sort_dicts=False)
```

Output:
```
--- Parsed System Information ---
[{'Description': 'Alcatel-Lucent Enterprise OS6900-X40 8.9.94.R04 GA, March '
                 '28, 2024.',
  'Object ID': '1.3.6.1.4.1.6486.801.1.1.2.1.10.1.2',
  'Up Time': '120 days 21 hours 29 minutes and 0 seconds',
  'Contact': 'Alcatel-Lucent Enterprise, https://www.al-enterprise.com',
  'Name': 'OS6900-X40',
  'Location': 'Unknown',
  'Services': '78',
  'Date & Time': 'MON JUN 02 2025 19:23:22 (UTC)',
  'Primary CMM - Available (bytes)': '1440706560',
  'Primary CMM - Comments': 'None'}]
```

**5. Access specific data from the parsed output:**

```python
# Get the specific data you want, such as querying "Up Time"
print(system_info[0]["Up Time"])
```

Output:
```
120 days 21 hours 29 minutes and 0 seconds
```

## aosdl CLI Command

`aosdl` is a CLI command included in the `tsbuddy` module that facilitates downloading AOS images to OmniSwitch. It automates the process of connecting to the devices via SSH, identifying their platform family, and downloading the appropriate images from your local repo.

### Usage

Run the `aosdl` command directly from your terminal:

```powershell
(venv) admin:~/$ aosdl
```

This will prompt you to enter device details (IP, username, and password) and the AOS version. The script will then connect to the devices, identify their platform family, and download the appropriate images to their /flash/ directory.

### Example

```powershell
(venv) admin:~/$ aosdl
Enter device IP: 192.168.1.1
Enter username for 192.168.1.1 [admin]: admin
Enter password for 192.168.1.1 [switch]:
Connecting to 192.168.1.1...
[192.168.1.1] Platform family: shasta
[192.168.1.1] Downloading Uos.img...
[192.168.1.1] Downloaded Uos.img to /flash/
```

The `aosdl` command simplifies the process of pushing AOS images across multiple devices. For more details, see the [aosdl README](./src/aosdl/README.md).

## Future Enhancements (Examples)

The `tsbuddy` module is designed to be extensible. Future development could include:

*   Chatbot
*   More parsers for common log outputs (e.g., `show fabric`, `vrf ... show ...`, `debug show ...`).
*   Functions to compare states (e.g., before/after changes).
*   Integration with alerting systems.
*   Parse configuration.
*   Convert configurations.
*   Auto-detect parsing function.
*   Generate tech-support & validate generation.
*   Support outputting to .xlsx.
*   Support for different log formats & devices.
*   More sophisticated section extraction logic.

## Contributing

Contributions are welcome! If you have ideas for improvements or new features, or if you've found a bug, please feel free to:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/YourFeature` or `bugfix/YourBugfix`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/YourFeature`).
6.  Open a Pull Request.

Please ensure your code adheres to any existing style guidelines and includes tests where appropriate.

## Changelog

### 2025-08-08
- Added change directory feature.
- Fixed crash when extracting corrupted files; now errors are ignored.

### 2025-08-06
- Added get tech support feature.

### 2025-08-04
- Introduced interactive menu for easier navigation of `tsbuddy` features.
- Added interactive menu and CLI tool documentation to README.
- Linked CLI commands and menu options to their respective modules.
- Added this changelog section and linked it in the Table of Contents.
- Created CLI commands for common tasks: `aosup`, `aosga`, `ts-extract`, `ts-log`.

### 2025-05-30
- Initial release and documentation for tsbuddy core features and parsers.
- Added aosdl CLI documentation and usage examples.
- Added initial parsing functions for temperature and system information.
- Created CLI commands for common tasks: `aosdl`, `ts-csv`.
- Added extensibility for future parser and feature additions.
