# import pandas as pd
import requests
import math
import traceback
from datetime import datetime, timedelta
from django.db.models import Max
from django.db.models import Prefetch
from pytz import timezone
from celery import Celery, shared_task
from assets.models import AssetsProperties
from device.models import DeviceDataHistory
from users.models import APIKey
from django.db import transaction
dfmt5 = 'Dfmt8020005'
dfmt6 = 'Dfmt8020006'
dfmt7A = 'Dfmt8020007A'
DfmtHatchery = 'DfmtHatchery'

import logging
import os

# Setup logger
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("device_data_logger")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(os.path.join(LOG_DIR, 'device_data.log'))
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
file_handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(file_handler)


def current_date_time():
    bd_timezone = timezone('Asia/Dhaka')
    bd_time = datetime.now(bd_timezone).strftime('%Y-%m-%d %H:%M:%S')
    print("TIME STAMP --------------->", bd_time)
    return bd_time

def current_date_time_obj()->str:
    bd_timezone = timezone('Asia/Dhaka')
    bd_time = datetime.now(bd_timezone)
    time_stamp = bd_time.strftime('%Y-%m-%d %H:%M:%S')
    print(type(time_stamp))
    print("TIME STAMP --------------->",time_stamp)
    return time_stamp

def current_time():
    bd_timezone = timezone('Asia/Dhaka')
    bd_time = datetime.now(bd_timezone)
    time_stamp = bd_time.strftime('%H')
    return time_stamp


def location_from_address_combined(address):
    try:
        API_KEY = APIKey.objects.get(key_type=2).key_value
    except APIKey.DoesNotExist:
        print("API KEY DOES NOT EXIST")
        API_KEY = "AIzaSyACjdaw1GGQJvjm8H8TUSQwAuuimzJ055c"

    params = {
        'key': API_KEY,
        'address': address
    }
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    response = requests.get(base_url, params=params).json()
    response.keys()
    # print("line 14", response)
    if response['status'] == 'OK':
        geometry = response['results'][0]['geometry']
        lat = geometry['location']['lat']
        lon = geometry['location']['lng']
        location = {
            'latitude': lat,
            'longitude': lon,

        }
    else:
        location = {
            'error_message': response
        }

    # print("line 23", location)
    return location


def convert_weather_code_to_description(weather_code):
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Fog",
        51: "Drizzle",
        53: "Drizzle",
        55: "Drizzle",
        56: "Freezing Drizzle",
        57: "Freezing Drizzle",
        61: "Rain",
        63: "Rain",
        65: "Rain",
        66: "Freezing Rain",
        67: "Freezing Rain",
        71: "Snowfall",
        73: "Snowfall",
        75: "Snowfall",
        77: "Snow grains",
        80: "Rain showers",
        81: "Rain showers",
        82: "Rain showers",
        85: "Snow showers",
        86: "Snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm",
        99: "Thunderstorm",
    }
    return weather_codes.get(weather_code, "Unknown")


def create_new_weather(location, base_url: str):
    from device.models import Weather

    response = requests.get(base_url)

    data = response.json()
    current_weather = data["current_weather"]
    current_time = current_weather["time"]
    hourly_data = data["hourly"]
    time_list = hourly_data["time"]

    current_time_dt = datetime.strptime(current_time, "%Y-%m-%dT%H:%M")

    # Round up the time to the closest hour
    rounded_time = (current_time_dt + timedelta(hours=1)).replace(minute=0, second=0)

    # Convert the rounded time back to a string in the format "YYYY-MM-DDTHH:00"
    rounded_time_str = rounded_time.strftime("%Y-%m-%dT%H:00")

    current_time_index = time_list.index(rounded_time_str)
    print(current_time_index)

    # Collect the temperature, humidity, and solar radiation for the current time
    temperature = hourly_data["temperature_2m"][current_time_index]
    humidity = hourly_data["relativehumidity_2m"][current_time_index]
    solar_radiation = hourly_data["diffuse_radiation"][current_time_index]
    weather_code = current_weather["weathercode"]
    weather_description = convert_weather_code_to_description(int(weather_code))

    if solar_radiation >= 500:
        sunlight_level = "high"
    elif 200 <= solar_radiation < 500:
        sunlight_level = "medium"
    else:
        sunlight_level = "low"

    new_weather = Weather.objects.create(weather_district_id=location["district"], weather_temperature=temperature,
                                         sunlight_level=sunlight_level, solar_radiation=solar_radiation,
                                         weather_humidity=humidity, weather_description=weather_description,
                                         weather_created_at=current_date_time())



