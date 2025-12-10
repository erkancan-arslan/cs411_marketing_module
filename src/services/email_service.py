"""
Email Service with Strategy Pattern Implementation
Provides flexible email sending mechanisms through interchangeable strategies.
"""
from abc import ABC, abstractmethod
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os


class IEmailProvider(ABC):
    """
    Abstract Base Class for Email Provider Strategy Pattern.
    
    This interface defines the contract that all email sending strategies must follow.
    Implementing classes can provide different behaviors (Mock, SMTP, etc.) while
    maintaining a consistent interface for the client code.
    
    This is the STRATEGY PATTERN interface.
    """
    
    @abstractmethod
    def send(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send an email to the specified recipient.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Email body content (can be plain text or HTML)
        
        Returns:
            True if email was sent successfully, False otherwise
        """
        pass


class MockEmailProvider(IEmailProvider):
    """
    Mock Email Provider - STRATEGY PATTERN Concrete Implementation #1
    
    Simulates email sending without actually sending emails.
    Used for testing and bulk campaign simulations where we don't want
    to send real emails but need to verify the logic.
    
    This is perfect for:
    - Development and testing
    - Bulk campaign simulations
    - Demonstrations without email infrastructure
    """
    
    def send(self, to_email: str, subject: str, body: str) -> bool:
        """
        Simulate sending an email by logging to console.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Email body content
        
        Returns:
            Always returns True (simulated success)
        """
        print(f"📧 [MOCK] Sending email to: {to_email}")
        print(f"   Subject: {subject}")
        print(f"   Body Preview: {body[:50]}...")
        return True


class SmtpEmailProvider(IEmailProvider):
    """
    SMTP Email Provider - STRATEGY PATTERN Concrete Implementation #2
    
    Sends real emails using SMTP protocol.
    Supports common email providers (Gmail, Outlook, Yahoo, etc.)
    
    Configuration via environment variables:
    - SMTP_HOST: SMTP server hostname (e.g., smtp.gmail.com)
    - SMTP_PORT: SMTP server port (e.g., 587 for TLS)
    - SMTP_USER: Email account username
    - SMTP_PASSWORD: Email account password or app-specific password
    
    Note: For Gmail, you may need to use an "App Password" instead of
    your regular password. Enable 2FA and generate an app password.
    """
    
    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None
    ):
        """
        Initialize SMTP provider with configuration.
        
        Args:
            smtp_host: SMTP server hostname (falls back to env var)
            smtp_port: SMTP server port (falls back to env var)
            smtp_user: SMTP username (falls back to env var)
            smtp_password: SMTP password (falls back to env var)
        """
        self.smtp_host = smtp_host or os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = smtp_user or os.getenv('SMTP_USER', '')
        self.smtp_password = smtp_password or os.getenv('SMTP_PASSWORD', '')
        
        if not self.smtp_user or not self.smtp_password:
            print("⚠️  Warning: SMTP credentials not configured. Email sending will fail.")
    
    def send(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send a real email via SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Email body content (HTML supported)
        
        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['From'] = self.smtp_user
            message['To'] = to_email
            message['Subject'] = subject
            
            # Attach body (support both plain text and HTML)
            html_part = MIMEText(body, 'html')
            message.attach(html_part)
            
            # Connect to SMTP server and send
            print(f"📨 [SMTP] Connecting to {self.smtp_host}:{self.smtp_port}...")
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
            
            print(f"✅ [SMTP] Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print(f"❌ [SMTP] Authentication failed. Check credentials.")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ [SMTP] Failed to send email: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ [SMTP] Unexpected error: {str(e)}")
            return False


class EmailServiceFactory:
    """
    Factory class to create the appropriate email provider based on configuration.
    
    This simplifies the selection of email strategies and centralizes
    the decision logic in one place.
    """
    
    @staticmethod
    def create_provider(use_real_email: bool = False) -> IEmailProvider:
        """
        Create and return the appropriate email provider.
        
        Args:
            use_real_email: If True, returns SmtpEmailProvider; otherwise MockEmailProvider
        
        Returns:
            An instance of IEmailProvider (either Mock or SMTP)
        """
        if use_real_email:
            print("🔧 Using SMTP Email Provider (Real Emails)")
            return SmtpEmailProvider()
        else:
            print("🔧 Using Mock Email Provider (Simulation Mode)")
            return MockEmailProvider()
