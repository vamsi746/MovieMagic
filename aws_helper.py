import boto3
from botocore.exceptions import ClientError

REGION_NAME = 'ap-south-1'  # Change to your AWS region if needed
USERS_TABLE = 'MovieMagic_Users'
BOOKINGS_TABLE = 'MovieMagic_Bookings'
SNS_TOPIC_ARN = 'arn:aws:sns:ap-south-1:xxxxxxxxxxxx:MovieMagic_Topic'

# Initialize clients (used only when AWS access is active)
dynamodb = boto3.resource('dynamodb', region_name=REGION_NAME)
sns = boto3.client('sns', region_name=REGION_NAME)

def store_user_aws(email, password):
    try:
        table = dynamodb.Table(USERS_TABLE)
        table.put_item(Item={
            'Email': email,
            'Password': password
        })
    except ClientError as e:
        print(f"Error storing user: {e}")

def get_user_aws(email):
    try:
        table = dynamodb.Table(USERS_TABLE)
        response = table.get_item(Key={'Email': email})
        return response.get('Item')
    except ClientError as e:
        print(f"Error fetching user: {e}")
        return None

def store_booking_aws(data):
    try:
        table = dynamodb.Table(BOOKINGS_TABLE)
        table.put_item(Item=data)
    except ClientError as e:
        print(f"Error storing booking: {e}")

def send_email_notification_aws(booking):
    try:
        message = (
            f"🎟️ Booking Confirmation\n"
            f"Booking ID: {booking['booking_id']}\n"
            f"Movie: {booking['movie']}\n"
            f"Theater: {booking['theater']}\n"
            f"Seat: {booking['seat']}\n"
            f"User: {booking['user']}"
        )
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject="MovieMagic Ticket Confirmed"
        )
        print("[AWS SNS] Email sent successfully.")
    except ClientError as e:
        print(f"Error sending SNS email: {e}")
