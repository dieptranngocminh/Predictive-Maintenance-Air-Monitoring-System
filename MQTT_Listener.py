import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json
from datetime import datetime
import time
from AQI_CalculatoN import*
from collections import deque
# Initialize Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://database-for-air-monitoring-default-rtdb.firebaseio.com/'
})

# Function to normalize timestamp
def normalize_timestamp(timestamp):
    datetime_obj = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S %Z%z")
    date_str = datetime_obj.strftime("%d-%m-%Y")
    time_str = datetime_obj.strftime("%H:%M")
    return date_str, time_str

# Function called when connected to MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("/innovation/airmonitoring/WSNs")

sensor_values = {}
# Define global variables to store O3 sensor values
o3_values_1h = deque(maxlen=6)  # Store values for 1 hour (data received every 10 minute)
o3_values_8h = deque(maxlen=48)  # Store values for 8 hours (data received every 10 minute)


def update_o3_averages(value):
    # Add new O3 value to the deque for 1 hour
    o3_values_1h.append(value)

    # Add new O3 value to the deque for 8 hours
    o3_values_8h.append(value)


def calculate_o3_averages():
    # Calculate average for O3_1h
    o3_1h_average = sum(o3_values_1h) / len(o3_values_1h) if o3_values_1h and len(o3_values_1h) > 0 else 0

    # Calculate average for O3_8h
    o3_8h_average = sum(o3_values_8h) / len(o3_values_8h) if o3_values_8h and len(o3_values_8h) > 0 else 0

    return o3_1h_average, o3_8h_average



