import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('email_service.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Log environment variables (except sensitive ones)
logger.info("Email service initialized")
logger.info(f"SENDER_EMAIL: {'set' if os.getenv('SENDER_EMAIL') else 'not set'}")
logger.info(f"APP_PASSWORD: {'set' if os.getenv('APP_PASSWORD') else 'not set'}")

def send_email(recipient, subject, body, sender_email=None, app_password=None, is_html=False, 
              image_paths=None, image_cids=None):
    """
    Send an email using SMTP (Gmail by default) with optional image attachments
    
    Args:
        recipient (str): Email address of the recipient
        subject (str): Email subject
        body (str): Email body (can be plain text or HTML)
        sender_email (str, optional): Sender's email. Defaults to SENDER_EMAIL from .env
        app_password (str, optional): App password. Defaults to APP_PASSWORD from .env
        is_html (bool, optional): Whether the body is HTML. Defaults to False.
        image_paths (list, optional): List of image file paths to attach. Defaults to None.
        image_cids (list, optional): List of content IDs for embedding images in HTML. 
                                   Should match the order of image_paths. Defaults to None.
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Use provided credentials or fall back to .env
        sender = sender_email or os.getenv("SENDER_EMAIL")
        password = app_password or os.getenv("APP_PASSWORD")
        
        logger.info(f"Attempting to send email to: {recipient}")
        logger.info(f"Using sender: {sender}")
        
        if not sender or not password:
            error_msg = "Email credentials not configured. Please check your .env file."
            logger.error(error_msg)
            st.error(error_msg)
            return False
            
        # Create the root message and fill in the from, to, and subject headers
        msg = MIMEMultipart('related')
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.preamble = 'This is a multi-part message in MIME format.'

        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.
        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)
        
        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText('Please use an HTML compatible email viewer to see this message.', 'plain')
        part2 = MIMEText(body, 'html' if is_html else 'plain')
        
        msg_alternative.attach(part1)
        msg_alternative.attach(part2)
        
        # Attach images if provided
        if image_paths and image_cids:
            for img_path, cid in zip(image_paths, image_cids):
                try:
                    with open(img_path, 'rb') as img_file:
                        img_data = img_file.read()
                    
                    # Guess the content type based on the file's extension
                    import mimetypes
                    content_type, _ = mimetypes.guess_type(img_path)
                    if content_type is None or content_type.split('/')[0] != 'image':
                        content_type = 'application/octet-stream'  # Fallback
                    
                    maintype, subtype = content_type.split('/', 1)
                    
                    # Create the attachment with the image data
                    img = MIMEBase(maintype, subtype)
                    img.set_payload(img_data)
                    
                    # Encode the payload using Base64
                    from email import encoders
                    encoders.encode_base64(img)
                    
                    # Set the filename parameter and Content-ID header
                    img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(img_path))
                    img.add_header('Content-ID', f'<{cid}>')
                    img.add_header('X-Attachment-Id', cid)
                    
                    msg.attach(img)
                    logger.info(f"Attached image: {img_path} with CID: {cid}")
                    
                except Exception as e:
                    logger.error(f"Error attaching image {img_path}: {str(e)}")
                    continue
        
        # Connect to server and send email
        logger.info("Connecting to SMTP server...")
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as server:
            logger.info("SMTP connection established")
            server.ehlo()
            logger.info("EHLO successful")
            
            logger.info("Starting TLS...")
            server.starttls()
            logger.info("TLS started")
            
            logger.info("Attempting to login...")
            server.login(sender, password)
            logger.info("Login successful")
            
            logger.info("Sending email...")
            server.send_message(msg)
            logger.info("Email sent successfully")
            
            server.quit()
            logger.info(f"Email successfully sent to {recipient}")
            st.success(f"✅ Email sent successfully to {recipient}")
            return True
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"SMTP Authentication Error: {str(e)}. Please check your email credentials and ensure you're using an App Password if 2FA is enabled."
        logger.error(error_msg)
        st.error(error_msg)
        return False
    except smtplib.SMTPException as e:
        error_msg = f"SMTP Error: {str(e)}"
        logger.error(error_msg)
        st.error(f"Failed to send email: {str(e)}")
        return False
    except socket.timeout as e:
        error_msg = "Connection to SMTP server timed out. Please check your internet connection."
        logger.error(error_msg)
        st.error(error_msg)
        return False
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        st.error(f"An unexpected error occurred: {str(e)}")
        return False

def send_bulk_email(recipients_df, subject, body, progress_callback=None):
    """
    Send bulk emails to a list of recipients
    
    Args:
        recipients_df (DataFrame): DataFrame containing subscriber emails and info
        subject (str): Email subject
        body (str): Email body (can include {name} for personalization)
        progress_callback (function, optional): Callback for progress updates
        
    Returns:
        tuple: (success_count, error_count)
    """
    if recipients_df.empty:
        return 0, 0
        
    success_count = 0
    error_count = 0
    total = len(recipients_df)
    
    for i, (_, row) in enumerate(recipients_df.iterrows()):
        try:
            # Personalize the email if {name} is in the body
            personalized_body = body
            if '{name}' in body and 'name' in row and pd.notna(row['name']):
                first_name = row['name'].split(' ')[0]
                personalized_body = body.replace('{name}', first_name)
            
            # Send the email
            if send_email(
                recipient=row['email'],
                subject=subject,
                body=personalized_body
            ):
                success_count += 1
                
                # Update progress
                if progress_callback:
                    progress = (i + 1) / total
                    progress_callback(progress, i+1, total, success_count, error_count)
                
                # Small delay to avoid hitting rate limits
                time.sleep(0.5)
                
        except Exception as e:
            error_count += 1
            st.error(f"Error sending to {row.get('email', 'unknown')}: {str(e)}")
    
    return success_count, error_count
