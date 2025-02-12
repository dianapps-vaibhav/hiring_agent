from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime

@dataclass
class UserApplicationData:
    selected_job: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    age_consent: Optional[bool] = None
    country_consent: Optional[bool] = None
    shift_preference: Optional[str] = None
    environment_consent: Optional[bool] = None
    contact_preference: Optional[str] = None
    interview_datetime: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}

class SessionDataManager:
    def __init__(self):
        self._session_data: Dict[str, UserApplicationData] = {}
    
    def get_user_data(self, session_id: str) -> UserApplicationData:
        if session_id not in self._session_data:
            self._session_data[session_id] = UserApplicationData()
        return self._session_data[session_id]
    
    def update_user_data(self, session_id: str, **kwargs) -> None:
        """Update specific fields in user data"""
        user_data = self.get_user_data(session_id)
        for key, value in kwargs.items():
            if hasattr(user_data, key):
                setattr(user_data, key, value)
    
    def is_field_filled(self, session_id: str, field: str) -> bool:
        """Check if a specific field has been filled"""
        user_data = self.get_user_data(session_id)
        return getattr(user_data, field, None) is not None
    
    def get_next_empty_field(self, session_id: str) -> Optional[str]:
        """Get the next empty required field"""
        user_data = self.get_user_data(session_id)
        required_fields = [
            'selected_job', 'name', 'phone', 'email', 
            'age_consent', 'country_consent', 'shift_preference',
            'environment_consent', 'contact_preference'
        ]
        
        for field in required_fields:
            if getattr(user_data, field, None) is None:
                return field
        return None