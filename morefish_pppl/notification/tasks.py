import datetime
import traceback
# import traceback
from celery import Celery, shared_task
from django.db import DatabaseError
from pyfcm import FCMNotification
from pytz import timezone

from django.core.mail import send_mail
from assets.models import AssetsProperties
# from device.models import , current_date_time
from morefish_pppl import settings
from celery.utils.log import get_task_logger
# from new_mqtt import current_date_time
from django.db.models import Q

from notification.models import Configuration, NotificationThreshold, Notifications
from notification.FCM_manager import sendPush
from .messaging import fcm_by_ron
from users.models import FCM, User


def current_date_time():
    bd_timezone = timezone('Asia/Dhaka')
    bd_time = datetime.datetime.now(bd_timezone)
    time_stamp = bd_time.strftime('%Y-%m-%d %H:%M:%S')
    return time_stamp


logger = get_task_logger(__name__)

def create_new_conf_notification(code:str,devicedata):


    configuration = Configuration.objects.get(con_code = code)

    if configuration.con_todo == None:
        todo = ""
    else:
        todo = configuration.con_todo

    notification_time = current_date_time()
    notification_alert = configuration.con_urgency
    notification_pond = devicedata.dvd_dev.dev_asset.ast_name
    notification_msg = configuration.con_message_body
    notification_value_msg = configuration.con_warning_msg
    notification_value_msg_warning = configuration.con_warning
    notification_color = configuration.con_color
    issue_value=''
    
    if configuration.con_type == 'INVALID':
        issue_value = "sensor"
        notification_final = current_date_time() + " " + notification_alert + " " + devicedata.dvd_dev.dev_asset.ast_name + notification_msg + " " + notification_value_msg + " "
    
        notification_value= todo
    else:
        issue_value=str(devicedata.dvd_val)
        notification_final = current_date_time() + " " + notification_alert + " " + devicedata.dvd_dev.dev_asset.ast_name + notification_msg + " " + notification_value_msg + " " + \
                                        notification_value_msg_warning + " " + issue_value
        notification_value=issue_value
        
    # user_id = notification_dict['user_id']
    user_list = AssetsProperties.objects.prefetch_related("ast_user").get(id = devicedata.dvd_dev.dev_asset.id)

    users_with_domain = User.objects.filter(usr_email__icontains="@dma-bd.com",is_active=True).exclude(id__in=user_list.ast_user.all().values_list('id', flat=True))
    print("LINE 93", users_with_domain)
    today = datetime.datetime.today().date()
    # # print('LINE 117',user_list.ast_user.all())
    for user in user_list.ast_user.all():
        
        new_notif = Notifications.objects.create(not_final = notification_final, not_user_id = user.id,
                                                not_color=notification_color,not_message_body = notification_msg,
                                                not_time = notification_time, not_urgency = notification_alert,
                                                not_pond = notification_pond, not_warning = notification_value_msg_warning,
                                                not_value = notification_value, not_warning_msg = notification_value_msg,
                                                not_date = today,dev_id = devicedata.dvd_dev.id,conf_id = configuration.id,
                                                not_sensor_id=devicedata.dvd_sen_id)
        try:
            user_fcm = FCM.objects.get(user_id = user.id).token
            print("FCM",user,user_fcm)
            # sendPush(notification_title=notification_alert,datapayload=notification_final,devicetoken=user_fcm)
            fcm_by_ron(user_fcm, notification_alert, notification_final)
        except Exception as e:
            logger.info("NOTIFICATION EXCEPTION")
            print("Cannot send notification")
    
    for user in users_with_domain:
        
        new_notif = Notifications.objects.create(not_final = notification_final, not_user_id = user.id,
                                                not_color=notification_color,not_message_body = notification_msg,
                                                not_time = notification_time, not_urgency = notification_alert,
                                                not_pond = notification_pond, not_warning = notification_value_msg_warning,
                                                not_value = notification_value, not_warning_msg = notification_value_msg,
                                                not_date = today,dev_id = devicedata.dvd_dev.id,conf_id = configuration.id)
        try:
            if user.company_id == user_list.company_id:
                user_fcm = FCM.objects.get(user_id = user.id).token
                print("FCM",user,user_fcm)
                # sendPush(notification_title=notification_alert,datapayload=notification_final,devicetoken=user_fcm)
                fcm_by_ron(user_fcm, notification_alert, notification_final)
        except Exception as e:
            logger.info("NOTIFICATION EXCEPTION")
            print("Cannot send notification")

@shared_task(queue='notification_queue')
def send_threshold_notification(device_data_id:int):
    from device.models import DeviceData
    from device.models import InvalidValue
    try:

        
        
        devicedata = DeviceData.objects.select_related("dvd_sen").get(id=device_data_id)
        
        
        notifications = Notifications.objects.select_related('conf').filter(dev_id = devicedata.dvd_dev.id,not_sensor_id=devicedata.dvd_sen_id)

        value_range = InvalidValue.objects.filter(sensor_id = devicedata.dvd_sen).first()
        codes = Configuration.objects.filter(con_sensor_id = devicedata.dvd_sen_id)
        
        if float(devicedata.dvd_val)>devicedata.dvd_sen.sensor_max:
            code = codes.filter(con_type=Configuration.TypeChoices.MAX).first()

        if float(devicedata.dvd_val)<devicedata.dvd_sen.sensor_min:
            code = codes.filter(con_type=Configuration.TypeChoices.MIN).first()

        if devicedata.dvd_sen.sensor_min<float(devicedata.dvd_val)<devicedata.dvd_sen.sensor_max:
            code = codes.filter(con_type=Configuration.TypeChoices.GOOD).first()

        if not value_range.min_invalid_value<float(devicedata.dvd_val)<value_range.max_invalid_value:
            code = codes.filter(con_type=Configuration.TypeChoices.INVALID).first()    

        
        print("CODE WARNING -------->", code.con_warning_msg)
        notification = notifications.filter(not_warning_msg = code.con_warning_msg).last()
        print("NOTIFICATION -------->", notification)
        if not notification:
                print("NO NOTIFICATION FOUND -------------->")
                create_new_conf_notification(code=code.con_code,devicedata=devicedata)
        elif notification.conf != None:
            
            if notification.conf.con_code != str(code.con_code): 
                print("Different Notification ------------------->")
                create_new_conf_notification(code=code.con_code,devicedata=devicedata)
        else:
            create_new_conf_notification(code=code.con_code,devicedata=devicedata)
        
        

            
    except Exception as e:
        traceback.print_exc()
        # return False
        # logger.error(str(e))
        logger.info("Notification error: %s", str(e))