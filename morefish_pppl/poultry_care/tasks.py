import traceback
from datetime import datetime, timedelta

from celery import shared_task
from celery.utils.log import get_task_logger
from pytz import timezone

logger = get_task_logger(__name__)



@shared_task
def check_poultry_thresholds(device_id: int, sensor_name: str, value: float, sensor_id: int):

    from .models import Device, Sensor, PoultryNotification
    from users.models import FCM
    from notification.messaging import fcm_by_ron  

    try:
        device = Device.objects.select_related('farm', 'company').get(id=device_id)
        sensor = Sensor.objects.get(id=sensor_id)
    except (Device.DoesNotExist, Sensor.DoesNotExist):
        logger.info(f'Sensor (id={sensor_id}) or Device (id={device_id}) not found — skipping threshold check')
        return

    try:
        fval = float(value)
    except (TypeError, ValueError):
        logger.warning(f'Non-numeric value for {sensor_name}: {value}')
        return

    urgency = None
    message = ''

    invalid_low  = sensor.min_invalid is not None and fval < sensor.min_invalid
    invalid_high = sensor.max_invalid is not None and fval > sensor.max_invalid

    if invalid_low or invalid_high:
        urgency = PoultryNotification.UrgencyLevel.DANGER
        message = (f'SENSOR FAULT: {sensor.name} '
                   f'reported an impossible value of {fval} {sensor.unit or ""}. '
                   f'Please check the sensor.')
    elif fval > sensor.max_value:
        urgency = PoultryNotification.UrgencyLevel.WARNING
        message = (f'HIGH ALERT: {sensor.name} '
                   f'is {fval} {sensor.unit or ""}, above the safe maximum of {sensor.max_value}.')
    elif fval < sensor.min_value:
        urgency = PoultryNotification.UrgencyLevel.WARNING
        message = (f'LOW ALERT: {sensor.name} '
                   f'is {fval} {sensor.unit or ""}, below the safe minimum of {sensor.min_value}.')

    if urgency is None:
        return

    last_notif = PoultryNotification.objects.filter(
        device=device,
        sensor_id=sensor_id,          
        urgency=urgency,
    ).order_by('-notified_at').first()

    if last_notif:
        from django.utils import timezone as dj_tz
        age = dj_tz.now() - last_notif.notified_at
        if age.total_seconds() < 1800:  # 30 minutes
            logger.info(f'Suppressed duplicate notification for {sensor_name} on device {device_id}')
            return

    farm  = device.farm
    users = farm.users.all() if farm else []

    for user in users:
        notif = PoultryNotification.objects.create(
            device=device,
            sensor=sensor,              
            value=fval,
            urgency=urgency,
            message=message,
            user=user,
        )

        try:
            fcm_token = FCM.objects.get(user_id=user.id).token
            title = f'Poultry Alert — {farm.name if farm else device.client_id}'
            fcm_by_ron(fcm_token, title, message)
            logger.info(f'FCM sent to user={user.id} for device={device_id}, sensor={sensor_name}')
        except FCM.DoesNotExist:
            logger.info(f'No FCM token for user={user.id}')
        except Exception:
            logger.warning(f'FCM failed for user={user.id}')
            traceback.print_exc()



@shared_task
def poultry_device_status():

    from .models import Device

    try:
        bd_tz       = timezone('Asia/Dhaka')
        now         = datetime.now(bd_tz)
        cutoff      = now - timedelta(minutes=30)
        cutoff_str  = cutoff.strftime('%Y-%m-%d %H:%M:%S')

        for device in Device.objects.all():
            try:
                if device.latest_reading_timestamp:
                    ts_str = device.latest_reading_timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    device.dev_status = 1 if ts_str > cutoff_str else 0
                else:
                    device.dev_status = 0
                device.save(update_fields=['dev_status'])
            except Exception:
                traceback.print_exc()

        logger.info('Poultry device status check complete.')
    except Exception:
        traceback.print_exc()