"""
Campaign Domain Model
Represents a marketing campaign entity.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass
class Campaign:
    """
    Campaign entity for marketing automation.
    
    Attributes:
        id: Unique identifier (UUID string)
        title: Campaign title/name
        content_template: Email content template with placeholders (e.g., "Hello {name}...")
        target_segment_criteria: Dictionary containing the segmentation criteria used
        status: Campaign status ('Draft' or 'Sent')
        created_at: Timestamp when campaign was created
        stats: Dictionary containing campaign statistics (sent, opened, clicked)
    """
    id: str
    title: str
    content_template: str
    target_segment_criteria: Dict
    status: str = 'Draft'
    created_at: Optional[datetime] = None
    stats: Dict[str, int] = field(default_factory=lambda: {'sent': 0, 'opened': 0, 'clicked': 0})
    
    def __post_init__(self):
        """Set created_at to current time if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert campaign to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'content_template': self.content_template,
            'target_segment_criteria': self.target_segment_criteria,
            'status': self.status,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'stats': self.stats
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Campaign':
        """Create a Campaign instance from a dictionary."""
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return Campaign(
            id=data['id'],
            title=data['title'],
            content_template=data['content_template'],
            target_segment_criteria=data['target_segment_criteria'],
            status=data.get('status', 'Draft'),
            created_at=created_at,
            stats=data.get('stats', {'sent': 0, 'opened': 0, 'clicked': 0})
        )
