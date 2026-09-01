import json
from datetime import datetime, timezone
import time
import os


# Helper method to append a telemetry record as JSON
def write_json(data, filename="/data/telemetry_data.json"):
    with open(filename, "a") as f:
        json.dump(data, f)
        f.write("\n")  

# Helper method to get hostname 
def get_host_name():
    host_name = ""
    with open("/proc/sys/kernel/hostname", "r") as f:
        host_name = f.read().strip()

    return host_name

# Helper method to get cpu temperature 
def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as temprature_file:
        raw_temp_data = temprature_file.read()      
    return int(raw_temp_data.strip()) / 1000.0

# Helper method to get cpu usage percent
def get_cpu_usage_pct():
    def read_cpu_ticks():
        with open("/proc/stat", "r") as f:
            # first line given is cpu raw metrics ex: cpu  9561 30 8572 109003245 2237 0 51 0 0 0
            first_line = f.readline() 

            # splits the string by whitespaces and the converts line into list of individual strings.
            # then slices from index 1 to end and then removes word 'cpu' to leave only numbers then loops through to make integers
            ticks = [int(x) for x in first_line.split()[1:]]

            # returns tuple with two values
            # sum(ticks) -> adds all numbers in the list together to represent total cpu Time (both busy and resting time) since device booted
            # ticks[3] = pure idle time, ticks[4] = iowait time (waiting for disk). We add them together because the CPU is physically resting during both states.
            return sum(ticks), ticks[3] + ticks[4]

    total1, idle1 = read_cpu_ticks()
    time.sleep(1) # wait 1 second to measure difference
    total2, idle2 = read_cpu_ticks()

    total_delta = total2 - total1
    idle_delta = idle2 - idle1

    # safety check
    if total_delta == 0:
        return 0.0
    return (1.0 - (idle_delta / total_delta)) * 100

# Helper method to get memory usage percent
def get_mem_usage_pct():
    with open("/proc/meminfo", "r") as f:
        # Ex of data 
        # MemTotal:        8255888 kB
        # MemFree:         6903936 kB
        # MemAvailable:    7890688 kB
        lines = f.readlines()


    # create clean data dict
    mem_dict = {}
    for line in lines:
        parts = line.split() # split into list of strings ex: ['MemTotal:', '8255888', 'kB']
        if len(parts) >= 2:
            key = parts[0].replace(":", "") # takes first item and removes colon to make into key ex: MemTotal
            mem_dict[key] = int(parts[1]) # takes second item and converts itt from text to integer ex: 8255888

    total = mem_dict.get("MemTotal", 0)
    available = mem_dict.get("MemAvailable", 0)

    # safety check
    if total == 0:
        return 0.0
    used = total - available
    return (used / total) * 100

# Helper method to get disk usage percent
def get_disk_usage_pct():
    # Use built in tool status virtual file system. Pass root directory "/"
    stat = os.statvfs("/")

    total_blocks = stat.f_blocks # number of storage blocks on entire partition
    # number of storage blocks to normal unprivileged user. 
    # f_bavail is better choice over f_free since it ensures accurate calcuation of room left to write files. 
    # linux locks away a small safety buffer of storage space strictly for system administrator. 
    free_blocks = stat.f_bavail 

    # safety check
    if total_blocks == 0:
        return 0.0

    used_blocks = total_blocks - free_blocks
    return (used_blocks / total_blocks) * 100

def main():
    raw_interval = os.getenv("COLLECTION_INTERVAL", "29")
    collection_interval = int(raw_interval)
    try: 
         while True:
            
            time_stamp = datetime.now(timezone.utc)
            host_name = get_host_name()
            cpu_temp = get_cpu_temperature()
            cpu_usage = get_cpu_usage_pct()
            mem_usage = get_mem_usage_pct()
            disk_usage = get_disk_usage_pct()
                
            system_snapshot = {
                "timestamp": time_stamp.isoformat(),
                "hostname": host_name,
                "cpu_temperature_c": round(cpu_temp, 2),
                "cpu_usage_percent": round(cpu_usage, 2),
                "memory_usage_percent": round(mem_usage, 2),
                "disk_usage_percent": round(disk_usage, 2)
            }
        
            write_json(system_snapshot) 
        
        
            time.sleep(collection_interval)
    except KeyboardInterrupt:
        print("Collector Stopped.")
    


if __name__ == "__main__":
    main()