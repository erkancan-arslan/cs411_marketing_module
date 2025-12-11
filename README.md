# CRM Marketing Automation Module

A Flask-based marketing automation system demonstrating clean layered architecture principles for CS411 Software Architecture course. This project implements customer segmentation, campaign management, and analytics functionality using a service-oriented design pattern.

## Project Overview

This Marketing Automation Module is a web-based CRM system that enables businesses to segment customers, create targeted marketing campaigns, and analyze campaign performance. The project emphasizes software architecture best practices with strict separation of concerns across presentation, business, and data layers.

## Key Features

- **Customer Segmentation**: Dynamic customer grouping based on configurable criteria (age, location, interests, purchase history)
- **Campaign Management**: Create, schedule, and track marketing campaigns with targeted email delivery
- **Analytics Dashboard**: Real-time visualization of campaign performance metrics and customer engagement statistics
- **Email Simulation**: Strategy pattern implementation for both mock and SMTP-based email delivery
- **User Authentication**: Session-based login system for secure access

## Architecture

The project follows a strict **Layered Architecture** pattern with three distinct layers:

### 1. Presentation Layer (`src/web`)
- **Technology**: Flask, Jinja2, Bootstrap 5, Chart.js
- **Responsibility**: HTTP request handling, view rendering, user interface
- **Rule**: No business logic - delegates all operations to the Service Layer

### 2. Business Logic Layer (`src/services`)
- **Technology**: Pure Python
- **Responsibility**: Customer segmentation, campaign orchestration, analytics calculations
- **Rule**: Input/output are domain models only, no direct data access

### 3. Data Access Layer (`src/repository`)
- **Technology**: JSON file storage with Repository Pattern
- **Responsibility**: CRUD operations on data files
- **Rule**: Implementation details hidden from upper layers

## Design Patterns

### Repository Pattern
Located in `src/repository/`, this pattern decouples the application from the data source. The `JsonRepository` class provides a consistent interface for data operations, allowing easy migration to SQL databases in the future.

### Strategy Pattern
Implemented in `src/services/email_service.py` to provide flexible email delivery:
- **MockEmailSender**: Simulates email delivery for testing and bulk operations
- **SmtpEmailSender**: Real SMTP-based email delivery for production use

### Facade Pattern
Service layer methods provide simplified interfaces to complex subsystem interactions, particularly in analytics and segmentation operations.

## Technology Stack

- **Language**: Python 3.10+
- **Web Framework**: Flask 3.0.0
- **Frontend**: Bootstrap 5, Chart.js
- **Data Storage**: JSON files
- **Session Management**: Flask sessions with filesystem backend

## Project Structure

```
cs411_marketing_module/
├── config.py                 # Application configuration
├── run.py                    # Application entry point
├── start.py                  # Project structure generator
├── generate_data.py          # Mock data generation script
├── requirements.txt          # Python dependencies
├── data/                     # JSON data files
│   ├── customers.json
│   └── campaigns.json
├── src/
│   ├── core/                 # Core interfaces and abstractions
│   ├── models/               # Domain models (Customer, Campaign)
│   ├── repository/           # Data access layer (Repository Pattern)
│   ├── services/             # Business logic layer
│   │   ├── segmentation.py  # Customer segmentation engine
│   │   ├── campaign.py      # Campaign management
│   │   ├── email_service.py # Email delivery strategies
│   │   └── analytics.py     # Analytics and reporting
│   └── web/                  # Presentation layer
│       ├── app.py            # Flask application and routes
│       ├── templates/        # Jinja2 HTML templates
│       └── static/           # CSS, JavaScript, images
├── tests/                    # Unit and integration tests
└── _context/                 # Architecture documentation
```

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Setup Steps

1. Clone the repository:
```bash
git clone <repository-url>
cd cs411_marketing_module
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Generate mock data:
```bash
python generate_data.py
```

## Usage

### Running the Application

Start the Flask development server:

```bash
python run.py
```

The application will be available at `http://localhost:5001`

### Default Login Credentials

- **Username**: admin
- **Password**: password

### Application Flow

1. **Login**: Access the system through the login page
2. **Dashboard**: View overview statistics and recent campaigns
3. **Customer Segmentation**: Create and manage customer segments based on various criteria
4. **Campaigns**: Create targeted marketing campaigns for specific customer segments
5. **Analytics**: Monitor campaign performance with interactive charts and metrics

## Configuration

Configuration settings are managed in `config.py`:

```python
# Data file paths
CUSTOMERS_DATA_FILE = 'data/customers.json'
CAMPAIGNS_DATA_FILE = 'data/campaigns.json'

# Email configuration (for SMTP strategy)
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = ''
SMTP_PASSWORD = ''

# Debug mode
DEBUG = True
```

Environment variables can be set using a `.env` file:

```
SECRET_KEY=your-secret-key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-password
FLASK_DEBUG=True
```
