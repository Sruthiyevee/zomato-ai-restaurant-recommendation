"""
Session Manager Module for Phase 2
Manages user session state and query history
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

from validator import PriceRange

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SessionState(Enum):
    """Session states"""
    INITIALIZED = "initialized"
    INPUT_COLLECTED = "input_collected"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class SessionManager:
    """Manages user session state and history"""
    
    def __init__(self, session_timeout_minutes: int = 30):
        """
        Initialize session manager
        
        Args:
            session_timeout_minutes: Session timeout in minutes
        """
        self.session_id = self._generate_session_id()
        self.state = SessionState.INITIALIZED
        self.session_timeout_minutes = session_timeout_minutes
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        
        # Current query
        self.current_city: Optional[str] = None
        self.current_price_range: Optional[PriceRange] = None
        
        # Query history
        self.query_history: List[Dict] = []
        
        logger.info(f"Session initialized: {self.session_id}")
    
    def _generate_session_id(self) -> str:
        """
        Generate unique session ID
        
        Returns:
            Session ID string
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        import random
        random_suffix = random.randint(1000, 9999)
        return f"session_{timestamp}_{random_suffix}"
    
    def set_user_input(self, city: str, price_range: PriceRange) -> None:
        """
        Set current user input
        
        Args:
            city: Selected city
            price_range: Selected price range
        """
        self.current_city = city
        self.current_price_range = price_range
        self.state = SessionState.INPUT_COLLECTED
        self.last_activity = datetime.now()
        
        logger.info(f"User input set: city={city}, price_range={price_range.value}")
    
    def get_user_input(self) -> Optional[Dict[str, any]]:
        """
        Get current user input
        
        Returns:
            Dictionary with city and price_range, or None if not set
        """
        if self.current_city and self.current_price_range:
            return {
                'city': self.current_city,
                'price_range': self.current_price_range
            }
        return None
    
    def start_processing(self) -> None:
        """Mark session as processing"""
        self.state = SessionState.PROCESSING
        self.last_activity = datetime.now()
        logger.info("Session state: PROCESSING")
    
    def complete_query(self, results: Optional[Dict] = None) -> None:
        """
        Mark query as completed and add to history
        
        Args:
            results: Optional query results to store
        """
        self.state = SessionState.COMPLETED
        self.last_activity = datetime.now()
        
        # Add to history
        query_entry = {
            'timestamp': datetime.now().isoformat(),
            'city': self.current_city,
            'price_range': self.current_price_range.value if self.current_price_range else None,
            'results': results
        }
        self.query_history.append(query_entry)
        
        logger.info(f"Query completed. History entries: {len(self.query_history)}")
    
    def set_error(self, error_message: str) -> None:
        """
        Set session error state
        
        Args:
            error_message: Error message
        """
        self.state = SessionState.ERROR
        self.last_activity = datetime.now()
        
        # Add error to history
        query_entry = {
            'timestamp': datetime.now().isoformat(),
            'city': self.current_city,
            'price_range': self.current_price_range.value if self.current_price_range else None,
            'error': error_message
        }
        self.query_history.append(query_entry)
        
        logger.error(f"Session error: {error_message}")
    
    def reset_for_new_query(self) -> None:
        """Reset session for a new query while maintaining history"""
        self.current_city = None
        self.current_price_range = None
        self.state = SessionState.INITIALIZED
        self.last_activity = datetime.now()
        logger.info("Session reset for new query")
    
    def is_expired(self) -> bool:
        """
        Check if session has expired
        
        Returns:
            True if session is expired, False otherwise
        """
        time_diff = datetime.now() - self.last_activity
        return time_diff.total_seconds() > (self.session_timeout_minutes * 60)
    
    def get_session_info(self) -> Dict:
        """
        Get session information
        
        Returns:
            Dictionary with session details
        """
        return {
            'session_id': self.session_id,
            'state': self.state.value,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'is_expired': self.is_expired(),
            'query_count': len(self.query_history),
            'current_city': self.current_city,
            'current_price_range': self.current_price_range.value if self.current_price_range else None
        }
    
    def get_query_history(self) -> List[Dict]:
        """
        Get query history
        
        Returns:
            List of query history entries
        """
        return self.query_history.copy()
    
    def clear_history(self) -> None:
        """Clear query history"""
        self.query_history = []
        logger.info("Query history cleared")
    
    def get_last_query(self) -> Optional[Dict]:
        """
        Get the last query from history
        
        Returns:
            Last query entry or None if no history
        """
        return self.query_history[-1] if self.query_history else None
