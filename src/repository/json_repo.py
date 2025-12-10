"""
Repository Pattern Implementation for JSON Data Storage
Provides generic CRUD operations for JSON files, decoupling data access from business logic.
"""
import json
import os
from typing import List, Optional, Callable, TypeVar, Generic
from pathlib import Path

T = TypeVar('T')


class JsonRepository(Generic[T]):
    """
    Generic Repository for JSON file-based data storage.
    
    This class implements the Repository Pattern to abstract data access operations.
    It provides a consistent interface for CRUD operations regardless of the underlying
    data storage mechanism (currently JSON files).
    
    Type Parameters:
        T: The domain model type this repository manages
    
    Attributes:
        file_path: Path to the JSON data file
        from_dict: Function to deserialize dict to domain model
        to_dict: Function to serialize domain model to dict
    """
    
    def __init__(
        self, 
        file_path: str, 
        from_dict: Callable[[dict], T],
        to_dict: Callable[[T], dict]
    ):
        """
        Initialize the repository.
        
        Args:
            file_path: Absolute or relative path to the JSON file
            from_dict: Function that converts a dict to domain model instance
            to_dict: Function that converts a domain model instance to dict
        """
        self.file_path = Path(file_path)
        self.from_dict = from_dict
        self.to_dict = to_dict
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create the JSON file with empty list if it doesn't exist."""
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def _read_all_raw(self) -> List[dict]:
        """Read raw data from JSON file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _write_all_raw(self, data: List[dict]):
        """Write raw data to JSON file."""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_all(self) -> List[T]:
        """
        Retrieve all entities from the repository.
        
        Returns:
            List of domain model instances
        """
        raw_data = self._read_all_raw()
        return [self.from_dict(item) for item in raw_data]
    
    def get_by_id(self, entity_id: str) -> Optional[T]:
        """
        Retrieve a single entity by its ID.
        
        Args:
            entity_id: The unique identifier of the entity
        
        Returns:
            Domain model instance if found, None otherwise
        """
        raw_data = self._read_all_raw()
        for item in raw_data:
            if item.get('id') == entity_id:
                return self.from_dict(item)
        return None
    
    def save(self, entity: T) -> T:
        """
        Save a new entity to the repository.
        
        Args:
            entity: The domain model instance to save
        
        Returns:
            The saved entity
        """
        raw_data = self._read_all_raw()
        raw_data.append(self.to_dict(entity))
        self._write_all_raw(raw_data)
        return entity
    
    def update(self, entity_id: str, entity: T) -> Optional[T]:
        """
        Update an existing entity in the repository.
        
        Args:
            entity_id: The unique identifier of the entity to update
            entity: The updated domain model instance
        
        Returns:
            The updated entity if found and updated, None otherwise
        """
        raw_data = self._read_all_raw()
        for i, item in enumerate(raw_data):
            if item.get('id') == entity_id:
                raw_data[i] = self.to_dict(entity)
                self._write_all_raw(raw_data)
                return entity
        return None
    
    def delete(self, entity_id: str) -> bool:
        """
        Delete an entity from the repository.
        
        Args:
            entity_id: The unique identifier of the entity to delete
        
        Returns:
            True if entity was found and deleted, False otherwise
        """
        raw_data = self._read_all_raw()
        original_length = len(raw_data)
        raw_data = [item for item in raw_data if item.get('id') != entity_id]
        
        if len(raw_data) < original_length:
            self._write_all_raw(raw_data)
            return True
        return False
    
    def find(self, predicate: Callable[[T], bool]) -> List[T]:
        """
        Find all entities matching a predicate function.
        
        Args:
            predicate: A function that takes an entity and returns True if it matches
        
        Returns:
            List of matching domain model instances
        """
        all_entities = self.get_all()
        return [entity for entity in all_entities if predicate(entity)]
    
    def count(self) -> int:
        """
        Count total number of entities in the repository.
        
        Returns:
            Total count of entities
        """
        return len(self._read_all_raw())
