from dotenv import load_dotenv
import os
import csv
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
import pytz

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
SENDER_EMAIL = os.getenv("SENDER_EMAIL")    # Your Gmail address
APP_PASSWORD = os.getenv("APP_PASSWORD")     # Gmail App Password
SEND_TEST_EMAIL = False  # Set to True to send a test email to yourself
TEST_EMAIL = SENDER_EMAIL  # Email to send test message to

# Email templates
EMAIL_TEMPLATES = {
    'new_listing': {
        'subject': '🏡 New Property Alert: {property_name}',
        'body': """Hello {name},

We're excited to share a new property that matches your interests:

🏠 {property_name}
📍 {location}
💵 {price}
📏 {size}

{description}

View more details: {property_url}

Best regards,
WestProp Team"""
    },
    'price_drop': {
        'subject': '📉 Price Alert: {property_name}',
        'body': """Hello {name},

Great news! A property you might be interested in has had a price reduction:

🏠 {property_name}
📍 {location}
💵 Old Price: {old_price}
💥 New Price: {new_price} (Save {savings}%)

Don't miss this opportunity! View details: {property_url}

Best regards,
WestProp Team"""
    },
    'market_update': {
        'subject': '📈 WestProp Market Update: {month} {year}',
        'body': """Hello {name},

Here's your {frequency} market update from WestProp:

{content}

Best regards,
WestProp Team"""
    }
}

def should_send_alert(subscriber, alert_type):
    """Check if we should send an alert based on frequency and last sent"""
    if not subscriber.get('status') == 'Active':
        return False
        
    # Check if alert type matches subscriber's interests
    if 'interests' in subscriber and subscriber['interests'] != 'All':
        interests = subscriber['interests'].split(',')
        if alert_type not in interests:
            return False
    
    # Check frequency
    last_sent = subscriber.get('last_sent', '')
    if not last_sent:
        return True
        
    try:
        last_sent_date = datetime.strptime(last_sent, '%Y-%m-%dT%H:%M:%S')
        now = datetime.now(pytz.UTC)
        
        frequency = subscriber.get('frequency', 'Weekly').lower()
        
        if frequency == 'daily':
            return (now - last_sent_date) >= timedelta(days=1)
        elif frequency == 'weekly':
            return (now - last_sent_date) >= timedelta(weeks=1)
        elif frequency == 'monthly':
            return (now - last_sent_date) >= timedelta(days=30)
    except Exception as e:
        print(f"Error checking send time: {e}")
    
    return True

def update_last_sent(email):
    """Update the last_sent timestamp for a subscriber"""
    subscribers = []
    updated = False
    
    if not os.path.exists('email_alert_subscribers.csv'):
        return
    
    # Read existing subscribers
    with open('email_alert_subscribers.csv', 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        for row in reader:
            if row.get('email') == email:
                row['last_sent'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
                updated = True
            subscribers.append(row)
    
    # Write back if updated
    if updated and subscribers:
        with open('email_alert_subscribers.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(subscribers)

def send_email(recipient, subject, body):
    """Send an email using Gmail SMTP"""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient
    msg.set_content(body)
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            smtp.send_message(msg)
            print(f"Sent email to {recipient}")
            return True
    except Exception as e:
        print(f"Error sending email to {recipient}: {e}")
        return False

def main():
    # Check for required environment variables
    if not all([SENDER_EMAIL, APP_PASSWORD]):
        print("Error: Missing required environment variables. Check your .env file.")
        return
    
    # For testing: Send a test email
    if SEND_TEST_EMAIL and TEST_EMAIL:
        print("Sending test email...")
        test_subject = "✅ WestProp Alerts: Test Message"
        test_body = "This is a test email from the WestProp Alerts system.\n\nIf you received this, the email system is working correctly!"
        if send_email(TEST_EMAIL, test_subject, test_body):
            print("✅ Test email sent successfully!")
        else:
            print("❌ Failed to send test email")
        return
    
    # Read subscribers
    if not os.path.exists('email_alert_subscribers.csv'):
        print("No subscribers found.")
        return
    
    subscribers = []
    with open('email_alert_subscribers.csv', 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        subscribers = list(reader)
    
    if not subscribers:
        print("No active subscribers found.")
        return
    
    # Example: Send a new listing alert (in a real app, this would be dynamic)
    alert_type = 'new_listing'  # Could be 'price_drop', 'market_update', etc.
    
    # Example property data (in a real app, this would come from your database)
    property_data = {
        'property_name': 'New Luxury Apartments in Harare',
        'location': 'Borrowdale, Harare',
        'price': 'From $120,000',
        'size': '85-120 sqm',
        'description': 'Modern luxury apartments with smart home features, swimming pool, and 24/7 security.',
        'property_url': 'https://westprop.co.zw/properties/new-luxury-apartments'
    }
    
    # Process each subscriber
    sent_count = 0
    for sub in subscribers:
        if should_send_alert(sub, alert_type):
            # Personalize the email
            name = sub.get('email', '').split('@')[0].title()
            template = EMAIL_TEMPLATES[alert_type]
            
            subject = template['subject'].format(**property_data)
            body = template['body'].format(
                name=name,
                frequency=sub.get('frequency', 'weekly').lower(),
                **property_data
            )
            
            # Send the email
            if send_email(sub['email'], subject, body):
                update_last_sent(sub['email'])
                sent_count += 1
    
    print(f"Sent {sent_count} {alert_type.replace('_', ' ')} alerts.")

if __name__ == "__main__":
    main()