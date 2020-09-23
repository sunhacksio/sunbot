import boto3
from botocore.exceptions import ClientError
from flask import render_template

SENDER = "sunhacks team <team@sunhacks.io>"
AWS_REGION = "us-west-2"
CHARSET = "UTF-8"

def send_mail(recipient, subject, body_html, body_text):
    client = boto3.client('ses',region_name=AWS_REGION)
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=SENDER,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        return False
    else:
        print("[MAIL]: Sent email to {0} with ID {1}".format(recipient, response["MessageId"]))
        return True

def send_verification_email(user, code):
    html = render_template('mail/verification.html', name=user.first_name, code = code)
    text = "Thank you for registering for sunhacks! Your verification code is " + code
    return send_mail(user.email, "Discord Verification for sunhacks", html, text)