# old logic before nh4 calculation
# @shared_task(queue='device_task_queue')
# def save_device_data(raw_data, drd_dev_id, gateway_id):
#     from device.models import Device, DeviceData, Weather
#     from device.models import DeviceGateway, DeviceRawData,SensorConfiguration
#     from notification.tasks import send_threshold_notification
#     raw_data = sorted(raw_data, key=lambda x: x["ctime"])
#     print(raw_data)
#     for data in raw_data:
#         try:
#             val = round(float(data["Addrv"]),2)
#         except ValueError:
#             return
#
#         try:
#             device = Device.objects.get(id=drd_dev_id)
#             if len(data["Addr"]) == 0:
#                 address="255"
#             else: address=data["Addr"]
#             try:
#                 sensorconf = SensorConfiguration.objects.get(device_id=drd_dev_id,pid=data["Pid"],address=address)
#                 timestamp_str = data["ctime"]
#
#             # Convert the timestamp string to a datetime object
#                 try:
#                     # Adjust the format string based on the actual format of the timestamp
#                     datetime_obj = datetime.strptime(timestamp_str, "%Y/%m/%d %H:%M:%S")
#                 except ValueError as e:
#                     # Handle the case where the timestamp string has an invalid format
#                     print(f"Error: {e}")
#                     datetime_obj = None
#
#                 new_historical_device_data = DeviceDataHistory.objects.create(
#                     dvd_dvg_id = gateway_id,
#                     dvd_dev_id = drd_dev_id,
#                     dvd_sen_id = sensorconf.sensor_id,
#                     dvd_val = val*sensorconf.multiplier,
#                     dvd_created_at = current_date_time_obj(),
#                     company_id = device.company_id,
#                     device_data_time = datetime_obj,
#                     asset_id = device.dev_asset_id
#                 )
#
#                 try:
#                     device_data = DeviceData.objects.get(dvd_dvg_id = gateway_id,
#                                                                     dvd_dev_id = drd_dev_id,
#                                                                     dvd_sen_id = sensorconf.sensor_id,
#                                                                     company_id = device.company_id,
#                                                                     asset_id = device.dev_asset_id
#                                                                     )
#                     device_data.dvd_val = str(val*sensorconf.multiplier)
#                     device_data.dvd_created_at = current_date_time()
#                     device_data.device_data_time = datetime.fromisoformat(datetime_obj.isoformat())
#
#
#                     device_data.save()
#                 except DeviceData.DoesNotExist:
#
#                     device_data = DeviceData.objects.create(
#                                                             dvd_dvg_id = gateway_id,
#                                                             dvd_dev_id = drd_dev_id,
#                                                             dvd_sen_id = sensorconf.sensor_id,
#                                                             dvd_val = val*sensorconf.multiplier,
#                                                             dvd_created_at = current_date_time_obj(),
#                                                             company_id = device.company_id,
#                                                             device_data_time = datetime_obj,
#                                                             asset_id = device.dev_asset_id
#                                                             )
#                 send_threshold_notification.delay(device_data_id=device_data.id)
#             except SensorConfiguration.DoesNotExist:
#                 print(f"SENSOR of pid {data["Pid"]} or address {address} DOES NOT EXIST FOR THIS DEVICE")
#
#         except Exception:
#             traceback.print_exc()





def calculate_nh3(tan_ppm, pH, temp_celsius):
    try:
        print(f"Calculating NH3 with TAN={tan_ppm}, pH={pH}, Temp={temp_celsius}")
        temp_kelvin = temp_celsius + 273.15
        pKa = 0.09018 + (2729.92 / temp_kelvin)
        nh3_fraction = 1 / (1 + 10 ** (pKa - pH))
        nh3_ppm = tan_ppm * nh3_fraction
        return nh3_ppm, nh3_fraction
    except Exception as e:
        print(f"NH3 Calculation failed: {e}")
        return 0.0, 0.0

