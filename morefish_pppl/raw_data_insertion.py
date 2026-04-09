import json
from math import log
import traceback
import paho.mqtt.client as mqtt
import uuid
from datetime import datetime
from pytz import timezone
from rawdata import script
from project_status import project_status
from django.db import transaction
import os
import django

from rawdata.calculation import get_battery_voltage, get_solar_voltage
try:
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "morefish_pppl.settings"
    )
    django.setup() 
    from device.models import Device
    from device.models import DeviceRawData
    from device.models import DeviceGateway
    from users.models import MqttTopci
except ImportError as e:
    exit(1)
import traceback




production = project_status()
debug = True  # Set debug = False to disable all print command
keep_log = True  # Set keep_log = False to disable log in production server
client = mqtt.Client(uuid.uuid4().hex)
broker = "broker.hivemq.com"  # broker address
mqtt_port = 1883  # mqtt port
pond_topic = ''
hatchery_topic = ''
dftm8 = 'Dfmt8020008'
battery="battery"
DfmtHatchery = 'DfmtHatchery'
extractor_class = script.extractor(dftm8)

def current_date_time():
    bd_timezone = timezone('Asia/Dhaka')
    bd_time = datetime.now(bd_timezone)
    
    time_stamp = bd_time.strftime('%Y-%m-%d %H:%M:%S')
    print("TIME STAMP----------->",time_stamp)
    print(bd_time)
    return time_stamp

if production is True:
    print("production topic")
    try:
        pond_topic = MqttTopci.objects.get(topic_type = 1).topic
    except MqttTopci.DoesNotExist:
        pond_topic = 'DMA/MoreFish/ifarmer/RawDataInsertion/'
else:
    pond_topic = MqttTopci.objects.get(topic_type = 1).topic



def on_connect(client, userdata, flags, rc):
    if keep_log:
        print("update_device_data is connected with result code " + str(rc))
        print(f"Connected to broker @ {datetime.now()}")
        client.subscribe(pond_topic)


# Called when script disconnects from broker
def on_disconnect(client, userdata, rc):
    client.connect(broker, mqtt_port, 60)
    if keep_log:
        print("update_device_data is dis-connected with result code " + str(rc))
        print(f"DisConnected from broker @ {datetime.now()}")


def on_message(client, userdata, message):
    try:
        if message.topic == pond_topic:
            data = message.payload.decode('utf-8')
            
            device_raw_data = json.loads(data)
            print("INCOMING SERIAL:", device_raw_data.get("did"))
            if len(device_raw_data)>0:
                device_serial = device_raw_data["did"]
                with transaction.atomic():
                    drd_dev=Device.objects.get(dev_serial_no=device_serial)
                    
                    timestamp_str = device_raw_data["Utime"]

                    # Convert the timestamp string to a datetime object
                    try:
                        # Adjust the format string based on the actual format of the timestamp
                        datetime_obj = datetime.strptime(timestamp_str, "%Y/%m/%d %H:%M:%S")
                    except ValueError:
                        try:
                            datetime_obj = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                        # Handle the case where the timestamp string has an invalid format
                        except ValueError as e:
                            print(f"Error: {e}")
                            datetime_obj = None
                    raw_data = DeviceRawData.objects.create(
                        drd_dev_id=drd_dev.id,
                        drd_data=data,
                        drd_created_at = current_date_time(),
                        gateway_id=drd_dev.dev_dvg_id,
                        company_id = drd_dev.company_id,
                        device_data_time = datetime_obj
                    )
                
            else:
                print("EMPTY DATA")
        
        else:
            print("LINE 100")
    except Exception:
        traceback.print_exc()
        
def save_battery_status(battery_status, solar, dev_id):
    from device.models import Device
    try:
        device = Device.objects.get(dev_serial_no = dev_id)
        if device:
            device.dev_battery = get_battery_voltage(battery_status)
            device.dev_solar = get_solar_voltage(solar)
            device.save()
        else:
            print("no device found")
    except:
        traceback.print_exc()

if __name__ == "__main__":
    if debug:
        try:
            print("connecting to broker now")
            client.on_connect = on_connect  # attach the callback function to the client object
            client.on_disconnect = on_disconnect
            client.on_message = on_message  # attach the callback function to the client object
            client.connect(broker, mqtt_port, 60)
            print("LINE 111",pond_topic)
            client.subscribe(pond_topic)
            client.loop_forever()  # to maintain continuous network traffic flow with the broker
        except:
            traceback.print_exc()