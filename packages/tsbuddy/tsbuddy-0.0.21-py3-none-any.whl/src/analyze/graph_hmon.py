import os
import csv
import glob
from datetime import datetime
import tkinter as tk
import random
import re

# --------- SETTINGS ---------
EXCLUDE_SUFFIX = ".gz"
Y_MAX = 100
WINDOW_WIDTH = 1000  # Visible window size
WINDOW_HEIGHT = 500
MARGIN = 70
# ----------------------------


# Help text
HELP_TEXT = """
This script visualizes CPU usage data from multiple files in a chronological graph.
It reads all files in the current directory matching the pattern "*hmondata_chassis{chassis_id}*"
and plots CPU usage over time, allowing you to scroll through the data.
Click on the graph to see detailed information about a specific point.
This info will output to the terminal/shell.
"""

def print_help():
    print(HELP_TEXT)

def get_chassis_id():
    """Prompt user for chassis ID and return it."""
    while True:
        chassis_id = input("Enter chassis ID # (or type 'cd' to change directories) [1]: ").strip() or '1'
        if chassis_id.lower() == 'cd':
            print("\nEnter the path to the new directory (or press Enter to keep current):")
            print("You can also use relative paths like '../' to go up a directory.")
            new_dir = input("Enter the path to the new directory: ").strip()
            if os.path.isdir(new_dir):
                os.chdir(new_dir)
                print(f"Directory changed to: {os.getcwd()}")
            else:
                print("Current directory remains unchanged: ", os.getcwd())
        elif chassis_id.isdigit():
            return chassis_id
        else:
            print("Invalid input. Please enter a numeric chassis ID.")