# having issue with nh4 apply
# @shared_task(queue='device_task_queue')
# def save_device_data(raw_data, drd_dev_id, gateway_id):
#     from device.models import Device, DeviceData, DeviceGateway, SensorConfiguration, DeviceDataHistory
#     from notification.tasks import send_threshold_notification
#
#     try:
#         device = Device.objects.get(id=drd_dev_id)
#     except Device.DoesNotExist:
#         print(f"Device with id {drd_dev_id} not found.")
#         return
#
#     raw_data = sorted(raw_data, key=lambda x: x["ctime"])
#
#     tan_val, pH_val, temp_val = None, None, None
#
#     for data in raw_data:
#         try:
#             val = round(float(data["Addrv"]), 2)
#         except ValueError:
#             continue
#
#         address = data["Addr"] if data["Addr"] else "255"
#
#         try:
#             sensorconf = SensorConfiguration.objects.get(
#                 device_id=drd_dev_id,
#                 pid=data["Pid"],
#                 address=address
#             )
#
#             try:
#                 datetime_obj = datetime.strptime(data["ctime"], "%Y/%m/%d %H:%M:%S")
#             except ValueError:
#                 print(f"Invalid datetime format: {data['ctime']}")
#                 datetime_obj = None
#
#             scaled_val = val * (sensorconf.multiplier or 1)
#
#             # Save to history
#             DeviceDataHistory.objects.create(
#                 dvd_dvg_id=gateway_id,
#                 dvd_dev_id=drd_dev_id,
#                 dvd_sen_id=sensorconf.sensor_id,
#                 dvd_val=scaled_val,
#                 dvd_created_at=current_date_time_obj(),
#                 company_id=device.company_id,
#                 device_data_time=datetime_obj,
#                 asset_id=device.dev_asset_id
#             )
#
#             # Save or update DeviceData
#             device_data, _ = DeviceData.objects.update_or_create(
#                 dvd_dvg_id=gateway_id,
#                 dvd_dev_id=drd_dev_id,
#                 dvd_sen_id=sensorconf.sensor_id,
#                 company_id=device.company_id,
#                 asset_id=device.dev_asset_id,
#                 defaults={
#                     'dvd_val': scaled_val,
#                     'dvd_created_at': current_date_time(),
#                     'device_data_time': datetime_obj
#                 }
#             )
#
#             send_threshold_notification.delay(device_data_id=device_data.id)
#
#             # Capture values for NH3 calc
#             pid_int = int(data["Pid"])
#             address_int = int(address)
#
#             if pid_int == 5 and address_int == 255:
#                 tan_val = scaled_val
#             elif (pid_int, address_int) == (1, 1):
#                 pH_val = scaled_val
#             elif (pid_int, address_int) == (3, 2):
#                 temp_val = scaled_val
#
#         except SensorConfiguration.DoesNotExist:
#             print(f"Sensor not found for pid={data['Pid']} address={address}")
#         except Exception:
#             traceback.print_exc()
#
#     # NH3 CALCULATION
#     if tan_val is not None:
#         print(f"tan_val for pid={data['Pid']} address={address} is {tan_val}")
#         print(f"pH_val and temp  for pid={data['Pid']} address={address} is {pH_val} and {temp_val}")
#         if pH_val is None or temp_val is None:
#             nh3_ppm = 0.0
#         else:
#             nh3_ppm, _ = calculate_nh3(tan_val, pH_val, temp_val)
#             print(f"nh3_ppm for pid={data['Pid']} address={address} is {nh3_ppm}")
#
#         try:
#             nh3_sensor = SensorConfiguration.objects.filter(
#                 device_id=drd_dev_id,
#                 sensor__sensor_name__icontains="NH3"
#             ).first()
#
#             if nh3_sensor:
#                 DeviceDataHistory.objects.create(
#                     dvd_dvg_id=gateway_id,
#                     dvd_dev_id=drd_dev_id,
#                     dvd_sen_id=nh3_sensor.sensor_id,
#                     dvd_val=round(nh3_ppm, 4),
#                     dvd_created_at=current_date_time_obj(),
#                     company_id=device.company_id,
#                     device_data_time=current_date_time_obj(),
#                     asset_id=device.dev_asset_id
#                 )
#
#                 DeviceData.objects.update_or_create(
#                     dvd_dvg_id=gateway_id,
#                     dvd_dev_id=drd_dev_id,
#                     dvd_sen_id=nh3_sensor.sensor_id,
#                     company_id=device.company_id,
#                     asset_id=device.dev_asset_id,
#                     defaults={
#                         'dvd_val': round(nh3_ppm, 4),
#                         'dvd_created_at': current_date_time(),
#                         'device_data_time': current_date_time_obj()
#                     }
#                 )
#         except Exception:
#             traceback.print_exc()

