"""
Analytics Service - Business Logic Layer
Provides campaign performance analytics and engagement simulation.

This service generates realistic engagement metrics for demonstration purposes
since we're using mock email sending. In production, this would integrate with
actual email tracking services (SendGrid, Mailchimp, etc.).
"""

import random
from typing import Dict, Optional
from ..models.campaign import Campaign
from ..repository.json_repo import JsonRepository


class AnalyticsService:
    """
    Service for campaign analytics and performance metrics.
    
    Responsibilities:
    - Simulate realistic engagement data (opens, clicks) for demo purposes
    - Calculate performance metrics (delivery rate, open rate, click rate, ROI)
    - Provide data for visualization dashboards
    
    Design Pattern: Service Layer Pattern
    - Encapsulates business logic for analytics calculations
    - Depends on Repository Layer for data persistence
    """
    
    def __init__(self, campaign_repository: JsonRepository):
        """
        Initialize the analytics service with a campaign repository.
        
        Args:
            campaign_repository: Repository for campaign data access
        """
        self.campaign_repo = campaign_repository
    
    def simulate_engagement(self, campaign_id: str) -> Campaign:
        """
        Simulate realistic engagement metrics for a campaign.
        
        This method generates random but realistic open and click data based on
        industry benchmarks:
        - Open Rate: 25-65% (industry average: 21.33%)
        - Click Rate: 5-20% of opens (industry average: 10.5% of opens)
        
        Only simulates if current stats are zero (campaign just launched).
        
        Args:
            campaign_id: The ID of the campaign to simulate engagement for
            
        Returns:
            Updated campaign object with simulated stats
            
        Raises:
            ValueError: If campaign not found
        """
        # Load campaign
        campaign = self.campaign_repo.get_by_id(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found.")
        
        # Only simulate if stats are all zero (just launched)
        if (campaign.stats.get('sent', 0) > 0 and 
            campaign.stats.get('opened', 0) == 0 and 
            campaign.stats.get('clicked', 0) == 0):
            
            emails_sent = campaign.stats['sent']
            
            # Generate realistic open rate (25-65%)
            open_rate = random.uniform(0.25, 0.65)
            emails_opened = int(emails_sent * open_rate)
            
            # Generate realistic click rate (5-20% of opens)
            click_rate_of_opens = random.uniform(0.05, 0.20)
            emails_clicked = int(emails_opened * click_rate_of_opens)
            
            # Update campaign stats
            campaign.stats['opened'] = emails_opened
            campaign.stats['clicked'] = emails_clicked
            
            # Save updated campaign
            self.campaign_repo.update(campaign_id, campaign)
            
            print(f"📊 Analytics Simulation Complete:")
            print(f"   Sent: {emails_sent}")
            print(f"   Opened: {emails_opened} ({open_rate*100:.1f}% open rate)")
            print(f"   Clicked: {emails_clicked} ({click_rate_of_opens*100:.1f}% click rate of opens)")
        
        return campaign
    
    def get_campaign_performance(self, campaign_id: str) -> Dict:
        """
        Calculate comprehensive performance metrics for a campaign.
        
        Returns:
            Dictionary containing:
            - sent: Total emails sent
            - opened: Total emails opened
            - clicked: Total emails clicked
            - delivery_rate: Percentage of emails successfully delivered
            - open_rate: Percentage of sent emails that were opened
            - click_rate: Percentage of opened emails that were clicked
            - click_through_rate: Percentage of sent emails that were clicked
            - roi_prediction: Estimated revenue (clicks * $15 avg value)
            - engagement_score: Overall engagement metric (0-100)
            
        Raises:
            ValueError: If campaign not found
        """
        # Load campaign
        campaign = self.campaign_repo.get_by_id(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found.")
        
        # Extract stats
        sent = campaign.stats.get('sent', 0)
        opened = campaign.stats.get('opened', 0)
        clicked = campaign.stats.get('clicked', 0)
        failed = campaign.stats.get('failed', 0)
        
        # Calculate metrics
        total_attempted = sent + failed
        delivery_rate = (sent / total_attempted * 100) if total_attempted > 0 else 0
        open_rate = (opened / sent * 100) if sent > 0 else 0
        click_rate = (clicked / opened * 100) if opened > 0 else 0
        click_through_rate = (clicked / sent * 100) if sent > 0 else 0
        
        # ROI Prediction: Assume $15 average value per click
        # (e.g., 10% conversion rate on $150 average order value)
        roi_prediction = clicked * 15.0
        
        # Engagement Score: Weighted average of open and click rates
        # Formula: (open_rate * 0.6) + (click_through_rate * 4.0)
        # This gives more weight to clicks (which indicate higher engagement)
        engagement_score = min(100, (open_rate * 0.6) + (click_through_rate * 4.0))
        
        return {
            # Raw counts
            'sent': sent,
            'opened': opened,
            'clicked': clicked,
            'failed': failed,
            
            # Calculated percentages
            'delivery_rate': round(delivery_rate, 2),
            'open_rate': round(open_rate, 2),
            'click_rate': round(click_rate, 2),
            'click_through_rate': round(click_through_rate, 2),
            
            # Business metrics
            'roi_prediction': round(roi_prediction, 2),
            'engagement_score': round(engagement_score, 1),
            
            # Campaign metadata
            'campaign_title': campaign.title,
            'campaign_status': campaign.status,
            'target_criteria': campaign.target_segment_criteria
        }
    
    def get_geographic_distribution(self, campaign_id: str) -> Dict:
        """
        Get geographic distribution of campaign target audience.
        
        This is based on the campaign's target criteria, not actual engagement.
        Useful for visualizing which regions were targeted.
        
        Args:
            campaign_id: The ID of the campaign
            
        Returns:
            Dictionary with city names as keys and counts as values
        """
        campaign = self.campaign_repo.get_by_id(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found.")
        
        # If campaign targeted a specific city, return that
        if 'city' in campaign.target_segment_criteria:
            city = campaign.target_segment_criteria['city']
            return {city: campaign.stats.get('sent', 0)}
        
        # Otherwise, return mock distribution for visualization
        # In production, this would query actual customer data
        sent = campaign.stats.get('sent', 0)
        if sent == 0:
            return {}
        
        # Mock distribution: 40% Istanbul, 25% Ankara, 15% Izmir, 20% Others
        return {
            'Istanbul': int(sent * 0.40),
            'Ankara': int(sent * 0.25),
            'Izmir': int(sent * 0.15),
            'Others': sent - int(sent * 0.40) - int(sent * 0.25) - int(sent * 0.15)
        }
    
    def get_device_distribution(self, campaign_id: str) -> Dict:
        """
        Get mock device distribution for email opens.
        
        In production, this would come from email tracking pixels that detect
        user agents. For demo purposes, we generate realistic distributions.
        
        Args:
            campaign_id: The ID of the campaign
            
        Returns:
            Dictionary with device types as keys and percentages as values
        """
        campaign = self.campaign_repo.get_by_id(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found.")
        
        opened = campaign.stats.get('opened', 0)
        if opened == 0:
            return {'Mobile': 0, 'Desktop': 0, 'Tablet': 0}
        
        # Mock distribution based on industry averages
        # Source: Litmus Email Analytics (2024)
        mobile_pct = random.uniform(50, 65)  # 50-65% mobile
        tablet_pct = random.uniform(5, 10)   # 5-10% tablet
        desktop_pct = 100 - mobile_pct - tablet_pct
        
        return {
            'Mobile': round(mobile_pct, 1),
            'Desktop': round(desktop_pct, 1),
            'Tablet': round(tablet_pct, 1)
        }
