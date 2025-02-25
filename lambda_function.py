import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from twilio.rest import Client

def send_email(group):
    # Fetch email credentials from environment variables
    sender_email = os.environ['EMAIL_USER']
    sender_password = os.environ['EMAIL_PASSWORD']

    subject = f"Weekly Church Cleaning Reminder for {group['GroupName']}"
    body = (
        f"Hello {group['GroupName']},\n\n"
        "This is your automated reminder to clean the church building this week.\n\n"
        "Please contact your team leader for more information. Thank you!\n\n"
        "Elizabeth River Ward Bishopric"
    )

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ', '.join(group['Emails'])
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, group['Emails'], msg.as_string())
        server.quit()
        print(f"Email sent to {group['GroupName']}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_sms(group):
    # Fetch Twilio credentials from environment variables
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    twilio_phone = os.environ['TWILIO_PHONE_NUMBER']

    client = Client(account_sid, auth_token)

    # SMS message content
    sms_body = f"This is an automated message from the Elizabeth River Ward Bishopric. Reminder: {group['GroupName']}, it is your turn clean the church this week. Thank you!😊"

    # Check if the group has a list of phone numbers
    if 'PhoneNumbers' in group and group['PhoneNumbers']:
        for number in group['PhoneNumbers']:
            try:
                message = client.messages.create(
                    body=sms_body,
                    from_=twilio_phone,
                    to=number
                )
                print(f"SMS sent to {number}: {message.sid}")
            except Exception as e:
                print(f"Failed to send SMS to {number}: {e}")
    else:
        print(f"No phone numbers provided for {group['GroupName']}.")

# Main Lambda handler
def lambda_handler(event, context):
    groups = [
        {
            'GroupName': 'Group1',
            'Emails': [
                'example@gexample.com', 'example2@example.com'
            ],
            'PhoneNumbers': [
                '+15551234567', '+15551234568'
            ]
        },
        {
            'GroupName': 'Group2',
            'Emails': [
                'example3@gexample.com', 'example4@example.com'
            ],
            'PhoneNumbers': [
                '+15551234569', '+15551234560'
            ]
        }
    ]

    # Rotate between the groups weekly based on the ISO week number
    week_number = datetime.now().isocalendar()[1]
    group_index = (week_number - 1) % len(groups)
    current_group = groups[group_index]

    # Send email and SMS reminders to the selected group
    send_email(current_group)
    send_sms(current_group)

if __name__ == '__main__':
    # For local testing, simulate lambda_handler call
    lambda_handler({}, None)
