# mqtt_publisher.py (short version – no de-dup here)
import uuid
import logging
import threading
import paho.mqtt.client as mqtt
from django.utils import timezone
from device.models import AeratorCommandLog

BROKER_HOST = '66.29.151.40'
BROKER_PORT = 1883
MQTT_USERNAME = None
MQTT_PASSWORD = None
MQTT_KEEPALIVE = 30

_mqtt_client = None
_client_lock = threading.RLock()


def _on_disconnect(client, userdata, rc):
    global _mqtt_client
    logging.warning(f"MQTT disconnected (rc={rc}). Will recreate client on next publish.")
    with _client_lock:
        try:
            client.loop_stop()
            client.disconnect()
        except Exception:
            pass
        _mqtt_client = None


def get_mqtt_client() -> mqtt.Client:
    global _mqtt_client
    with _client_lock:
        if _mqtt_client is None:
            client_id = f"api_publisher_{uuid.uuid4().hex[:6]}"
            c = mqtt.Client(client_id=client_id)
            if MQTT_USERNAME and MQTT_PASSWORD:
                c.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
            c.on_disconnect = _on_disconnect
            c.reconnect_delay_set(min_delay=1, max_delay=30)
            c.connect(BROKER_HOST, BROKER_PORT, keepalive=MQTT_KEEPALIVE)
            c.loop_start()
            _mqtt_client = c
            logging.info(f"Created MQTT publisher client {client_id} -> {BROKER_HOST}:{BROKER_PORT}")
        return _mqtt_client


def publish_command(aerator, turn_on: bool, qos: int = 1, timeout: float = 5.0) -> AeratorCommandLog:
    if not aerator.aerator_id or '/' in aerator.aerator_id.strip():
        raise ValueError("Invalid or missing aerator_id; cannot publish to MFA/CMD/<id>.")

    topic = f"MFA/CMD/{aerator.aerator_id.strip()}"
    payload = '1' if turn_on else '0'
    client = get_mqtt_client()

    try:
        logging.info(f"Publishing to {topic}: {payload}")
        info = client.publish(topic, payload=payload, qos=qos, retain=False)
        info.wait_for_publish(timeout=timeout)

        if not info.is_published():
            raise RuntimeError(f"MQTT publish timeout or not published for {topic}")
        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"MQTT publish failed (rc={info.rc})")

        cmd_log = AeratorCommandLog.objects.create(
            aerator=aerator,
            command_on=turn_on,
            sent_at=timezone.now()
        )
        logging.info(f"Sent {'ON' if turn_on else 'OFF'} → {topic} (log #{cmd_log.id})")
        return cmd_log

    except Exception as e:
        logging.exception(f"Failed to publish command to {topic}: {e}")
        _on_disconnect(client, None, rc=-1)
        raise
