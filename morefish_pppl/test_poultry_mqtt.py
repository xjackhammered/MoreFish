import paho.mqtt.client as mqtt
import json, uuid, time

client = mqtt.Client(uuid.uuid4().hex)
client.connect("broker.hivemq.com", 1883)

client.loop_start()  # Start network loop in background

payload = json.dumps({
    "client_id": "test-poultry-002",
    "data": [{
        "temperature": 100,
        "humidity": 70.0,
        "co2": 1700,
        "nh3_gas": 12.4,
        "aqi": 75,
        "pm2_5": 15.2,
        "pm10": 22.1,
        "sound_db": 55.0,
        "tvoc": 551,
        "methane_ppm": 235,
    }]
})

client.publish("PoultryCare/DTU", payload)
time.sleep(1)  # Wait for message to be sent
client.loop_stop()
client.disconnect()
print("Published test message")