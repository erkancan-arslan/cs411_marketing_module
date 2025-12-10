"""
Flask Web Application - Presentation Layer
Marketing Automation Module - CS411 Software Architecture Project

This module implements the Presentation Layer following the Layered Architecture pattern.
NO BUSINESS LOGIC should be placed here - only routing, request handling, and view rendering.
All business logic is delegated to the Service Layer.
"""
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import models, repositories, and services
from src.models.customer import Customer
from src.models.campaign import Campaign
from src.repository.json_repo import JsonRepository
from src.services.segmentation import SegmentationService
from src.services.campaign import CampaignService
from config import config


# ============================================================================
# APPLICATION FACTORY & DEPENDENCY INJECTION
# ============================================================================

def create_app(config_name='development'):
    """
    Application factory pattern.
    Creates and configures the Flask application with dependency injection.
    
    Args:
        config_name: Configuration environment ('development' or 'production')
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize repositories (Data Layer)
    customer_repository = JsonRepository(
        app.config['CUSTOMERS_DATA_FILE'],
        Customer.from_dict,
        lambda c: c.to_dict()
    )
    
    campaign_repository = JsonRepository(
        app.config['CAMPAIGNS_DATA_FILE'],
        Campaign.from_dict,
        lambda c: c.to_dict()
    )
    
    # Initialize services (Business Logic Layer)
    segmentation_service = SegmentationService(customer_repository)
    campaign_service = CampaignService(campaign_repository, segmentation_service)
    
    # Store services in app context for access in routes
    app.segmentation_service = segmentation_service
    app.campaign_service = campaign_service
    
    return app


# Create the application instance
app = create_app()


# ============================================================================
# AUTHENTICATION DECORATOR
# ============================================================================

def login_required(f):
    """
    Decorator to protect routes that require authentication.
    Redirects to login page if user is not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# ROUTES - AUTHENTICATION
