import json
from datetime import datetime, timezone
import time


# Helper method to write json for temperature 
def write_json(data, filename="telemetry_data.json"):
    with open(filename, "a") as f:
        json.dump(data, f)
        f.write("\n")  

def main():
    while True:
        ##code to get cpu temperature for raspbery Pi 5
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as temprature_file:
            raw_data = temprature_file.read()
        
        temp_celsius = int(raw_data.strip()) / 1000.0
        time_stamp = datetime.now(timezone.utc)
        
        temperature_dict = {
            "timestamp": time_stamp.isoformat(),
            "metric": "cpu_temperature",
            "value": temp_celsius,
            "unit": "celsius"
        }

        write_json(temperature_dict) 


        time.sleep(30)
        
    ##print(f"CPU Temperature: {temp_celsius} °C")


if __name__ == "__main__":
    main()