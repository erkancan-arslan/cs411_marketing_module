"""
Customer Domain Model
Represents a customer entity in the CRM system with all relevant attributes.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Customer:
    """
    Customer entity with attributes for segmentation and marketing.
    
    Attributes:
        id: Unique identifier (UUID string)
        name: Customer full name
        email: Customer email address
        city: Customer city (used for geographic segmentation)
        age: Customer age in years
        spending_score: Score from 1-100 indicating spending potential
        total_spent: Total amount spent by customer (currency)
        is_active: Whether the customer is currently active
    """
    id: str
    name: str
    email: str
    city: str
    age: int
    spending_score: int
    total_spent: float
    is_active: bool
    
    def to_dict(self) -> dict:
        """Convert customer to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'city': self.city,
            'age': self.age,
            'spending_score': self.spending_score,
            'total_spent': self.total_spent,
            'is_active': self.is_active
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Customer':
        """Create a Customer instance from a dictionary."""
        return Customer(
            id=data['id'],
            name=data['name'],
            email=data['email'],
            city=data['city'],
            age=data['age'],
            spending_score=data['spending_score'],
            total_spent=data['total_spent'],
            is_active=data['is_active']
        )