# ============================================================================

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route with mock authentication.
    
    For demonstration purposes, accepts any username/password combination.
    In production, this would validate against a user database.
    
    GET:  Display login form
    POST: Process login credentials and create session
    """
    # If already logged in, redirect to dashboard
    if 'user' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Mock authentication - accept any non-empty credentials
        if username and password:
            # Create session
            session['user'] = username
            session.permanent = True
            
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Please enter both username and password.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """
    Logout route - clears the session and redirects to login.
    """
    username = session.get('user', 'User')
    session.clear()
    flash(f'Goodbye, {username}! You have been logged out.', 'info')
    return redirect(url_for('login'))


# ============================================================================
# ROUTES - DASHBOARD
# ============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """
    Dashboard route - displays system overview and key metrics.
    
    Shows:
    - Total customers count
    - Active customers count
    - Total campaigns count
    - Sent campaigns count
    - Recent campaigns list
    """
    # Delegate to Service Layer - NO business logic here
    all_customers = app.segmentation_service.get_all_customers()
    active_customers = [c for c in all_customers if c.is_active]
    
    all_campaigns = app.campaign_service.get_all_campaigns()
    sent_campaigns = app.campaign_service.get_sent_campaigns()
    
    # Prepare data for view
    stats = {
        'total_customers': len(all_customers),
        'active_customers': len(active_customers),
        'total_campaigns': len(all_campaigns),
        'sent_campaigns': len(sent_campaigns),
        'draft_campaigns': len(all_campaigns) - len(sent_campaigns)
    }
    
    # Get recent campaigns (last 5)
    recent_campaigns = sorted(
        all_campaigns,
        key=lambda c: c.created_at if c.created_at else '',
        reverse=True
    )[:5]
    
    return render_template(
        'dashboard.html',
        stats=stats,
        recent_campaigns=recent_campaigns,
        username=session.get('user', 'User')
    )


# ============================================================================
# ROUTES - CUSTOMER SEGMENTATION
# ============================================================================

@app.route('/segmentation', methods=['GET', 'POST'])
@login_required
def segmentation():
    """
    Customer segmentation route.
    
    GET:  Display segmentation form
    POST: Process filter criteria and display results
    
    Allows filtering customers by:
    - City
    - Age range (min/max)
    - Spending score range
    - Active status
    """
    customers = []
    criteria = {}
    stats = None
    
    if request.method == 'POST':
        # Build criteria from form data
        city = request.form.get('city', '').strip()
        min_age = request.form.get('min_age', '').strip()
        max_age = request.form.get('max_age', '').strip()
        min_spending_score = request.form.get('min_spending_score', '').strip()
        max_spending_score = request.form.get('max_spending_score', '').strip()
        min_spent = request.form.get('min_spent', '').strip()
        max_spent = request.form.get('max_spent', '').strip()
        is_active = request.form.get('is_active', '')
        
        # Build criteria dictionary
        if city:
            criteria['city'] = city
        if min_age:
            criteria['min_age'] = int(min_age)
        if max_age:
            criteria['max_age'] = int(max_age)
        if min_spending_score:
            criteria['min_spending_score'] = int(min_spending_score)
        if max_spending_score:
            criteria['max_spending_score'] = int(max_spending_score)
        if min_spent:
            criteria['min_spent'] = float(min_spent)
        if max_spent:
            criteria['max_spent'] = float(max_spent)
        if is_active:
            criteria['is_active'] = is_active == 'true'
        
        # Delegate to Service Layer
        if criteria:
            customers = app.segmentation_service.filter_customers(criteria)
            stats = app.segmentation_service.get_segment_statistics(customers)
            
            flash(f'Found {len(customers)} customers matching your criteria.', 'success')
        else:
            customers = app.segmentation_service.get_all_customers()
            stats = app.segmentation_service.get_segment_statistics(customers)
            flash('Showing all customers (no filters applied).', 'info')
    
    # Get unique cities for dropdown
    all_customers = app.segmentation_service.get_all_customers()
    cities = sorted(list(set(c.city for c in all_customers)))
    
    return render_template(
        'segmentation.html',
        customers=customers,
        criteria=criteria,
        stats=stats,
        cities=cities
    )


# ============================================================================
# ROUTES - CAMPAIGN MANAGEMENT
# ============================================================================

@app.route('/campaigns')
@login_required
def campaigns_list():
    """
    Campaigns list route - displays all campaigns.
    """
    all_campaigns = app.campaign_service.get_all_campaigns()
    
    # Sort by created_at (most recent first)
    all_campaigns = sorted(
        all_campaigns,
        key=lambda c: c.created_at if c.created_at else '',
        reverse=True
    )
    
    return render_template('campaigns.html', campaigns=all_campaigns)


@app.route('/campaigns/new', methods=['GET', 'POST'])
@login_required
def campaign_new():
    """
    Create new campaign route.
    
    GET:  Display campaign creation form
    POST: Process form and create campaign
    """
    if request.method == 'POST':
        # Extract form data
        title = request.form.get('title', '').strip()
        content_template = request.form.get('content_template', '').strip()
        
        # Build segmentation criteria from form
        criteria = {}
        city = request.form.get('city', '').strip()
        min_age = request.form.get('min_age', '').strip()
        max_age = request.form.get('max_age', '').strip()
        min_spending_score = request.form.get('min_spending_score', '').strip()
        max_spending_score = request.form.get('max_spending_score', '').strip()
        min_spent = request.form.get('min_spent', '').strip()
        max_spent = request.form.get('max_spent', '').strip()
        is_active = request.form.get('is_active', '')
        
        if city:
            criteria['city'] = city
        if min_age:
            criteria['min_age'] = int(min_age)
        if max_age:
            criteria['max_age'] = int(max_age)
        if min_spending_score:
            criteria['min_spending_score'] = int(min_spending_score)
        if max_spending_score:
            criteria['max_spending_score'] = int(max_spending_score)
        if min_spent:
            criteria['min_spent'] = float(min_spent)
        if max_spent:
            criteria['max_spent'] = float(max_spent)
        if is_active:
            criteria['is_active'] = is_active == 'true'
        
        # Validate
        if not title:
            flash('Campaign title is required.', 'danger')
            return redirect(url_for('campaign_new'))
        
        if not content_template:
            flash('Campaign content is required.', 'danger')
            return redirect(url_for('campaign_new'))
        
        if not criteria:
            flash('Please select at least one targeting criterion.', 'danger')
            return redirect(url_for('campaign_new'))
        
        try:
            # Delegate to Service Layer
            campaign = app.campaign_service.create_campaign(
                title=title,
                content_template=content_template,
                target_segment_criteria=criteria
            )
            
            flash(f'Campaign "{title}" created successfully!', 'success')
            return redirect(url_for('campaign_detail', campaign_id=campaign.id))
            
        except ValueError as e:
            flash(f'Error creating campaign: {str(e)}', 'danger')
            return redirect(url_for('campaign_new'))
    
    # GET request - show form
    all_customers = app.segmentation_service.get_all_customers()
    cities = sorted(list(set(c.city for c in all_customers)))
    
    return render_template('campaign_new.html', cities=cities)


@app.route('/campaigns/<campaign_id>')
@login_required
def campaign_detail(campaign_id):
    """
    Campaign detail route - displays campaign information and launch option.
    
    Args:
        campaign_id: Campaign unique identifier
    """
    # Delegate to Service Layer
    campaign = app.campaign_service.get_campaign_by_id(campaign_id)
    
    if not campaign:
        flash('Campaign not found.', 'danger')
        return redirect(url_for('campaigns_list'))
    
    # Get target audience preview
    target_customers = app.segmentation_service.filter_customers(
        campaign.target_segment_criteria
    )
    
    return render_template(
        'campaign_detail.html',
        campaign=campaign,
        target_audience_size=len(target_customers),
        target_customers=target_customers[:10]  # Preview first 10
    )


@app.route('/campaigns/<campaign_id>/launch', methods=['POST'])
@login_required
def campaign_launch(campaign_id):
    """
    Launch campaign route - triggers email sending.
    
    Args:
        campaign_id: Campaign unique identifier
    """
    use_real_email = request.form.get('use_real_email') == 'true'
    
    try:
        # Delegate to Service Layer - Strategy Pattern in action!
        result = app.campaign_service.launch_campaign(
            campaign_id=campaign_id,
            use_real_email=use_real_email
        )
        
        if result['success']:
            flash(
                f'Campaign launched successfully! {result["emails_sent"]} emails sent.',
                'success'
            )
        else:
            flash(f'Campaign launch failed: {result["message"]}', 'warning')
            
    except ValueError as e:
        flash(f'Error launching campaign: {str(e)}', 'danger')
    
    return redirect(url_for('campaign_detail', campaign_id=campaign_id))


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors."""
    return render_template('500.html'), 500


# ============================================================================
# TEMPLATE FILTERS
# ============================================================================

@app.template_filter('datetime_format')
def datetime_format(value, format='%B %d, %Y at %I:%M %p'):
    """Format datetime objects in templates."""
    if value is None:
        return ''
    return value.strftime(format)


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=app.config['DEBUG']
    )
