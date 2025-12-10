"""
Customer Segmentation Service
Business logic for filtering and segmenting customers based on dynamic criteria.
"""
from typing import List, Dict, Optional
from src.models.customer import Customer
from src.repository.json_repo import JsonRepository


class SegmentationService:
    """
    Service responsible for customer segmentation logic.
    
    This service provides functionality to retrieve and filter customers
    based on various criteria (city, age, spending patterns, etc.).
    Implements the business logic layer for customer segmentation.
    """
    
    def __init__(self, customer_repository: JsonRepository[Customer]):
        """
        Initialize the segmentation service.
        
        Args:
            customer_repository: Repository for customer data access
        """
        self.customer_repository = customer_repository
    
    def get_all_customers(self) -> List[Customer]:
        """
        Retrieve all customers from the repository.
        
        Returns:
            List of all Customer objects
        """
        return self.customer_repository.get_all()
    
    def filter_customers(self, criteria: Dict) -> List[Customer]:
        """
        Filter customers based on dynamic criteria using AND logic.
        
        All provided criteria must match for a customer to be included.
        
        Supported criteria:
            - city (str): Exact match for customer city
            - min_age (int): Minimum age (inclusive)
            - max_age (int): Maximum age (inclusive)
            - min_spent (float): Minimum total amount spent (inclusive)
            - max_spent (float): Maximum total amount spent (inclusive)
            - min_spending_score (int): Minimum spending score (inclusive)
            - max_spending_score (int): Maximum spending score (inclusive)
            - is_active (bool): Active status filter
        
        Args:
            criteria: Dictionary containing filter conditions
        
        Returns:
            List of Customer objects matching ALL criteria
        
        Example:
            criteria = {
                'city': 'Ankara',
                'min_age': 25,
                'min_spent': 1000,
                'is_active': True
            }
        """
        all_customers = self.get_all_customers()
        filtered_customers = []
        
        for customer in all_customers:
            if self._matches_criteria(customer, criteria):
                filtered_customers.append(customer)
        
        return filtered_customers
    
    def _matches_criteria(self, customer: Customer, criteria: Dict) -> bool:
        """
        Check if a customer matches all provided criteria.
        
        Args:
            customer: Customer object to check
            criteria: Dictionary of filter conditions
        
        Returns:
            True if customer matches all criteria, False otherwise
        """
        # City filter (exact match, case-insensitive)
        if 'city' in criteria and criteria['city']:
            if customer.city.lower() != criteria['city'].lower():
                return False
        
        # Age filters
        if 'min_age' in criteria and criteria['min_age'] is not None:
            if customer.age < criteria['min_age']:
                return False
        
        if 'max_age' in criteria and criteria['max_age'] is not None:
            if customer.age > criteria['max_age']:
                return False
        
        # Total spent filters
        if 'min_spent' in criteria and criteria['min_spent'] is not None:
            if customer.total_spent < criteria['min_spent']:
                return False
        
        if 'max_spent' in criteria and criteria['max_spent'] is not None:
            if customer.total_spent > criteria['max_spent']:
                return False
        
        # Spending score filters
        if 'min_spending_score' in criteria and criteria['min_spending_score'] is not None:
            if customer.spending_score < criteria['min_spending_score']:
                return False
        
        if 'max_spending_score' in criteria and criteria['max_spending_score'] is not None:
            if customer.spending_score > criteria['max_spending_score']:
                return False
        
        # Active status filter
        if 'is_active' in criteria and criteria['is_active'] is not None:
            if customer.is_active != criteria['is_active']:
                return False
        
        # All criteria matched
        return True
    
    def get_segment_statistics(self, customers: List[Customer]) -> Dict:
        """
        Calculate statistics for a given customer segment.
        
        Args:
            customers: List of customers to analyze
        
        Returns:
            Dictionary containing segment statistics
        """
        if not customers:
            return {
                'total_count': 0,
                'active_count': 0,
                'avg_age': 0,
                'avg_spending_score': 0,
                'total_revenue': 0,
                'avg_revenue_per_customer': 0
            }
        
        active_count = sum(1 for c in customers if c.is_active)
        total_age = sum(c.age for c in customers)
        total_spending_score = sum(c.spending_score for c in customers)
        total_revenue = sum(c.total_spent for c in customers)
        
        return {
            'total_count': len(customers),
            'active_count': active_count,
            'avg_age': round(total_age / len(customers), 1),
            'avg_spending_score': round(total_spending_score / len(customers), 1),
            'total_revenue': round(total_revenue, 2),
            'avg_revenue_per_customer': round(total_revenue / len(customers), 2)
        }
