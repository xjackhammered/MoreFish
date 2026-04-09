import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connected with result code {rc}")
    if rc == 0:
        print("Connection successful!")
        client.subscribe("#")  # Subscribe to all topics to see everything
    else:
        print(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    print(f"Received: {msg.topic} -> {msg.payload.decode()}")

def on_publish(client, userdata, mid):
    print(f"Message published with mid: {mid}")

def on_disconnect(client, userdata, rc):
    print(f"Disconnected with code {rc}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.on_disconnect = on_disconnect

print("Connecting to broker.hivemq.com:1883...")
client.connect("broker.hivemq.com", 1883, 60)

client.loop_start()
time.sleep(2)  # Wait for connection

print("Publishing test message...")
client.publish("PoultryCare/DTU", "test payload")

time.sleep(2)  # Wait for message to be processed
client.loop_stop()
client.disconnect()