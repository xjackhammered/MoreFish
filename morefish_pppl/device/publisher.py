import paho.mqtt.client as mqttClient
import uuid
def on_connect(client, userdata, flags, rc):
    if rc == 0:

        print("Connected to broker")

        global Connected  # Use global variable
        Connected = True  # Signal connection

    else:

        print("Connection failed")


Connected = False  # global variable for the state of the connection

broker_address = "broker.hivemq.com"
port = 1883


client = mqttClient.Client(uuid.uuid4().hex) # create new instance
client.on_connect = on_connect  # attach function to callback