@shared_task(queue='device_task_queue')
def save_device_data(raw_data, drd_dev_id, gateway_id):
    from device.models import Device, DeviceData, SensorConfiguration, DeviceDataHistory
    from notification.tasks import send_threshold_notification
    from datetime import datetime
    import traceback

    try:
        device = Device.objects.get(id=drd_dev_id)
    except Device.DoesNotExist:
        logger.error(f"Device with id={drd_dev_id} not found.")
        return

    raw_data = sorted(raw_data, key=lambda x: x["ctime"])
    tan_val, pH_val, temp_val = None, None, None

    for data in raw_data:
        try:
            val = round(float(data["Addrv"]), 2)
        except (ValueError, TypeError):
            logger.warning(f"Invalid Addrv: {data.get('Addrv')}")
            continue

        try:
            pid = int(data["Pid"])
        except (ValueError, TypeError):
            logger.warning(f"Invalid Pid: {data.get('Pid')}")
            continue

        try:
            address = int(data["Addr"]) if data.get("Addr") else 255
        except (ValueError, TypeError):
            logger.warning(f"Invalid Addr: {data.get('Addr')}")
            address = 255

        try:
            sensorconf = SensorConfiguration.objects.get(
                device_id=drd_dev_id,
                pid=pid,
                address=address
            )
        except SensorConfiguration.DoesNotExist:
            logger.info(f"SensorConfiguration not found: pid={pid}, address={address}")
            continue

        try:
            datetime_obj = datetime.strptime(data["ctime"], "%Y/%m/%d %H:%M:%S")
        except (ValueError, TypeError):
            logger.warning(f"Invalid datetime format: {data.get('ctime')}")
            datetime_obj = None

        sensor_id = sensorconf.sensor_id
        sensor_name = getattr(sensorconf.sensor, 'sensor_name', 'Unknown')
        scaled_val = round(val * (sensorconf.multiplier or 1), 4)
        current_time = current_date_time_obj()

        logger.debug(f"Sensor: {sensor_name} | pid={pid} | addr={address} | scaled_val={scaled_val}")

        # DeviceDataHistory insertion
        try:
            DeviceDataHistory.objects.create(
                dvd_dvg_id=gateway_id,
                dvd_dev_id=drd_dev_id,
                dvd_sen_id=sensor_id,
                dvd_val=scaled_val,
                dvd_created_at=current_time,
                company_id=device.company_id,
                device_data_time=datetime_obj,
                asset_id=device.dev_asset_id
            )
            logger.info(f"✅ DeviceDataHistory saved for sensor: {sensor_name}")
        except Exception as e:
            logger.error(f"❌ Error saving DeviceDataHistory for sensor={sensor_name}, pid={pid}, addr={address}: {str(e)}")
            logger.debug(traceback.format_exc())

        # DeviceData update
        try:
            device_data, created = DeviceData.objects.update_or_create(
                dvd_dvg_id=gateway_id,
                dvd_dev_id=drd_dev_id,
                dvd_sen_id=sensor_id,
                company_id=device.company_id,
                asset_id=device.dev_asset_id,
                defaults={
                    'dvd_val': scaled_val,
                    'dvd_created_at': current_date_time(),
                    'device_data_time': datetime_obj
                }
            )
            logger.info(f"{'✅ Created' if created else '✅ Updated'} DeviceData for sensor: {sensor_name}")
            send_threshold_notification.delay(device_data_id=device_data.id)
        except Exception as e:
            logger.error(f"❌ Error updating DeviceData for sensor={sensor_name}: {str(e)}")
            logger.debug(traceback.format_exc())

        # Save for NH3 calculation
        if (pid, address) == (5, 255): tan_val = scaled_val
        elif (pid, address) in ((1, 1), (1, 0)): pH_val = scaled_val
        #elif (pid, address) == (3, 2): temp_val = scaled_val
        elif (pid, address) in ((3, 2), (2, 1)): temp_val = scaled_val 

    # NH3 calculation
    if tan_val is not None:
        logger.info(f"NH3 Calc Inputs — TAN: {tan_val}, pH: {pH_val}, Temp: {temp_val}")
        nh3_ppm = 0.0
        if pH_val is not None and temp_val is not None:
            try:
                nh3_ppm, _ = calculate_nh3(tan_val, pH_val, temp_val)
                nh3_ppm = round(nh3_ppm, 4)
                logger.info(f"✅ NH3 Calculated: {nh3_ppm}")
            except Exception as e:
                logger.error("❌ Error calculating NH3")
                logger.debug(traceback.format_exc())
        else:
            logger.warning("⚠️ pH or temperature missing — NH3 calculation skipped")

        nh3_sensor = SensorConfiguration.objects.filter(
            device_id=drd_dev_id,
            sensor__sensor_name__icontains="NH3"
        ).first()

        if nh3_sensor:
            try:
                DeviceDataHistory.objects.create(
                    dvd_dvg_id=gateway_id,
                    dvd_dev_id=drd_dev_id,
                    dvd_sen_id=nh3_sensor.sensor_id,
                    dvd_val=nh3_ppm,
                    dvd_created_at=current_date_time_obj(),
                    company_id=device.company_id,
                    device_data_time=current_date_time_obj(),
                    asset_id=device.dev_asset_id
                )
                DeviceData.objects.update_or_create(
                    dvd_dvg_id=gateway_id,
                    dvd_dev_id=drd_dev_id,
                    dvd_sen_id=nh3_sensor.sensor_id,
                    company_id=device.company_id,
                    asset_id=device.dev_asset_id,
                    defaults={
                        'dvd_val': nh3_ppm,
                        'dvd_created_at': current_date_time(),
                        'device_data_time': current_date_time_obj()
                    }
                )
                logger.info("✅ NH3 data saved.")
            except Exception as e:
                logger.error("❌ Error saving NH3 data")
                logger.debug(traceback.format_exc())
        else:
            logger.info("ℹ️ NH3 sensor not configured.")



