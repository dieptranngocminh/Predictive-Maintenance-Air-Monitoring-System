import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json
from datetime import datetime
import time

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
                    else:
                        sensor_data[date_str] = {time_str: sensor.get('value')}
                # If the sensor data doesn't exist, create a new entry
                else:
                    sensor_data = {date_str: {time_str: sensor.get('value')}}

                # Update the sensor data in Firebase
                db.reference(sensor_path).set(sensor_data)

        # Update last update timestamp and station information
        db.reference("/airmonitoringV2/lastUpdate").set(timestamp)
        station_info = {
            'station_id': station_id,
            'station_name': station_name
        }
        db.reference("/airmonitoringV2/station_info").set(station_info)
    except Exception as e:
        print("Exception in on_message: ", e)


# Function to delete all data in /airmonitoringV2 branch
def delete_airmonitoring_data():
    db.reference("/airmonitoringV2").delete()
    print("All data in /airmonitoringV2 deleted")


# Connect to MQTT Server
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
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