def main():
    print_help()
    chassis_id = get_chassis_id()
    # Insert the chassis ID into the file pattern
    FILE_PATTERN = f"*hmondata_chassis{chassis_id}*"
    # STEP 1: Get first timestamp from each file
    def get_first_timestamp(file):
        try:
            with open(file, newline='') as csvfile:
                next(csvfile)  # skip metadata
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        ts = datetime.strptime(row['time_stamp'], "%d %b %Y %H:%M:%S")
                        return ts
                    except (ValueError, KeyError):
                        continue
        except Exception as e:
            print(f"Could not read {file}: {e}")
        return datetime.max
    # Extract the suffix number after the last underscore, or after the last dot, or assign 0 for base file
    def extract_suffix_number(filename):
        base = os.path.splitext(os.path.basename(filename))[0]
        # Try to match _<number> at the end
        match = re.search(r'_(\d+)$', base)
        if match:
            return int(match.group(1))
        # Try to match .<number> at the end
        match = re.search(r'\.(\d+)$', base)
        if match:
            return int(match.group(1))
        # Base file (no suffix)
        return 0
    # STEP 2: Filter and sort files
    files = [f for f in glob.glob(f"{FILE_PATTERN}") if not f.endswith(EXCLUDE_SUFFIX)]
    files_sorted = sorted(
        files,
        key=lambda f: (extract_suffix_number(f), len(f), f),
        reverse=True
    )
    # Debug: print file order and extracted numbers
    print("Files sorted by suffix number (descending, oldest to newest, left to right):")
    for f in files_sorted:
        #print(f"{f} -> {extract_suffix_number(f)}")
        print(f"{f}")
    print("\nPlease wait while the data is being processed...\n")
    # STEP 3: Assign colors per file
    file_colors = {f: "#{:06x}".format(random.randint(0, 0xFFFFFF)) for f in files_sorted}
    # STEP 4: Load and store all data rows
    data_points = []
    for file in files_sorted:
        try:
            with open(file, newline='') as csvfile:
                next(csvfile)  # skip metadata
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        ts = datetime.strptime(row['time_stamp'], "%d %b %Y %H:%M:%S")
                        usage = float(row['cpu_usage'])
                        data_points.append((ts, usage, file))
                    except (ValueError, KeyError):
                        continue
        except Exception as e:
            print(f"Failed to read {file}: {e}")
    if not data_points:
        print("No valid data found.")
    # STEP 5: Do NOT sort all data by actual timestamps; chain by filename order
    # Instead, use the order in which data_points were appended (by files_sorted)
    time_stamps, cpu_usages, file_names = zip(*data_points)
    # Use a simple index as the time axis (chained by file order)
    times_in_seconds = list(range(len(time_stamps)))
    # STEP 6: Configure scrollable canvas
    SCROLLABLE_WIDTH = max(1000, int(len(times_in_seconds)) * .5)
    SCROLLABLE_HEIGHT = WINDOW_HEIGHT
    root = tk.Tk()
    root.title("Chronological CPU Usage Graph with Scroll")
    # Canvas + scrollbar frame
    frame = tk.Frame(root)
    frame.pack(fill='both', expand=True)
    # Horizontal scrollbar
    h_scrollbar = tk.Scrollbar(frame, orient='horizontal')
    h_scrollbar.pack(side='bottom', fill='x')
    # Canvas setup
    canvas = tk.Canvas(
        frame,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        bg='white',
        xscrollcommand=h_scrollbar.set,
        scrollregion=(0, 0, SCROLLABLE_WIDTH, SCROLLABLE_HEIGHT)
    )
    canvas.pack(side='left', fill='both', expand=True)
    h_scrollbar.config(command=canvas.xview)
    # Scaling
    PLOT_WIDTH = SCROLLABLE_WIDTH
    x_scale = (PLOT_WIDTH - 2 * MARGIN) / max(times_in_seconds)
    y_scale = (WINDOW_HEIGHT - 2 * MARGIN) / Y_MAX
    # Draw axes
    canvas.create_line(MARGIN, WINDOW_HEIGHT - MARGIN, PLOT_WIDTH - MARGIN, WINDOW_HEIGHT - MARGIN)
    canvas.create_line(MARGIN, MARGIN, MARGIN, WINDOW_HEIGHT - MARGIN)
    # Axis labels
    canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT - MARGIN // 2 + 20, text="Time (HH:MM)", font=("Arial", 12))
    canvas.create_text(MARGIN // 2, WINDOW_HEIGHT // 2, text="CPU Usage (%)", angle=90, font=("Arial", 12))
    # Y-axis ticks
    for y in range(0, Y_MAX + 1, 10):
        y_pos = WINDOW_HEIGHT - MARGIN - y * y_scale
        canvas.create_line(MARGIN - 5, y_pos, MARGIN, y_pos)
        canvas.create_text(MARGIN - 25, y_pos, text=f"{y}", font=("Arial", 10))
    # X-axis hourly ticks
    last_hour = None
    for i, ts in enumerate(time_stamps):
        if ts.minute == 0 and ts.hour != last_hour:
            x = MARGIN + times_in_seconds[i] * x_scale
            hour_min = ts.strftime("%H:%M")
            canvas.create_line(x, WINDOW_HEIGHT - MARGIN, x, WINDOW_HEIGHT - MARGIN + 5)
            canvas.create_text(x, WINDOW_HEIGHT - MARGIN + 20, text=hour_min, font=("Arial", 10))
            last_hour = ts.hour
    # Plot data
    for i in range(1, len(cpu_usages)):
        x1 = MARGIN + times_in_seconds[i - 1] * x_scale
        y1 = WINDOW_HEIGHT - MARGIN - cpu_usages[i - 1] * y_scale
        x2 = MARGIN + times_in_seconds[i] * x_scale
        y2 = WINDOW_HEIGHT - MARGIN - cpu_usages[i] * y_scale
        color = file_colors[file_names[i]]
        canvas.create_line(x1, y1, x2, y2, fill=color)
    # Click handler to show info
    def on_click(event):
        canvas_x = canvas.canvasx(event.x)
        if not (MARGIN <= canvas_x <= PLOT_WIDTH - MARGIN and MARGIN <= event.y <= WINDOW_HEIGHT - MARGIN):
            return
        time_clicked = (canvas_x - MARGIN) / x_scale
        closest_idx = min(range(len(times_in_seconds)), key=lambda i: abs(times_in_seconds[i] - time_clicked))
        ts = time_stamps[closest_idx].strftime("%Y-%m-%d %H:%M:%S")
        usage = cpu_usages[closest_idx]
        fname = file_names[closest_idx]
        print(f"Clicked near: {ts} | CPU: {usage:.2f}% | File: {fname}")
    canvas.bind("<Button-1>", on_click)
    # Draw legend (at end of scrollable area)
    legend_y = MARGIN
    for file, color in file_colors.items():
        canvas.create_rectangle(PLOT_WIDTH + 10, legend_y, PLOT_WIDTH + 30, legend_y + 10, fill=color)
        canvas.create_text(PLOT_WIDTH + 35, legend_y + 5, text=file, anchor='w', font=("Arial", 8))
        legend_y += 15
    root.mainloop()

if __name__ == "__main__":
    main()
