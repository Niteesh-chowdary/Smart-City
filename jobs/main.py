import os
import random
import uuid
from confluent_kafka import SerializingProducer
import simplejson as json
from datetime import timedelta
from datetime import datetime

LONDON_COORDINATES = {"latitude":51.5074,"longitude":-0.1278}
BIRMINGHAM_COORDINATES = {"latitude":52.4862,"longitude":-1.8904}

# Calculate movement increments
LATITUDE_INCREMENTS = (BIRMINGHAM_COORDINATES['latitude'] - LONDON_COORDINATES['latitude'])/100
LONGITUDE_INCREMENTS = (BIRMINGHAM_COORDINATES['longitude'] - LONDON_COORDINATES['longitude']) / 100

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS','localhost:9092')
VEHICLE_TOPIC = os.getenv('VEHICLE_TOPIC','vehicle_data')
GPS_TOPIC = os.getenv('GPS_TOPIC','gps_data')
TRAFFIC_TOPIC = os.getenv('TRAFFIC_TOPIC','traffic_data')
WEATHER_TOPIC = os.getenv('WEATHER_TOPIC','weather_topic')
EMERGENCY_TOPIC = os.getenv('EMERGENCY_TOPIC','emergency_data')

start_time = datetime.now()
start_location = LONDON_COORDINATES.copy()

def get_next_time():
    global start_time
    start_time += timedelta(seconds=random.randint(30,60))
    return start_time

def generate_gps_data(device_id,timestamp,vehicle_type='private'):
    return {
        'id':uuid.uuid4(),
        'deviceId':device_id,
        'timestamp':timestamp,
        'speed':random.uniform(0,40),
        'direction': 'North-East',
        'vehicleType': vehicle_type,

    }

def generate_traffic_camera_data(device_id,timestamp,camera_id):
    return {
        'id': uuid.uuid4(),
        'deviceId': device_id,
        'timestamp': timestamp,
        'snapshot': 'Base64EncodedString'
    }

def generate_weather_data(device_id,timestamp,location):
    return {
        'id':uuid.uuid4(),
        'deviceId':device_id,
        'location':location,
        'timestamp':timestamp,
        'temperature':random.uniform(-5,26),
        'weatherCondition': random.choice(['Sunny','Cloudy','Rain','Snow']),
        'precipitation': random.uniform(0,25),
        'windspeed': random.uniform(0,100),
        'humidity': random.randint(0,100),
        'airQualityIndex':random.uniform(0,500),
    }

def generate_emergency_data(device_id,timestamp,location):
    return {
        'id':uuid.uuid4(),
        'deviceId': device_id,
        'incidentId': uuid.uuid4(),
        'type': random.choice(['Accident','Fire','Police','None']),
        'timestamp':timestamp,
        'location':location,
        'status':random.choice(['Active','Resolved']),
        'description': 'Description of the incident'
    }

def simulate_vehicle_movement():
    global start_location

    # move towards birmingham
    start_location['latitude'] += LATITUDE_INCREMENTS
    start_location['longitude'] += LONGITUDE_INCREMENTS

    # add some randomness to simulate actual road
    start_location['latitude'] += random.uniform(-0.0005,0.0005)
    start_location['longitude'] += random.uniform(-0.0005,0.0005)

    return start_location


def generate_vehicle_data(device_id):
    location = simulate_vehicle_movement()
    return {
        'id': uuid.uuid4(),
        'deviceId':device_id,
        'timestamp': get_next_time().isoformat(),
        'location':(location['latitude'],location['longitude']),
        'speed':random.uniform(10,40),
        'direction':'North-East',
        'make': 'Mercedes',
        'model': 'E350',
        'year': 2024,
        'fuelType':'Hybrid'
    }


def simulate_journey(producer,device_id):
    while True:
        vehicle_data = generate_vehicle_data(device_id)
        gps_data = generate_gps_data(device_id,vehicle_data['timestamp'])
        traffic_camera_data = generate_traffic_camera_data(device_id,vehicle_data['timestamp'],'surveillance-camera4')
        weather_data = generate_weather_data(device_id,vehicle_data['timestamp'],vehicle_data['location'])
        emergency_data = generate_emergency_data(device_id,vehicle_data['timestamp'],vehicle_data['location'])
        break

if __name__ == "__main__":
    producer_config = {
        'bootstrap.servers':KAFKA_BOOTSTRAP_SERVERS,
        'error_cb':lambda err: print(f'Kafka error: {err}')
    }
    producer = SerializingProducer(producer_config)

    try:
        simulate_journey(producer,'Vehicle-Niteesh-9')
    except KeyboardInterrupt:
        print("Simulation ended by the user")
    except Exception as e:
        print(f"Unexpected error has occurred: {e}")