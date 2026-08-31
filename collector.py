import json
from datetime import datetime, timezone

def main():

     ##code to get cpu temprature for raspbery Pi 5
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

    j = json.dumps(temperature_dict)
    with open("telemetry_data.json", "w") as f:
        f.write(j)


    ##print(f"CPU Temperature: {temp_celsius} °C")


if __name__ == "__main__":
    main()