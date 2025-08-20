from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import date

class Location(BaseModel):
    """
    Pydantic model for a Workday location record.
    `raw_data` holds the full SOAP response dict for any extra fields.
    """
    # Basic identification
    location_id: Optional[str]
    location_name: Optional[str]
    
    # Status and dates
    effective_date: Optional[date]
    inactive: Optional[bool]
    
    # Location details
    location_type: Optional[str]
    location_usage: Optional[List[str]]
    location_attributes: Optional[List[str]]
    
    # Hierarchy
    superior_location_id: Optional[str]
    superior_location_name: Optional[str]
    
    # Address and coordinates
    latitude: Optional[float]
    longitude: Optional[float]
    altitude: Optional[float]
    allow_duplicate_coordinates: Optional[bool]
    
    # Address information
    formatted_address: Optional[str]
    address_line_1: Optional[str]
    municipality: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]
    country_region: Optional[str]
    
    # Additional fields
    time_profile: Optional[str]
    locale: Optional[str]
    user_language: Optional[str]
    time_zone: Optional[str]
    currency: Optional[str]
    trade_name: Optional[str]
    worksite_id: Optional[str]
    default_job_posting_location: Optional[str]
    location_hierarchy: Optional[List[str]]
    
    # Raw payload
    raw_data: Dict[str, Any] = Field(..., exclude=True)

    class Config:
        extra = "ignore" 