from pathlib import Path
from collections import defaultdict
import re
import os

# Natural sort helper
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

# ✅ Extracts last numeric suffix (e.g. ".23" → 23), returns -1 if no suffix
def last_number_sort_key(filename: str):
    match = re.search(r'\.(\d+)$', filename)
    if match:
        return int(match.group(1))
    return -1  # Put base file (no numeric suffix) first

def last_number_sort_key2(filename: str) -> int:
    """
    Sorts by the last numeric suffix (e.g., .23 → 23), or -1 for base file (no suffix).
    This ignores 'swlog_archive/' prefix when present.
    """
    base = filename.replace("swlog_archive/", "")
    match = re.search(r'\.(\d+)$', base)
    return int(match.group(1)) if match else -1

def last_number_sort_key3(filename: str) -> tuple:
    """
    Sorts files by base name first, then by numeric suffix if present.
    Handles filenames like NI3_consoleLog.0 and swlog_archive/NI3_consoleLog.0.
    """
    # Remove swlog_archive/ if present
    stripped = filename.replace("swlog_archive/", "")
    
    # Separate base name and numeric suffix
    match = re.match(r'(.+?)\.(\d+)$', stripped)
    if match:
        base, num = match.groups()
        return (base, int(num))  # Sort by base name then number
    else:
        return (stripped, -1)  # Base file comes before numbered

# Predefined categories
category_patterns = [
    "CMMB_host",
    "CMMA_host",
    "NI1_consoleLog",
    "NI2_consoleLog",
    "NI3_consoleLog",
    "NI4_consoleLog",
    "NI5_consoleLog",
    "NI6_consoleLog",
    "NI7_consoleLog",
    "NI8_consoleLog",
    "chassis1_CMMA",
    "chassis1_CMMB",
    "chassis2_CMMA",
    "chassis2_CMMB",
    "chassis3_CMMA",
    "chassis3_CMMB",
    "chassis4_CMMA",
    "chassis4_CMMB",
    "chassis5_CMMA",
    "chassis5_CMMB",
    "chassis6_CMMA",
    "chassis6_CMMB",
    "chassis7_CMMA",
    "chassis7_CMMB",
    "chassis8_CMMA",
    "chassis8_CMMB",
    "swlog_CMMA",
    "swlog_CMMB",
    "swlog_chassis1",
    "swlog_chassis2",
    "swlog_chassis3",
    "swlog_chassis4",
    "swlog_chassis5",
    "swlog_chassis6",
    "swlog_chassis7",
    "swlog_chassis8",
    "localConsole"
]

# Categorize a single file name
def categorize(name: str) -> str:
    name = name.replace("swlog_archive/", "")
    base = re.sub(r'\.\d+$', '', name)  # Remove .0, .1, etc.
    for pattern in category_patterns:
        if pattern in base:
            return pattern
    return "Uncategorized"

# Step 1: Read and group files into dir_dict
def filter_log_paths(
    root_dir: str = None,
    include_keywords=("swlog", "console"),
    exclude_keywords=("tsbuddy",),
):
    """
    Recursively searches for files in root_dir (default current directory) whose names
    include any of the include_keywords and exclude any of the exclude_keywords (case-insensitive).
    Returns a list of full file paths.
    """
    if root_dir is None:
        root_dir = os.getcwd()
    include_pattern = re.compile("|".join(include_keywords), re.IGNORECASE)
    exclude_pattern = re.compile("|".join(exclude_keywords), re.IGNORECASE)
    filtered_paths = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if include_pattern.search(filename) and not exclude_pattern.search(filename):
                full_path = os.path.join(dirpath, filename)
                filtered_paths.append(full_path)
    print(f"Total: {len(filtered_paths)} log files found.")
    return filtered_paths

# Step 2: Categorize each value in each directory
categorized_by_dir = {}

def main():
    """Main function to categorize and print log file paths."""
    file_paths = filter_log_paths()

    skip_suffixes = {'.gz', '.tar', '.time', '.level'}
    skip_name_suffixes = ('_Qemu', '_Vm')

    dir_dict = defaultdict(list)

    for full_path_str in file_paths:
        path = Path(full_path_str)
        if not path.is_file() or path.suffix in skip_suffixes or path.stem.endswith(skip_name_suffixes):
            continue
        parent = path.parent
        if parent.name == "swlog_archive":
            grandparent = parent.parent
            relative_name = f"swlog_archive/{path.name}"
            dir_dict[str(grandparent)].append(relative_name)
        else:
            dir_dict[str(parent)].append(path.name)

    #for parent_dir, files in dir_dict.items():
    #    category_map = defaultdict(list)
    #    for file in files:
    #        category = categorize(file)
    #        category_map[category].append(file)
    #    # Sort each category
    #    for cat in category_map:
    #        category_map[cat] = sorted(category_map[cat], key=natural_sort_key)
    #    categorized_by_dir[parent_dir] = dict(category_map)

    for parent_dir, files in dir_dict.items():
        category_map = defaultdict(list)
        for file in files:
            category = categorize(file)
            category_map[category].append(file)
        # Sort each category's files by the last number
        for cat in category_map:
            category_map[cat] = sorted(category_map[cat], key=last_number_sort_key3)
        categorized_by_dir[parent_dir] = dict(category_map)
    return categorized_by_dir

def print_categorized_logs():
    """Prints categorized log files."""
    categorized_by_dir = main()
    # Step 3: Print the nested structure
    for parent_dir, categories in categorized_by_dir.items():
        print(f"\nDirectory: {parent_dir}")
        for category, files in categories.items():
            print(f"\n\n  Category: {category}")
            for f in files:
                print(f"    {f}")

# Step 4: Return File Paths with Category Filter
def print_filtered_paths():
    """Prints file paths for categories starting with "swlog" or "localConsole".
    """
    categorized_by_dir = main()
    for dir_path, logs_dict in categorized_by_dir.items():
        print(dir_path, "\n")
        for category in logs_dict:
            if category.startswith("swlog") or category.startswith("localConsole"):
                for log_name in logs_dict[category]:
                    print(f"{dir_path}/{log_name}")

# Step 5: Return File Paths by Category
def print_paths_by_category():
    """Prints file paths grouped by category."""
    categorized_by_dir = main()
    for dir_path, logs_dict in categorized_by_dir.items():
        print(dir_path, "\n")
        for category in logs_dict:
            print(f"\nCategory: {category}")
            for log_name in logs_dict[category]:
                print(f"{dir_path}/{log_name}")

if __name__ == "__main__":
    print("Categorized Logs:")
    print_categorized_logs()
    print("\nFiltered Paths:")
    print_filtered_paths()
    print("\nPaths by Category:")
    print_paths_by_category()
    # Uncomment the following line to run the main function directly
    # main()
