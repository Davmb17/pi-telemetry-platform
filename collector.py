def main():

     ##code to get cpu temprature for raspbery Pi 5
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as tempraturefile:
        raw_data = tempraturefile.read()

    temp_celsius = int(raw_data.strip()) / 1000.0

    print(f"CPU Temperature: {temp_celsius} °C")


if __name__ == "__main__":
    main()