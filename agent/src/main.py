from paho.mqtt import client as mqtt_client
import time
from schema.aggregated_data_schema import AggregatedDataSchema
from schema.parking_schema import ParkingSchema
from file_datasource import FileDatasource
import config


def connect_mqtt(broker, port):
    """Create MQTT client"""
    print(f"CONNECT TO {broker}:{port}")

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT Broker ({broker}:{port})!")
        else:
            print("Failed to connect {broker}:{port}, return code %d\n", rc)
            exit(rc)  # Stop execution

    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect(broker, port)
    client.loop_start()
    return client


def publish(client, topic_aggregated, topic_parking, datasource, delay):
    datasource.start_reading()
    schema_map = {
        topic_aggregated: (AggregatedDataSchema(), 'aggregated'),
        topic_parking: (ParkingSchema(), 'parking')
    }

    while True:
        time.sleep(delay)
        data = datasource.read()

        if not data:
            continue

        for topic, (schema, key) in schema_map.items():
            msg = schema.dumps(data[key])
            result = client.publish(topic, msg)
            if result[0] != 0:
                print(f"Failed to send {key} data to topic {topic}")


def run():
    # Prepare mqtt client
    client = connect_mqtt(config.MQTT_BROKER_HOST, config.MQTT_BROKER_PORT)

    # Prepare datasource
    datasource = FileDatasource(
        "data/accelerometer.csv",
        "data/gps.csv",
        "data/parking.csv"
    )

    # Infinity publish data
    publish(client, config.MQTT_TOPIC_AGGREGATED, config.MQTT_TOPIC_PARKING, datasource, config.DELAY)


if __name__ == '__main__':
    run()
