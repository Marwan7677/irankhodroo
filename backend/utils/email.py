"""
Email Service - ارسال ایمیل‌های مختلف
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings
from typing import List

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.sender_email = settings.SENDER_EMAIL
        self.sender_password = settings.SENDER_PASSWORD
        self.sender_name = settings.SENDER_NAME
    
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        Send email with HTML content
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = to_email
            
            part = MIMEText(html_content, 'html')
            msg.attach(part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_order_confirmation(self, to_email: str, order_number: str, order_total: float) -> bool:
        """
        Send order confirmation email
        """
        subject = f"تأیید سفارش #{order_number} - فروشگاه ایران خودرو"
        html_content = f"""
        <html dir="rtl">
            <body style="font-family: 'Vazirmatn', Arial;">
                <h2>سلام!</h2>
                <p>سفارش شما با موفقیت ثبت شد.</p>
                <p><strong>شماره سفارش:</strong> {order_number}</p>
                <p><strong>مبلغ کل:</strong> {order_total:,.0f} تومان</p>
                <p>شما می‌توانید وضعیت سفارش خود را در پیوند زیر پیگیری کنید:</p>
                <a href="https://ikcostore.com/orders/{order_number}">مشاهده سفارش</a>
                <p>با تشکر,<br>تیم ایران خودرو</p>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, html_content)
    
    def send_password_reset(self, to_email: str, reset_token: str) -> bool:
        """
        Send password reset email
        """
        subject = "بازنشانی رمز عبور - فروشگاه ایران خودرو"
        html_content = f"""
        <html dir="rtl">
            <body style="font-family: 'Vazirmatn', Arial;">
                <h2>بازنشانی رمز عبور</h2>
                <p>برای بازنشانی رمز عبور خود روی لینک زیر کلیک کنید:</p>
                <a href="https://ikcostore.com/reset-password?token={reset_token}">بازنشانی رمز عبور</a>
                <p>اگر این درخواست از سوی شما نیست، این ایمیل را نادیده بگیرید.</p>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, html_content)

email_service = EmailService()

def send_email(to_email: str, subject: str, html_content: str) -> bool:
    return email_service.send_email(to_email, subject, html_content)

def send_order_confirmation(to_email: str, order_number: str, order_total: float) -> bool:
    return email_service.send_order_confirmation(to_email, order_number, order_total)
