import csv
import glob
from datetime import datetime, timedelta

# Parameters
ROLLING_WINDOW_MINUTES = 1
INCREASE_DURATION_MINUTES = 5 # Must be a multiple of ROLLING_WINDOW_MINUTES
MIN_INCREASE_THRESHOLD = 22.0  # Percentage increase considered significant

def parse_cpu_data(file_pattern):
    data = []
    files = sorted([f for f in glob.glob(file_pattern) if not f.endswith('.gz')])
    for file in files:
        try:
            with open(file, newline='') as csvfile:
                next(csvfile)  # skip metadata
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        ts = datetime.strptime(row['time_stamp'], "%d %b %Y %H:%M:%S")
                        cpu = float(row['cpu_usage'])
                        data.append((ts, cpu))
                    except (ValueError, KeyError):
                        continue
        except Exception as e:
            print(f"Error reading {file}: {e}")
    return sorted(data, key=lambda x: x[0])

def compute_rolling_averages(data, window_minutes):
    from collections import deque
    window = timedelta(minutes=window_minutes)
    rolling_averages = []
    q = deque()
    sum_cpu = 0.0
    idx = 0
    for ts, cpu in data:
        q.append((ts, cpu))
        sum_cpu += cpu
        # Remove old entries outside the window
        while q and (ts - q[0][0]) > window:
            old_ts, old_cpu = q.popleft()
            sum_cpu -= old_cpu
        if len(q) > 0:
            avg = sum_cpu / len(q)
            rolling_averages.append((ts, avg))
    return rolling_averages

def detect_prolonged_increase(rolling_avgs, window_minutes, duration_minutes, threshold):
    result = []
    required_points = duration_minutes // window_minutes
    for i in range(len(rolling_avgs) - required_points):
        window_slice = rolling_avgs[i:i + required_points]
        values = [v for _, v in window_slice]
        if all(earlier < later for earlier, later in zip(values, values[1:])):
            total_increase = values[-1] - values[0]
            if total_increase >= threshold:
                result.append({
                    'start': window_slice[0][0],
                    'end': window_slice[-1][0],
                    'increase': round(total_increase, 2)
                })
    return result

def main():
    chassis_id = input("Enter chassis ID [1]: ").strip() or "1"
    file_pattern = f"flash/flash/system/hmon/*hmondata_chassis{chassis_id}*"
    data = parse_cpu_data(file_pattern)
    if not data:
        print("No valid CPU data found.")
        return
    print(f"Loaded {len(data)} data points. Computing rolling averages...")
    rolling_avgs = compute_rolling_averages(data, ROLLING_WINDOW_MINUTES)
    print(f"Analyzing {len(rolling_avgs)} rolling average points for prolonged increase...")
    prolonged_increases = detect_prolonged_increase(
        rolling_avgs,
        ROLLING_WINDOW_MINUTES,
        INCREASE_DURATION_MINUTES,
        MIN_INCREASE_THRESHOLD
    )
    if prolonged_increases:
        print(f"\nDetected {len(prolonged_increases)} prolonged CPU usage increases:\n")
        for item in prolonged_increases:
            print(f"From {item['start']} to {item['end']} | Increase: {item['increase']}%")
    else:
        print("No prolonged CPU usage increases detected.")

if __name__ == "__main__":
    main()
