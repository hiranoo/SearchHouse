#pylint --disable=F0401
from gmail_api_helpers import *

def send_email(subject, message_text, filepath):
    service = authorize()
    
    sender = "automf03@gmail.com"
    to = "trivalworks@gmail.com"
    message = create_message_with_attachment(sender, to, subject, message_text, filepath)
    send_message(service=service, user_id='me', message=message)




if __name__ == '__main__':
    service = authorize()

    sender = "automf03@gmail.com"
    to = "trivalworks@gmail.com"
    subject = "gmail api test attatchment"
    message_text = "This is the first trial of using gmail-api with an attatchment!"
    filepath = "hello.csv"
    message = create_message_with_attachment(sender, to, subject, message_text, filepath)
    send_message(service=service, user_id='me', message=message)

