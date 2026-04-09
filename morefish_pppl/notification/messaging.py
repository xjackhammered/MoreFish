"""Server Side FCM sample.

Firebase Cloud Messaging (FCM) can be used to send messages to clients on iOS,
Android and Web.

This sample uses FCM to send two types of messages to clients that are subscribed
to the `news` topic. One type of message is a simple notification message (display message).
The other is a notification message (display notification) with platform specific
customizations. For example, a badge is added to messages that are sent to iOS devices.
"""

import argparse
import json
import requests
import google.auth.transport.requests

from google.oauth2 import service_account

PROJECT_ID = 'morefishv2'
BASE_URL = 'https://fcm.googleapis.com'
FCM_ENDPOINT = 'v1/projects/' + PROJECT_ID + '/messages:send'
FCM_URL = BASE_URL + '/' + FCM_ENDPOINT
SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

# [START retrieve_access_token]
def _get_access_token():
  """Retrieve a valid access token that can be used to authorize requests.

  :return: Access token.
  """
  credentials = service_account.Credentials.from_service_account_file(
    'server_key.json', scopes=SCOPES)
  request = google.auth.transport.requests.Request()
  credentials.refresh(request)
  return credentials.token
# [END retrieve_access_token]

def _send_fcm_message(fcm_message):
  """Send HTTP request to FCM with given message.

  Args:
    fcm_message: JSON object that will make up the body of the request.
  """
  # [START use_access_token]
  headers = {
    'Authorization': 'Bearer ' + _get_access_token(),
    'Content-Type': 'application/json; UTF-8',
  }
  # [END use_access_token]
  resp = requests.post(FCM_URL, data=json.dumps(fcm_message), headers=headers)

  if resp.status_code == 200:
    print('Message sent to Firebase for delivery, response:')
    print(resp.text)
  else:
    print('Unable to send message to Firebase')
    print(resp.text)

def _build_common_message():
  """Construct common notifiation message.

  Construct a JSON object that will be used to define the
  common parts of a notification message that will be sent
  to any app instance subscribed to the news topic.
  """
  return {
    'message': {
      # 'token': "e12LKEyYR8iOcXIS1eXcnm:APA91bHrwwM3s4mLeS22L3Xc33_6506wImS0gOtxEo5dKL6uQf42xpNn0nqkE098os__I7WhFlk1cmQEoU-5z4d7UlhiHKLv5nEMBihFbg0lARIqvGIVhGGSY01Del_QU5lXf0dARydU",
      'token': "c_cWbQEXQwu1EksMcpLlRW:APA91bFbfTiztSZ8vqM19U_YXNwa_qC6ZhYZrhcS1MHXaYaRNTbX7Y-NRKVJaM5Hw5k_sVKH-raRkjMYyfqGxLyQJNhPMii-jvw8e2mYlaBqQ1Bn6_cD2l3SSpy8KS0kgacAd17aWhFy",
      # 'topic': 'news',
      # 'notification': {
      #   'title': 'iguard Test Title',
      #   'body': 'Test Notification iguard'
      # },
      'data': {
        'title': 'Test Title',
        'message': 'Test Notification'
      }
    }
  }

def _build_override_message():
  """Construct common notification message with overrides.

  Constructs a JSON object that will be used to customize
  the messages that are sent to iOS and Android devices.
  """
  fcm_message = _build_common_message()

  apns_override = {
    'payload': {
      'aps': {
        'badge': 1
      }
    },
    'headers': {
      'apns-priority': '10'
    }
  }

  android_override = {
    'notification': {
      'click_action': 'android.intent.action.MAIN'
    }
  }

  fcm_message['message']['android'] = android_override
  fcm_message['message']['apns'] = apns_override

  return fcm_message

def fcm_by_ron(token, title, push_notification_text):

  headers = {
    'Authorization': 'Bearer ' + _get_access_token(),
    'Content-Type': 'application/json; UTF-8',
  }

  fcm_message = {
    'message': {
      # 'token': "dcTsO5xCTtSi94qD2Nu19s:APA91bF8j7ZreTgh-wxfdHake06fHKRSgt6n1obHVRaVtBq0U3zWwKGkhnXja5SwrNA70LMEqHijuj-6Ixf2uKKs8PLD5wdFPx0CtJIGD4YZsPx_q6EC00FvwpVET3kTFcWlIedzHqW2",
      # 'topic': 'news',
      'token': token,
      # 'notification': {
      #   'title': title,
      #   'body': push_notification_text
      # },
      'data': {
        'title': title,
        'message': push_notification_text
      }
    }
  }
  # [END use_access_token]
  resp = requests.post(FCM_URL, data=json.dumps(fcm_message), headers=headers)

  if resp.status_code == 200:
    pass
    # print('Message sent to Firebase for delivery, response:')
    # print(resp.text)
  else:
    pass
    # print('Unable to send message to Firebase')
    # print(resp.text)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--message')
  args = parser.parse_args()
  if args.message and args.message == 'common-message':
    common_message = _build_common_message()
    print('FCM request body for message using common notification object:')
    print(json.dumps(common_message, indent=2))
    _send_fcm_message(common_message)
  elif args.message and args.message == 'override-message':
    override_message = _build_override_message()
    print('FCM request body for override message:')
    print(json.dumps(override_message, indent=2))
    _send_fcm_message(override_message)
  elif args.message and args.message == 'ron':
    # token = 'c_cWbQEXQwu1EksMcpLlRW:APA91bFbfTiztSZ8vqM19U_YXNwa_qC6ZhYZrhcS1MHXaYaRNTbX7Y-NRKVJaM5Hw5k_sVKH-raRkjMYyfqGxLyQJNhPMii-jvw8e2mYlaBqQ1Bn6_cD2l3SSpy8KS0kgacAd17aWhFy'
    token = 'f8ONITKiR0mAZki1xKc1vi:APA91bGtmEVjEIk9aQN2WEltzgz7torxjhImnGUZtTPPfTtFjNXzoRYy4MF_wwGBSt5b0tWPWd3LxV2gbwFGkcqxyNa7MUjS9gfpsk77OSuWmVCN7fylo0-RbMlhDREGPKqiLjDpfowY'
    
    title = 'Ignore This!'
    push_notification_text = "Tashdid is Testing."
    fcm_by_ron(token, title, push_notification_text)
  else:
    print('''Invalid command. Please use one of the following commands:
python messaging.py --message=common-message
python messaging.py --message=override-message''')

if __name__ == '__main__':
  main()