@shared_task
def get_weather_report():
    from device.models import Device, DeviceData, Weather
    # Enter your API key here
    locations = AssetsProperties.objects.select_related('district').values('district','district__district', 'district__lattitude',
                                                                           'district__longitude').filter(
        district__isnull=False).distinct()
    # weather = Weather.objects.all()
    for location in locations:
        try:

            base_url = f"https://api.open-meteo.com/v1/forecast?latitude={location['district__lattitude']}&longitude={location['district__longitude']}&hourly=temperature_2m,relativehumidity_2m,weathercode,diffuse_radiation&current_weather=true&forecast_days=1&timezone=auto"
            print(base_url)
            create_new_weather(location=location, base_url=base_url)
        except:
            traceback.print_exc()


@shared_task
def device_status():
    from device.models import Device, DeviceData, Weather
    try:
        bd_timezone = timezone('Asia/Dhaka')
        bd_time = datetime.now(bd_timezone)

        earlier_datetime = bd_time - timedelta(minutes=30)
        devices = Device.objects.prefetch_related(
            Prefetch(
                "device_data"
            )
        ).all()

        for device in devices:
            try:
                if device.device_data.last():
                    print(device.device_data)
                    device.dev_status = 0

                    if device.device_data.last().dvd_created_at.strftime('%Y-%m-%d %H:%M:%S') > earlier_datetime.strftime(
                            '%Y-%m-%d %H:%M:%S'):
                        device.dev_status = 1
                        print("device is online")
                    else:
                        print("device is offline")

                    device.save()
            except:
                traceback.print_exc()
                print("Cannot change device status")
    except:
        traceback.print_exc()

@shared_task
def sensor_status():
    from device.models import Sensor, SensorConfiguration, DeviceData

    try:
        bd_timezone = timezone('Asia/Dhaka')
        bd_time = datetime.now(bd_timezone)

        earlier_datetime = bd_time - timedelta(minutes=30)
        sensors = SensorConfiguration.objects.all()

        for sensor in sensors:
            try:
                device_data = DeviceData.objects.filter(dvd_sen=sensor.sensor).last()
                if device_data:
                    sensor.sensor_status = 0
                    if device_data.dvd_created_at.strftime('%Y-%m-%d %H:%M:%S') > earlier_datetime.strftime(
                            '%Y-%m-%d %H:%M:%S'):
                        sensor.sensor_status = 1
                        print("sensor is online")
                    else:
                        print("sensor is offline")
            
                    sensor.save()
            except:
                traceback.print_exc()
                print("Cannot change sensor status")
    except:
        traceback.print_exc()

@shared_task
def gateway_status():
    from device.models import DeviceGateway

    try:
        gateways = DeviceGateway.objects.all()

        bd_timezone = timezone('Asia/Dhaka')
        bd_time = datetime.now(bd_timezone)

        earlier_datetime = bd_time - timedelta(minutes=1)
        print("EARLIER DATETIME GATEWAY", earlier_datetime)
        for gateway in gateways:
            if gateway.dvg_updated_at.strftime('%Y-%m-%d %H:%M:%S') > earlier_datetime.strftime('%Y-%m-%d %H:%M:%S'):
                print("gateway is online")
                gateway.gateway_status = 1
                gateway.save()
            else:
                gateway.gateway_status = 0
                gateway.save()
    except:
        traceback.print_exc()