# Function called when receiving a message from MQTT
def on_message(client, userdata, msg):
    try:
        print(msg.topic + " " + str(msg.payload))

        # Fix Exception in on_message:  Expecting property name enclosed in double quotes
        payload = msg.payload.decode().replace("'", '"')
        data = json.loads(payload)

        # Extract station information
        station_id = data.get('station_id')
        station_name = data.get('station_name')

        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        PM25 = 0
        PM10 = 0
        SO2 = 0
        NO2 = 0
        CO = 0
        O3 = 0

        # Iterate over sensors data
        for sensor in data.get('sensors', []):
            sensor_id = sensor.get('id')
            sensor_id = sensor_id.replace('.', '_')
            if sensor_id:
                sensor_path = f"/airmonitoringV2/{sensor_id}"

                #Get current date and time
                current_time = datetime.now()
                date_str = current_time.strftime("%Y-%m-%d")
                time_str = current_time.strftime("%H:%M:%S")

                # Check if the sensor data exists in Firebase
                sensor_data = db.reference(sensor_path).get()

                # If the sensor data exists, update it with the new value
                if sensor_data:
                    if date_str in sensor_data:
                        sensor_data[date_str][time_str] = sensor.get('value')
                        sensor_value = sensor_data[date_str][time_str]
                        # Calculate AQI
                        if sensor_id == 'pm2_5_0001':
                            PM25 = float(sensor_value)
                            pm25_subindex = get_PM25_subindex(PM25)
                            print("PM25 subindex ", pm25_subindex)
                        elif sensor_id == 'pm10_0001':
                            PM10 = float(sensor_value)
                            pm10_subindex = get_PM10_subindex(PM10)
                            print("PM10 subindex ", pm10_subindex)
                        elif sensor_id == 'SO2_0001':
                            SO2 = float(sensor_value)
                            so2_subindex = get_SO2_subindex(SO2)
                            print("SO2 subindex ", so2_subindex)
                        elif sensor_id == 'NO2_0001':
                            NO2 = float(sensor_value)
                            no2_subindex = get_NO2_subindex(NO2)
                            print("NO2 subindex ", no2_subindex)
                        elif sensor_id == 'CO_0001':
                            CO = float(sensor_value)
                            co_subindex = get_CO_subindex(CO)
                            print("CO subindex ", co_subindex)
                        elif sensor_id == 'O3_0001':
                            O3 = float(sensor_value)
                            update_o3_averages(O3)
                            o3_1h_avg, o3_8h_avg = calculate_o3_averages()
                            o3_1h_subindex = get_O3_subindex_1h(o3_1h_avg)
                            o3_8h_subindex = get_O3_subindex_8h(o3_8h_avg)
                            o3_subindex = get_O3_AQI(o3_1h_subindex, o3_8h_subindex)
                            print("O3 subindex ", o3_subindex)

                else:
                    sensor_data = {date_str: {time_str: sensor.get('value')}}
                    sensor_value = sensor_data[date_str][time_str]

            else:
                sensor_data = {date_str: {time_str: sensor.get('value')}}
                sensor_value = sensor_data[date_str][time_str]
                # Update the sensor data in Firebase
                db.reference(sensor_path).set(sensor_data)
        #test_aqi = get_overall_daily_AQI(*pm25_subindex, *pm10_subindex, *so2_subindex, *no2_subindex,
        #                                 *co_subindex, *o3_1h_avg, *o3_8h_avg)
        #print("test aqi ", test_aqi)
                overall_aqi = get_overall_daily_AQI(pm25_subindex, pm10_subindex, so2_subindex, no2_subindex,
                                                        co_subindex, o3_1h_avg, o3_8h_avg)
                print("AQI ", overall_aqi)
        #aqi_bucket = get_AQI_bucket(overall_aqi)
                db.reference(f"/airmonitoringV2/AQI/{date_str}").child(time_str).set(overall_aqi)
        # Update last update timestamp and station information
        db.reference("/airmonitoringV2/lastUpdate").set(timestamp)

        station_info = {
            'station_id': station_id,
            'station_name': station_name

        }
        db.reference("/airmonitoringV2/station_info").set(station_info)
        """
        # Calculate PM2.5, PM10, SO2, NO2, CO, and O3 subindices if all required sensors are available
        if all(sensor_id in sensor_values for sensor_id in ['PM25', 'PM10', 'SO2', 'NO2', 'CO', 'O3']):
            pm25_subindex = get_PM25_subindex(sensor_values['PM25'])
            pm10_subindex = get_PM10_subindex(sensor_values['PM10'])
            so2_subindex = get_SO2_subindex(sensor_values['SO2'])
            no2_subindex = get_NO2_subindex(sensor_values['NO2'])
            co_subindex = get_CO_subindex(sensor_values['CO'])
            # Calculate O3 subindices and overall daily AQI
            o3_1h_average, o3_8h_average = calculate_o3_averages()
            o3_1h_subindex = get_O3_subindex_1h(o3_1h_average)
            o3_8h_subindex = get_O3_subindex_8h(o3_8h_average)
            o3_aqi = get_O3_AQI(o3_1h_average, o3_8h_average)

            # Calculate overall daily AQI
            overall_aqi = get_overall_daily_AQI(pm25_subindex, pm10_subindex, so2_subindex, no2_subindex, co_subindex,
                                                o3_1h_subindex, o3_8h_subindex)
            aqi_bucket = get_AQI_bucket(overall_aqi)
            # print("test")
            # print("Overall Daily AQI:", overall_aqi)
            # print("AQI Bucket from function:", aqi_bucket)
        """
        # Set the AQI value with its corresponding timestamp

        #db.reference("/airmonitoringV2/AQI").push(overall_aqi)
    except Exception as e:
        print("Exception in on_message: ", e)

# Function to delete all data in /airmonitoringV2 branch
def delete_airmonitoring_data():
    db.reference("/airmonitoringV2").delete()
    print("All data in /airmonitoringV2 deleted")


# Connect to MQTT Server
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set("innovation", password="Innovation_RgPQAZoA5N")
client.connect("mqttserver.tk", 1883, 60)

# Start MQTT loop
client.loop_start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
    client.disconnect()
    client.loop_stop()