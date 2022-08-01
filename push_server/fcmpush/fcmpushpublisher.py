import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
import os

base_dir = os.path.abspath(os.path.dirname(__file__))
cred_path = os.path.join(base_dir, "serviceAccountKey.json")
# cred_path = 'C:\\Users\\ghkdt\\Desktop\\Soonyoung\\StockBalance\\merlot_kube_extra\\push_server\\fcmpush\\serviceAccountKey.json'
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)


def send_fcm_push(fcm_token, title, body):
    # See documentation on defining a message payload.
    # if fcm_token is empty string, return None
    if fcm_token == '':
        return None

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=fcm_token,
    )

    response = messaging.send(message)
    # Response is a message ID string.
    # print('Successfully sent message:', response)


if __name__ == '__main__':
    from datetime import datetime
    send_fcm_push(fcm_token='enGej7H-RZeLUR02-X0A7P:APA91bGxBdx8T90P5ew7hn3pyuPqb9U4xw0tffctFi3ERrwxkMeBraQUbcjMY61QFOfQqC3mIut4jr8nky7BdOe83JNc_1PEUmRP6wUqc-3ZvHhqj-ug0rLcffWv-HeZHfAlzJ6Ig8iq',
                  title='테스트 메시지',
                  body=f'현재 시간은 {datetime.now().strftime("%H:%M:%S")} 입니다.')

    send_fcm_push(fcm_token='eDnikSqaSQSTYNX8SlU4wM:APA91bFLwMeY4Zir7KO-kl05qEmNO-pMS2BewnH_av-kv8FYFF-9N3omPMMRRucRulZ9sFZFslYQXEwE69HOn9HjNrTMUxF9dMw7GjTk5qC2sSW6eDoUN_5Nv7dzMpkpY-Ui8QRszeHK',
                  title='테스트',
                  body=f'현재 시간은 {datetime.now().strftime("%H:%M:%S")} 입니다.')
send_fcm_push(fcm_token='', title= 's', body='f')