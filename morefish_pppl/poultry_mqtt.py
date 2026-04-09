"""
poultry_mqtt.py
MQTT listener for the Poultry Care module.
Connects to broker.hivemq.com, subscribes to PoultryCare/DTU,
parses incoming JSON payloads, applies the per-sensor multiplier,
and saves to the database.

After each save it fires a Celery task to check sensor thresholds
and send push notifications if values are out of range.

Run as a standalone process:
    python poultry_mqtt.py
"""
import os
import json
import time
import logging
from datetime import datetime

import django
import paho.mqtt.client as mqtt

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "morefish_pppl.settings")
django.setup()

from poultry_care.models import (
    Device, SensorReading, RawMQTTData, PoultryDeviceData, SensorConfig, Sensor
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MQTT_BROKER     = "broker.hivemq.com"   
MQTT_PORT       = 1883
MQTT_TOPIC      = "PoultryCare/DTU"
RECONNECT_DELAY = 5


def _get_sensor_config_map(device):
    """
    Fetch all SensorConfig for this device, including the linked Sensor.
    Returns a dict: { sensor_name: {'multiplier': float, 'sensor_obj': Sensor} }
    Only sensors that are configured for this device will be processed.
    """
    configs = SensorConfig.objects.filter(device=device).select_related('sensor')
    mapping = {}
    for cfg in configs:
        sensor_name = cfg.sensor.name
        mapping[sensor_name] = {
            'multiplier': cfg.multiplier,
            'sensor': cfg.sensor,
        }
    return mapping


# ─── MQTT Callbacks ───────────────────────────────────────────────────────────
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logger.info("Connected to MQTT broker")
        client.subscribe(MQTT_TOPIC)
        logger.info(f"Subscribed to {MQTT_TOPIC}")
    else:
        logger.error(f"Connection failed with code {rc}")


def on_disconnect(client, userdata, rc):
    if rc != 0:
        logger.warning("Unexpected MQTT disconnection")


def on_message(client, userdata, msg):
    payload_str = msg.payload.decode()
    logger.info(f"RAW MESSAGE: {payload_str[:200]}...")
    logger.info(f"Message received on {msg.topic}")

    try:
        data = json.loads(payload_str)
        client_id = data.get("client_id")
        timestamp = data.get("timestamp")
        raw_sensor_data = data.get("data", {})

        if isinstance(raw_sensor_data, list):
            if len(raw_sensor_data) == 0:
                logger.warning("Empty data list in payload")
                return
            sensor_data = {}
            for item in raw_sensor_data:
                if isinstance(item, dict):
                    sensor_data.update(item)
            logger.info(f"Merged {len(raw_sensor_data)} items into sensor data dict")
        else:
            sensor_data = raw_sensor_data

        if not client_id:
            logger.warning("client_id missing in payload")
            return

        device = Device.objects.filter(client_id=client_id).first()
        if not device:
            logger.warning(f"Unknown device: {client_id}")
            return

        # ── Save raw payload (audit trail) ────────────────────────────────────
        RawMQTTData.objects.create(
            device=device,
            topic=msg.topic,
            payload=data
        )

        # ── Parse timestamp (naive, local time Asia/Dhaka) ────────────────────
        ts = None
        if timestamp:
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
                try:
                    ts = datetime.strptime(timestamp, fmt)
                    break
                except ValueError:
                    continue
        if ts is None:
            logger.warning(f"Invalid timestamp: {timestamp} — using current time")
            ts = datetime.now()          # naive datetime

        # ── Load configured sensors for this device ───────────────────────────
        sensor_map = _get_sensor_config_map(device)

        if not sensor_map:
            logger.warning(f"No sensor configs found for device {client_id}")
            return

        # ── Build sensor fields, apply multiplier, skip unconfigured sensors ──
        sensor_fields = {}
        processed_sensors = []  # keep track for threshold checks

        for payload_key, raw_value in sensor_data.items():
            if payload_key not in sensor_map:
                logger.debug(f"Skipping unconfigured sensor: {payload_key}")
                continue

            config_info = sensor_map[payload_key]
            multiplier = config_info['multiplier']
            sensor_obj = config_info['sensor']

            try:
                scaled_value = float(raw_value) * multiplier
            except (TypeError, ValueError):
                scaled_value = raw_value

            sensor_fields[payload_key] = scaled_value
            processed_sensors.append((payload_key, scaled_value, sensor_obj))

        if not sensor_fields:
            logger.warning(f"No configured sensor data to save for device {client_id}")
            return

        # ── Save to SensorReading (append-only history table) ─────────────────
        valid_fields = {}
        for field_name, value in sensor_fields.items():
            if hasattr(SensorReading, field_name):
                valid_fields[field_name] = value

        SensorReading.objects.create(
            device=device,
            timestamp=ts,
            **valid_fields
        )

        # ── Update PoultryDeviceData (latest-per-sensor snapshot table) ───────
        for sensor_name, value in sensor_fields.items():
            try:
                sensor_obj = Sensor.objects.get(name=sensor_name)
                PoultryDeviceData.objects.update_or_create(
                    device=device,
                    sensor=sensor_obj,
                    defaults={
                        'value': value,
                        'data_time': ts,
                    }
                )
            except Sensor.DoesNotExist:
                logger.warning(f"Sensor '{sensor_name}' not found in DB – skipping snapshot")

        # ── Update Device.latest_reading_data (JSON snapshot for quick dash) ──
        device.latest_reading_timestamp = ts
        device.latest_reading_data = sensor_fields
        device.save(update_fields=["latest_reading_timestamp", "latest_reading_data"])

        logger.info(f"Data saved for device {client_id}")

        # ── Fire threshold check tasks for each processed sensor ──────────────
        logger.info(f"Processed sensors count: {len(processed_sensors)}")
        from poultry_care.tasks import check_poultry_thresholds
        for sensor_name, value, sensor_obj in processed_sensors:
            try:
                logger.info(f"Dispatching threshold check for {sensor_name} (value={value})")
                result = check_poultry_thresholds.delay(
                    device_id=device.id,
                    sensor_name=sensor_name,
                    value=float(value),
                    sensor_id=sensor_obj.id
                )
                logger.info(f"Task dispatched: {result.id}")
            except Exception as e:
                logger.exception(f"Failed to dispatch task for {sensor_name}: {e}")

    except json.JSONDecodeError:
        logger.error("Invalid JSON payload")
    except Exception as e:
        logger.exception(f"Error processing MQTT message: {e}")


# ─── Client ───────────────────────────────────────────────────────────────────
def create_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    return client


# ─── Main loop with auto-reconnect ───────────────────────────────────────────
def start_mqtt():
    client = create_client()
    while True:
        try:
            logger.info(f"Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT}...")
            client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            client.loop_forever()
        except Exception as e:
            logger.error(f"MQTT connection error: {e}")
            logger.info(f"Reconnecting in {RECONNECT_DELAY} seconds...")
            time.sleep(RECONNECT_DELAY)
            client = create_client()


if __name__ == "__main__":
    start_mqtt()