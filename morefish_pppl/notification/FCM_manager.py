from pyfcm import FCMNotification

from users.models import APIKey

def sendPush(notification_title,datapayload,devicetoken):
    api_key = APIKey.objects.get(key_type=3).key_value
    body = datapayload
    title = notification_title
    
    push_service = FCMNotification(api_key=api_key)

    print("TOKEN",devicetoken)
    
    registration_id = devicetoken
    result = push_service.notify_single_device(registration_id=registration_id,message_body=body,message_title=title)

    print("RESULT",result)
