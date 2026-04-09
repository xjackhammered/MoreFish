from django.db import models


# Create your models here.
class Notifications(models.Model):
    not_time = models.CharField(max_length=100, blank=True, null=True)
    not_urgency = models.CharField(max_length=100, blank=True, null=True)
    not_pond = models.CharField(max_length=100, blank=True, null=True)
    not_message_body = models.TextField(null=True, blank=True)
    not_warning = models.CharField(max_length=100, blank=True, null=True)
    not_warning_msg = models.CharField(max_length=1000, blank=True, null=True)
    not_value = models.CharField(max_length=1000, blank=True, null=True)
    not_color = models.CharField(null=True, blank=True, max_length=100)
    not_final = models.TextField(null=True, blank=True)
    not_sensor = models.ForeignKey('device.Sensor',null=True,blank=True,on_delete=models.SET_NULL)
    dev = models.ForeignKey("device.Device",null=True,blank=True,on_delete=models.CASCADE)
    not_user = models.ForeignKey(
        'users.User',
        related_name="notifications_user",
        on_delete=models.CASCADE, blank=True, null=True
    )
    not_date = models.CharField(max_length=100, blank=True, null=True)
    conf = models.ForeignKey("notification.Configuration",null=True,blank=True,on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'Notifications'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return "%s" % self.not_message_body


class Configuration(models.Model):
    class TypeChoices(models.TextChoices):
        INVALID = 'INV'
        MAX = 'MAX'
        MIN = 'MIN'
        GOOD = 'GOOD'
    con_code = models.CharField(max_length=50, null=True, blank=True)
    con_sensor = models.ForeignKey('device.Sensor',blank=True, null=True,on_delete=models.SET_NULL)
    con_urgency = models.CharField(max_length=100, blank=True, null=True)
    con_message_body = models.TextField(null=True, blank=True)
    con_warning_msg = models.CharField(max_length=100, blank=True, null=True)
    con_warning = models.CharField(max_length=100, blank=True, null=True)
    con_todo = models.CharField(max_length=1000, blank=True, null=True)
    con_created_at = models.DateTimeField(auto_now_add=True)
    con_color = models.CharField(max_length=150,null=True,blank=True)
    con_type = models.CharField(max_length=10, choices=TypeChoices.choices,default=TypeChoices.INVALID)
    def __str__(self):
        return "%s" % self.con_code
    
class NotificationThreshold(models.Model):
    thresh_device = models.OneToOneField("device.Device",null=True,blank=True,on_delete=models.CASCADE)
    max_ph_threshold = models.DecimalField(default=9.0,max_digits=5,decimal_places=2)
    min_ph_threshold = models.DecimalField(default=6.2,max_digits=5,decimal_places=2)
    max_tds_threshold = models.DecimalField(default=300,max_digits=5,decimal_places=2)
    min_tds_threshold = models.DecimalField(default=40.0,max_digits=5,decimal_places=2)
    max_temperature_threshold = models.DecimalField(default=38.0,max_digits=5,decimal_places=2)
    min_temperature_threshold = models.DecimalField(default=15.0,max_digits=5,decimal_places=2)
    max_ammonia_threshold = models.DecimalField(default=2.5,max_digits=5,decimal_places=2)
    min_ammonia_threshold = models.DecimalField(default=0.0,max_digits=5,decimal_places=2)
    max_do_threshold = models.DecimalField(default=0.0,max_digits=5,decimal_places=2)
    min_do_threshold = models.DecimalField(default=0.0,max_digits=5,decimal_places=2)
    max_alkinity_threshold = models.DecimalField(default=0,max_digits=5,decimal_places=2)
    min_alkinity_threshold = models.DecimalField(default=0,max_digits=5,decimal_places=2)
    max_hardness_threshold = models.DecimalField(default=0,max_digits=5,decimal_places=2)
    min_hardness_threshold = models.DecimalField(default=0,max_digits=5,decimal_places=2)
    max_good_ph_threshold = models.DecimalField(default=8.5,max_digits=5,decimal_places=2)
    max_good_tds_threshold = models.DecimalField(default=400,max_digits=5,decimal_places=2)
    max_good_temperature_threshold = models.DecimalField(default=0,max_digits=5,decimal_places=2)
    max_good_ammonia_threshold = models.DecimalField(default=1.5,max_digits=5,decimal_places=2)
    max_good_do_threshold = models.DecimalField(default=0,max_digits=5,decimal_places=2)
    max_good_alkinity_threshold = models.DecimalField(default=0,max_digits=5,decimal_places=2)
    max_good_hardness_threshold = models.DecimalField(default=0,max_digits=5,decimal_places=2)
    good_ph_threshold = models.DecimalField(default=8.0,max_digits=5,decimal_places=2)
    good_tds_threshold = models.DecimalField(default=240,max_digits=5,decimal_places=2)
    good_temperature_threshold = models.DecimalField(default=0,max_digits=5,decimal_places=2)
    good_ammonia_threshold = models.DecimalField(default=0,max_digits=5,decimal_places=2)
    good_do_threshold = models.DecimalField(default=5,max_digits=5,decimal_places=2)
    good_alkinity_threshold = models.DecimalField(default=0,max_digits=5,decimal_places=2)
    good_hardness_threshold = models.DecimalField(default=0,max_digits=5,decimal_places=2)
    min_good_ph_threshold = models.DecimalField(default=6.5,max_digits=5,decimal_places=2)
    min_good_tds_threshold = models.DecimalField(default=40,max_digits=5,decimal_places=2)
    min_good_temperature_threshold = models.DecimalField(default=0,max_digits=5,decimal_places=2)
    min_good_ammonia_threshold = models.DecimalField(default=0.15,max_digits=5,decimal_places=2)
    min_good_do_threshold = models.DecimalField(default=0,max_digits=5,decimal_places=2)
    min_good_alkinity_threshold = models.DecimalField(default=0,max_digits=5,decimal_places=2)
    min_good_hardness_threshold = models.DecimalField(default=0,max_digits=5,decimal_places=2)

    def __str__(self):
        return self.thresh_device.dev_name