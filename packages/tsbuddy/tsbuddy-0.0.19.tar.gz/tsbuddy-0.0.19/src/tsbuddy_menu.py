print("Loading tsbuddy menu...First run will take extra time.")
import os
import sys
import time

from src.tsbuddy import main as tsbuddy_main
#from src.extracttar.extracttar import main as extracttar_main
from src.extracttar.extract_all import main as extract_all_main
from src.aosdl.aosdl import main as aosdl_main, lookup_ga_build, aosup
from src.logparser import main as logparser_main
from src.get_techsupport import main as get_techsupport_main
from src.analyze.graph_hmon import main as graph_hmon_main
#from src.clean_pycache import clean_pycache_and_pyc


def print_help():
    help_text = """
\nHelp: Menu Option Details

1. Get GA Build & Upgrade (aosga):
   - Looks up the latest GA build for your switch and provides options for upgrading.
   - If you want a custom build, choose the AOS Upgrader (aosup) option to upgrade to a specific build.
   - If you only want to download an AOS image to /flash for later processing, use the AOS Downloader (aosdl) option.

2. Run tech support gatherer (ts-get):
   - Generates & gathers tech_support_complete.tar from your device, automating the collection process.

3. Run tech_support_complete.tar Extractor (ts-extract):
   - Extracts the contents of a tech_support_complete.tar archive, making logs and files accessible for analysis.
   - Use the legacy ts-extract-legacy command if you encounter issues with the new extractor.
   - The legacy extractor requires 7zip to be installed on your system and does not extract hmon data.

4. Run tech_support.log to CSV Converter (ts-csv):
   - Converts tech_support.log files into a CSV file for easier viewing and analysis.

5. Run swlog parser (to CSV & JSON) (ts-log):
   - Parses switch log & console log files and outputs the results in both CSV and JSON files.

6. Run AOS Upgrader (aosup):
   - Upgrades your OmniSwitch to the requested AOS build #, automating the upgrade process.

7. Run AOS Downloader (aosdl):
   - Downloads the requested AOS version to /flash for later processing.

8. Run HMON Graph Generator (graph-hmon):
   - Generates graphs from HMON data using the new script graph_hmon.py. Must be in the same directory as HMON data files.

9. Change current directory:
   - Allows you to view and change the current working directory. Lists available directories and files, and lets you navigate to a new directory for file operations.

10. Print Help (help):
   - Shows this help text describing each menu option in detail.
\n
"""
    print(help_text)
    time.sleep(1)  # Pause to allow user to read

def list_directory_contents(path="."):
    """List directories and files in the given path. Returns (dirs, files)."""
    dirs = []
    files = []
    for item in os.listdir(path):
        if os.path.isdir(os.path.join(path, item)):
            dirs.append(item)
        elif os.path.isfile(os.path.join(path, item)):
            files.append(item)
    print("Directories:")
    for i in dirs:
        print(f"- {i}/")
    print("Files:")
    for i in files:
        print(f"- {i}")
    return dirs, files

def change_directory():
    # Print current directory
    print(f"Current directory: {os.getcwd()}\n")
    list_directory_contents()
    # Prompt user for new directory
    print("\nEnter the path to the new directory (or press Enter to keep current):")
    print("You can also use relative paths like '../' to go up a directory.")
    new_dir = input("Enter the path to the new directory: ").strip()
    if os.path.isdir(new_dir):
        os.chdir(new_dir)
        print(f"Directory changed to: {os.getcwd()}")
        list_directory_contents()
    else:
        print("Current directory remains unchanged: ", os.getcwd())

def menu():
    menu_options = [
        {"Get GA Build & Upgrade (aosga)": lookup_ga_build},
        {"Run tech support gatherer (ts-get)": get_techsupport_main},
        {"Run tech_support_complete.tar Extractor (ts-extract)": extract_all_main},
        {"Run tech_support.log to CSV Converter (ts-csv)": tsbuddy_main},
        {"Run swlog parser to CSV & JSON (ts-log)": logparser_main},
        {"Run AOS Upgrader (aosup)": aosup},
        {"Run AOS Downloader (aosdl)": aosdl_main},
        {"Run HMON Graph (ts-graph-hmon)": graph_hmon_main},
        {"Change current directory": change_directory},
        # {"Clear pycache and .pyc files (ts-clean)": clean_pycache_and_pyc},
        {"Show help info": print_help},
    ]
    #print("\n       (•‿•)  Hey there, buddy!")
    #print(ale_ascii)
    try:
        print("\n   ( ^_^)ノ  Hey there, tsbuddy is at your service!")
    except:
        print("\n   ( ^_^)/  Hey there, tsbuddy is at your service!")
    print("\n Skip this menu by running the CLI commands directly (provided in parentheses below), e.g. `ts-get`.\n")
    while True:
        try:
            print("\n=== 🛎️  ===")
        except:
            print("\n=== Menu ===")
        for idx, opt in enumerate(menu_options, 1):
            print(f"{idx}. {list(opt.keys())[0]}")
        try:
            print("\n0. Exit  (つ﹏<) \n")
        except:
            print("\n0. Exit  (T_T) \n")
        choice = input("Select an option: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(menu_options):
            try:
                #print(f"\n   ( ^_^)ノ⌒☆   \n")
                print(f"\n   ( ^_^)ノ🛎️   \n")
            except:
                #print(f"\n   ( ^_^)/🕭   \n")
                pass
            # Get the function from the selected option
            selected_func = list(menu_options[int(choice)-1].values())[0]
            try:
                selected_func()
            except Exception as e:
                print(f"\nError: {e}\nReturning to menu...\n")
        elif choice == '0':
            print("Exiting...\n\n  (x_x) \n")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    menu()