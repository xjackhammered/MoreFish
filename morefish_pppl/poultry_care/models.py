import datetime
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


def current_date_time():
    from pytz import timezone
    bd_timezone = timezone('Asia/Dhaka')
    return datetime.datetime.now(bd_timezone)


ONLINE_STATUS = (
    (0, 'Offline'),
    (1, 'Online'),
    (2, 'Problem'),
)

DEVICE_STATUS_CHOICES = ONLINE_STATUS  


class Sensor(models.Model):

    name = models.CharField(max_length=50, unique=True)
    unit = models.CharField(max_length=20, blank=True, null=True)
    min_value = models.FloatField(help_text="Minimum safe value")
    max_value = models.FloatField(help_text="Maximum safe value")
    min_invalid = models.FloatField(null=True, blank=True,
                                    help_text="Physically impossible low")
    max_invalid = models.FloatField(null=True, blank=True,
                                    help_text="Physically impossible high")
    icon = models.ImageField(upload_to='uploads/poultry/sensor_icons/',
                             blank=True, null=True)

    def __str__(self):
        return self.name


class PoultryFarm(models.Model):

    name     = models.CharField(max_length=200)
    location = models.TextField(blank=True, null=True)
    company  = models.ForeignKey(
        'users.Company',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='poultry_farms'
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='poultry_farms',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Poultry Farm'
        verbose_name_plural = 'Poultry Farms'

    def __str__(self):
        return self.name


class Device(models.Model):

    farm = models.OneToOneField(
        PoultryFarm,
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='device'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='poultry_devices'
    )
    client_id = models.CharField(max_length=100, unique=True)
    name      = models.CharField(max_length=200, blank=True, null=True)
    location  = models.CharField(max_length=200, blank=True, null=True)
    company   = models.ForeignKey(
        'users.Company',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='poultry_devices'
    )
    dev_status = models.IntegerField(choices=ONLINE_STATUS, default=1)

    latest_reading_timestamp = models.DateTimeField(null=True, blank=True)
    latest_reading_data      = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Poultry Device'
        verbose_name_plural = 'Poultry Devices'

    def __str__(self):
        return f"{self.name or self.client_id}"


class SensorConfig(models.Model):

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='sensor_configs'
    )
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name='configs'
    )
    multiplier = models.FloatField(
        default=1.0,
        help_text='Raw value × multiplier = stored value'
    )
    sensor_status = models.IntegerField(choices=DEVICE_STATUS_CHOICES, default=1)

    class Meta:
        unique_together = ('device', 'sensor')
        verbose_name        = 'Sensor Configuration'
        verbose_name_plural = 'Sensor Configurations'

    def __str__(self):
        return f"{self.device} — {self.sensor.name}"


class PoultryDeviceData(models.Model):

    device      = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='device_data'
    )
    sensor      = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name='device_data',
        null = True,
        blank=True
    )
    value       = models.FloatField(null=True, blank=True)
    data_time   = models.DateTimeField(null=True, blank=True,
                                       help_text='Timestamp from the device payload')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together     = ('device', 'sensor')
        verbose_name        = 'Poultry Device Data (Latest)'
        verbose_name_plural = 'Poultry Device Data (Latest)'
        indexes = [
            models.Index(fields=['device', 'sensor']),
        ]

    def __str__(self):
        return f"{self.device} — {self.sensor.name} = {self.value}"


class SensorReading(models.Model):

    device          = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='readings')
    timestamp       = models.DateTimeField()
    temperature     = models.FloatField(null=True, blank=True)
    ref_temperature = models.FloatField(null=True, blank=True)
    humidity        = models.FloatField(null=True, blank=True)
    light_intensity = models.FloatField(null=True, blank=True)
    nh3_gas         = models.FloatField(null=True, blank=True)
    tvoc            = models.FloatField(null=True, blank=True)
    co2             = models.FloatField(null=True, blank=True)
    aqi             = models.IntegerField(null=True, blank=True)
    pm25            = models.FloatField(null=True, blank=True)
    pm10            = models.FloatField(null=True, blank=True)
    sound_db        = models.FloatField(null=True, blank=True)
    methane_ppm     = models.FloatField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes  = [
            models.Index(fields=['device', 'timestamp']),
            models.Index(fields=['device', 'created_at']),
        ]
        verbose_name        = 'Sensor Reading'
        verbose_name_plural = 'Sensor Readings'

    def __str__(self):
        return f"{self.device.client_id} @ {self.timestamp}"


class RawMQTTData(models.Model):
 
    device      = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='raw_mqtt_data')
    topic       = models.CharField(max_length=255)
    payload     = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Raw MQTT Data'
        verbose_name_plural = 'Raw MQTT Data'

    def __str__(self):
        return f"{self.device.client_id} — {self.received_at}"


class PoultryNotification(models.Model):

    class UrgencyLevel(models.TextChoices):
        INFO    = 'INFO',    _('Info')
        WARNING = 'WARNING', _('Warning')
        DANGER  = 'DANGER',  _('Danger')

    device      = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='notifications')
    sensor      = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    value       = models.FloatField()
    urgency     = models.CharField(max_length=20, choices=UrgencyLevel.choices,
                                   default=UrgencyLevel.WARNING)
    message     = models.TextField()
    is_read     = models.BooleanField(default=False)
    notified_at = models.DateTimeField(auto_now_add=True)
    user        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='poultry_notifications'
    )

    class Meta:
        ordering            = ['-notified_at']
        verbose_name        = 'Poultry Notification'
        verbose_name_plural = 'Poultry Notifications'

    def __str__(self):
        return f"[{self.urgency}] {self.device} — {self.sensor.name} = {self.value}"