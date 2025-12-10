"""
Flask Application Configuration
Centralized configuration for the Marketing Automation Module.
"""
import os
from datetime import timedelta


class Config:
    """Base configuration class."""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-cs411-marketing-module-2025')
    
    # Session Configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Application Settings
    APP_NAME = "CRM Marketing Automation"
    APP_VERSION = "1.0.0"
    
    # Data File Paths
    CUSTOMERS_DATA_FILE = 'data/customers.json'
    CAMPAIGNS_DATA_FILE = 'data/campaigns.json'
    
    # Email Configuration (for SMTP strategy)
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    
    # Debug Mode
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
