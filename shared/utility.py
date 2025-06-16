import threading


class PhoneThread(threading.Thread):
    def __init__(self, message):
        self.message = message
        threading.Thread.__init__(self)

    def run(self):
        print('run func: ', self.message)


class PhoneSender:
    @staticmethod
    def send_code(data):
        message = f"To: {data['to_phone']}\nCode: {data['body']}"
        PhoneThread(message).start()


def send_phone_code(phone_number, code):
    message_body = (f"--------------------------------------------------------------\n"
                    f"|            Sizning tasdiqlash kodingiz: >>> {code} <<<             |\n"
                    f"--------------------------------------------------------------------\n")
    PhoneSender.send_code(
        {
            'to_phone': phone_number,
            'body': message_body,
        }
    )


"""
Eskiz yoki Twilo

pip install requests

import requests

def send_sms(phone_number, code):
    token = 'your_eskiz_token'
    message = f"Ro'yxatdan o'tish kodi: {code}"

    response = requests.post(
        'https://notify.eskiz.uz/api/message/sms/send',
        headers={"Authorization": f"Bearer {token}"},
        data={
            "mobile_phone": phone_number,
            "message": message,
            "from": "4546",
            "callback_url": ""
        }
    )
    print(response.json())

"""
