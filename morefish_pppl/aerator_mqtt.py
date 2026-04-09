#!/usr/bin/env python3
import os
import logging
import uuid
import django
import paho.mqtt.client as mqtt
from django.utils import timezone

# ─── Django setup ────────────────────────────────────
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'morefish_pppl.settings')
django.setup()

from device.models import Aerator, AeratorStatusLog, AeratorCommandLog

# ─── CONFIG ──────────────────────────────────────────
BROKER_HOST = '66.29.151.40'
BROKER_PORT = 1883
TOPIC_CMD = 'MFA/CMD/+'
TOPIC_STATUS = 'MFA/STATUS/+'

# ─── LOGGING ────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# ─── MQTT CALLBACKS ─────────────────────────────────
def on_connect(client, userdata, flags, rc):
    if rc != 0:
        logging.error(f"MQTT connect failed (rc={rc})")
        return
    client.subscribe([(TOPIC_CMD, 0), (TOPIC_STATUS, 0)])
    logging.info(f"Subscribed to: {TOPIC_CMD} and {TOPIC_STATUS}")


def on_message(client, userdata, msg):
    parts = msg.topic.split('/')  # ['MFA', 'CMD'|'STATUS', 'A001']
    if len(parts) != 3 or parts[0] != 'MFA':
        return

    action = parts[1].upper()  # CMD or STATUS
    aer_id = parts[2]  # e.g. A001
    payload = msg.payload.decode().strip().lower()

    # Lookup aerator using aerator_id as requested
    try:
        aerator = Aerator.objects.get(aerator_id=aer_id)
    except Aerator.DoesNotExist:
        logging.error(f"Unknown aerator_id: {aer_id}")
        return

    if action == 'CMD':
        # Log the command we (or someone) published
        cmd_on = (payload == '1')
        AeratorCommandLog.objects.create(
            aerator=aerator,
            command_on=cmd_on
        )
        logging.info(f"Logged CMD {'ON' if cmd_on else 'OFF'} for {aer_id}")
        return

    if action == 'STATUS' and payload == 'executed':
        # Acknowledgement from device that last command executed
        try:
            cmd = AeratorCommandLog.objects.filter(
                aerator=aerator,
                acked=False
            ).latest('sent_at')
        except AeratorCommandLog.DoesNotExist:
            logging.info(f"No pending command for {aer_id}")
            return

        cmd.acked = True
        cmd.acked_at = timezone.now()
        cmd.save(update_fields=['acked', 'acked_at'])

        if not aerator.is_active:
            logging.info(f"Skipping inactive {aerator}")
            return

        if aerator.is_running != cmd.command_on:
            aerator.is_running = cmd.command_on
            aerator.save(update_fields=['is_running', 'updated_at'])
            AeratorStatusLog.objects.create(
                aerator=aerator,
                was_running=cmd.command_on
            )
            logging.info(f"{aerator} set to {'ON' if cmd.command_on else 'OFF'}")


def on_disconnect(client, userdata, rc):
    logging.warning("MQTT disconnected; will retry…")


# ─── ENTRY POINT ────────────────────────────────────
def main():
    client_id = f"mqtt_listener_{uuid.uuid4().hex[:8]}"
    client = mqtt.Client(client_id=client_id)

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    logging.info(f"Connecting to {BROKER_HOST}:{BROKER_PORT} as {client_id}…")
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_forever()


if __name__ == '__main__':
    main()
