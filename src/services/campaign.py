"""
Campaign Management Service
Business logic for creating and launching marketing campaigns.
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict
from src.models.campaign import Campaign
from src.models.customer import Customer
from src.repository.json_repo import JsonRepository
from src.services.segmentation import SegmentationService
from src.services.email_service import IEmailProvider, EmailServiceFactory


class CampaignService:
    """
    Service responsible for campaign management and execution.
    
    This service orchestrates the campaign lifecycle:
    1. Campaign creation and validation
    2. Target audience segmentation
    3. Email sending (via Strategy Pattern)
    4. Campaign status tracking and statistics
    """
    
    def __init__(
        self,
        campaign_repository: JsonRepository[Campaign],
        segmentation_service: SegmentationService
    ):
        """
        Initialize the campaign service.
        
        Args:
            campaign_repository: Repository for campaign data access
            segmentation_service: Service for customer segmentation
        """
        self.campaign_repository = campaign_repository
        self.segmentation_service = segmentation_service
    
    def create_campaign(
        self,
        title: str,
        content_template: str,
        target_segment_criteria: Dict
    ) -> Campaign:
        """
        Create a new campaign in Draft status.
        
        Args:
            title: Campaign title/name
            content_template: Email template with placeholders (e.g., "Hello {name}...")
            target_segment_criteria: Dictionary of segmentation criteria
        
        Returns:
            The created Campaign object
        
        Raises:
            ValueError: If validation fails
        """
        # Validation
        if not title or not title.strip():
            raise ValueError("Campaign title cannot be empty")
        
        if not content_template or not content_template.strip():
            raise ValueError("Campaign content template cannot be empty")
        
        if not target_segment_criteria:
            raise ValueError("Target segment criteria cannot be empty")
        
        # Create campaign object
        campaign = Campaign(
            id=str(uuid.uuid4()),
            title=title.strip(),
            content_template=content_template.strip(),
            target_segment_criteria=target_segment_criteria,
            status='Draft',
            created_at=datetime.now(),
            stats={'sent': 0, 'opened': 0, 'clicked': 0}
        )
        
        # Save to repository
        self.campaign_repository.save(campaign)
        
        print(f"✅ Campaign '{title}' created successfully (ID: {campaign.id})")
        return campaign
    
    def launch_campaign(
        self,
        campaign_id: str,
        use_real_email: bool = False
    ) -> Dict:
        """
        Launch a campaign by sending emails to the target audience.
        
        This method demonstrates the STRATEGY PATTERN in action:
        - Selects the appropriate email provider based on use_real_email flag
        - Uses the same interface (IEmailProvider.send) regardless of strategy
        
        Args:
            campaign_id: ID of the campaign to launch
            use_real_email: If True, uses SMTP; if False, uses Mock provider
        
        Returns:
            Dictionary containing launch results and statistics
        
        Raises:
            ValueError: If campaign not found or already sent
        """
        # Load campaign
        campaign = self.campaign_repository.get_by_id(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found")
        
        if campaign.status == 'Sent':
            raise ValueError("Campaign has already been sent")
        
        print(f"\n🚀 Launching campaign: {campaign.title}")
        print(f"   Campaign ID: {campaign.id}")
        
        # Get target audience using segmentation service
        print(f"   Retrieving target audience with criteria: {campaign.target_segment_criteria}")
        target_customers = self.segmentation_service.filter_customers(
            campaign.target_segment_criteria
        )
        
        if not target_customers:
            print("⚠️  No customers match the target criteria. Campaign aborted.")
            return {
                'success': False,
                'message': 'No customers match target criteria',
                'emails_sent': 0,
                'target_audience_size': 0
            }
        
        print(f"   Target audience size: {len(target_customers)} customers")
        
        # STRATEGY PATTERN: Select email provider based on flag
        email_provider: IEmailProvider = EmailServiceFactory.create_provider(use_real_email)
        
        # Send emails to each customer in target segment
        emails_sent = 0
        emails_failed = 0
        
        print(f"\n📨 Sending emails...")
        for customer in target_customers:
            # Personalize content by replacing placeholders
            personalized_content = self._personalize_content(
                campaign.content_template,
                customer
            )
            
            # Use the strategy to send email
            success = email_provider.send(
                to_email=customer.email,
                subject=campaign.title,
                body=personalized_content
            )
            
            if success:
                emails_sent += 1
            else:
                emails_failed += 1
        
        # Update campaign statistics
        campaign.stats['sent'] = emails_sent
        campaign.status = 'Sent'
        
        # Save updated campaign
        self.campaign_repository.update(campaign.id, campaign)
        
        print(f"\n✅ Campaign launched successfully!")
        print(f"   Emails sent: {emails_sent}")
        print(f"   Emails failed: {emails_failed}")
        
        return {
            'success': True,
            'message': 'Campaign launched successfully',
            'emails_sent': emails_sent,
            'emails_failed': emails_failed,
            'target_audience_size': len(target_customers),
            'campaign_id': campaign.id
        }
    
    def _personalize_content(self, template: str, customer: Customer) -> str:
        """
        Personalize email content by replacing placeholders with customer data.
        
        Supported placeholders:
        - {name}: Customer name
        - {email}: Customer email
        - {city}: Customer city
        
        Args:
            template: Content template with placeholders
            customer: Customer object with data
        
        Returns:
            Personalized content string
        """
        personalized = template
        personalized = personalized.replace('{name}', customer.name)
        personalized = personalized.replace('{email}', customer.email)
        personalized = personalized.replace('{city}', customer.city)
        return personalized
    
    def get_all_campaigns(self) -> List[Campaign]:
        """
        Retrieve all campaigns.
        
        Returns:
            List of all Campaign objects
        """
        return self.campaign_repository.get_all()
    
    def get_campaign_by_id(self, campaign_id: str) -> Optional[Campaign]:
        """
        Retrieve a campaign by ID.
        
        Args:
            campaign_id: Campaign unique identifier
        
        Returns:
            Campaign object if found, None otherwise
        """
        return self.campaign_repository.get_by_id(campaign_id)
    
    def get_draft_campaigns(self) -> List[Campaign]:
        """
        Retrieve all campaigns in Draft status.
        
        Returns:
            List of draft Campaign objects
        """
        return self.campaign_repository.find(lambda c: c.status == 'Draft')
    
    def get_sent_campaigns(self) -> List[Campaign]:
        """
        Retrieve all campaigns that have been sent.
        
        Returns:
            List of sent Campaign objects
        """
        return self.campaign_repository.find(lambda c: c.status == 'Sent')
