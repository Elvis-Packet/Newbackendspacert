import os
from sib_api_v3_sdk import ApiClient, Configuration, TransactionalEmailsApi
from sib_api_v3_sdk.models import SendSmtpEmail, SendSmtpEmailTo
from flask import current_app
import jwt
from datetime import datetime, timedelta

def get_email_client():
    configuration = Configuration()
    configuration.api_key['api-key'] = current_app.config['SENDINBLUE_API_KEY']
    api_client = ApiClient(configuration)
    return TransactionalEmailsApi(api_client)

def generate_verification_token(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

def send_verification_email(user):
    try:
        api_instance = get_email_client()
        
        # Generate verification token
        token = generate_verification_token(user)
        verification_url = f"{current_app.config['FRONTEND_URL']}/verify-email/{token}"
        
        # Create email content
        to = [SendSmtpEmailTo(email=user.email, name=f"{user.first_name} {user.last_name}")]
        email = SendSmtpEmail(
            to=to,
            subject="Verify your Spacer account",
            html_content=f"""
            <h1>Welcome to Spacer!</h1>
            <p>Hi {user.first_name},</p>
            <p>Thank you for registering with Spacer. Please click the link below to verify your email address:</p>
            <p><a href="{verification_url}">Verify Email</a></p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't create an account, you can safely ignore this email.</p>
            """
        )
        
        # Send email
        api_instance.send_transac_email(email)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send verification email: {str(e)}")
        return False

def send_booking_confirmation_email(booking):
    try:
        api_instance = get_email_client()
        user = booking.user
        space = booking.space
        
        to = [SendSmtpEmailTo(email=user.email, name=f"{user.first_name} {user.last_name}")]
        email = SendSmtpEmail(
            to=to,
            subject="Booking Confirmation - Spacer",
            html_content=f"""
            <h1>Booking Confirmation</h1>
            <p>Hi {user.first_name},</p>
            <p>Your booking for {space.name} has been confirmed.</p>
            <p>Details:</p>
            <ul>
                <li>Space: {space.name}</li>
                <li>Date: {booking.start_time.strftime('%Y-%m-%d')}</li>
                <li>Time: {booking.start_time.strftime('%H:%M')} - {booking.end_time.strftime('%H:%M')}</li>
                <li>Total: ${booking.total_price}</li>
            </ul>
            <p>Thank you for using Spacer!</p>
            """
        )
        
        api_instance.send_transac_email(email)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send booking confirmation email: {str(e)}")
        return False

def send_invoice_email(user, booking, invoice_number, payment_method):
    """
    Send invoice email to user
    
    Args:
        user (User): User object
        booking (Booking): Booking object
        invoice_number (str): Invoice number
        payment_method (str): Payment method used
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        api_instance = get_email_client()
        space = booking.space
        
        payment_method_display = {
            'card': 'Credit/Debit Card',
            'mpesa': 'M-Pesa',
            'cash': 'Cash on Arrival'
        }.get(payment_method, payment_method)
        
        # Format dates for display
        start_date = booking.start_time.strftime('%B %d, %Y %I:%M %p')
        end_date = booking.end_time.strftime('%B %d, %Y %I:%M %p')
        
        # Calculate duration in hours
        duration_hours = round((booking.end_time - booking.start_time).total_seconds() / 3600)
        
        to = [SendSmtpEmailTo(email=user.email, name=f"{user.first_name} {user.last_name}")]
        email = SendSmtpEmail(
            to=to,
            subject=f"Invoice #{invoice_number} - Spacer Booking",
            html_content=f"""
            <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
                <div style="display: flex; justify-content: space-between; padding-bottom: 20px; border-bottom: 1px solid #ddd;">
                    <div>
                        <h2 style="color: #4a90e2; margin: 0 0 5px;">Space Rental</h2>
                        <p style="margin: 3px 0;">123 Main Street</p>
                        <p style="margin: 3px 0;">Nairobi, Kenya</p>
                        <p style="margin: 3px 0;">Email: info@spacerental.com</p>
                        <p style="margin: 3px 0;">Phone: +254 712 345 678</p>
                    </div>
                    <div style="text-align: right;">
                        <h2 style="color: #4a90e2; margin: 0 0 5px;">INVOICE</h2>
                        <p style="margin: 3px 0; font-size: 18px;"><strong>Invoice #:</strong> {invoice_number}</p>
                        <p style="margin: 3px 0; color: #666;"><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
                        <p style="margin: 3px 0;"><strong>Status:</strong> Paid</p>
                    </div>
                </div>
                
                <div style="margin: 20px 0;">
                    <h3 style="color: #4a90e2; margin: 0 0 10px;">Billed To:</h3>
                    <p style="margin: 3px 0;">{user.first_name} {user.last_name}</p>
                    <p style="margin: 3px 0;">Email: {user.email}</p>
                    <p style="margin: 3px 0;">Phone: {booking.phone_number or 'N/A'}</p>
                </div>
                
                <div style="margin: 20px 0;">
                    <h3 style="color: #4a90e2; margin: 0 0 10px;">Booking Information:</h3>
                    <p style="margin: 3px 0;"><strong>Space:</strong> {space.name}</p>
                    <p style="margin: 3px 0;"><strong>Booking ID:</strong> {booking.id}</p>
                    <p style="margin: 3px 0;"><strong>From:</strong> {start_date}</p>
                    <p style="margin: 3px 0;"><strong>To:</strong> {end_date}</p>
                    <p style="margin: 3px 0;"><strong>Payment Method:</strong> {payment_method_display}</p>
                </div>
                
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr>
                            <th style="padding: 12px 15px; background-color: #f8f9fa; border-bottom: 1px solid #ddd; text-align: left;">Description</th>
                            <th style="padding: 12px 15px; background-color: #f8f9fa; border-bottom: 1px solid #ddd; text-align: left;">Rate</th>
                            <th style="padding: 12px 15px; background-color: #f8f9fa; border-bottom: 1px solid #ddd; text-align: left;">Duration</th>
                            <th style="padding: 12px 15px; background-color: #f8f9fa; border-bottom: 1px solid #ddd; text-align: left;">Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="padding: 12px 15px; border-bottom: 1px solid #ddd;">{space.name} Rental</td>
                            <td style="padding: 12px 15px; border-bottom: 1px solid #ddd;">${space.hourly_rate}/hr</td>
                            <td style="padding: 12px 15px; border-bottom: 1px solid #ddd;">{duration_hours} hours</td>
                            <td style="padding: 12px 15px; border-bottom: 1px solid #ddd;">${booking.total_price}</td>
                        </tr>
                        <tr>
                            <td colspan="3" style="padding: 12px 15px; font-weight: 700; font-size: 16px; border-top: 2px solid #4a90e2;">Total</td>
                            <td style="padding: 12px 15px; font-weight: 700; font-size: 16px; color: #28a745; border-top: 2px solid #4a90e2;">${booking.total_price}</td>
                        </tr>
                    </tbody>
                </table>
                
                <div style="color: #666; font-size: 14px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                    <p><strong>Note:</strong> This is an electronic invoice generated after successful payment.</p>
                    <p>For any inquiries, please contact our support team at support@spacerental.com</p>
                </div>
                
                <div style="margin-top: 30px; text-align: center; font-size: 14px; color: #666;">
                    <p>Thank you for your business!</p>
                </div>
            </div>
            """
        )
        
        api_instance.send_transac_email(email)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send invoice email: {str(e)}")
        return False 