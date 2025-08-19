"""
Listings DB Contracts Package

Data contracts for the Finder property listings application.
"""

from .schemas import (
    # Enums
    PropertyType,
    TenancyType,
    ClientType,
    
    # Base schemas
    AddressBase,
    AddressCreate,
    Address,
    LocationBase,
    LocationCreate,
    Location,
    
    # Image schemas
    ImageBase,
    ImageCreateNested,
    Image,
    ImageCreate,
    
    # Estate Agent schemas
    EstateAgentBase,
    EstateAgentCreate,
    EstateAgent,
    
    # Listing schemas
    ListingBase,
    ListingUpdate,
    ListingCreate,
    Listing,
    ListingSummary,
    
    # API Response schemas
    Error,
    ApiResponse,
    MCPResponse,
    PaginatedResponse,
    
    # Utility functions
    get_contracts_version,
    
    # Floorplan schemas
    FloorplanBase,
    FloorplanCreate,
    FloorplanCreateNested,
    Floorplan,
)

__version__ = "1.0.4"

__all__ = [
    # Enums
    "PropertyType",
    "TenancyType", 
    "ClientType",
    
    # Base schemas
    "AddressBase",
    "AddressCreate",
    "Address",
    "LocationBase",
    "LocationCreate",
    "Location",
    
    # Image schemas
    "ImageBase",
    "ImageCreateNested",
    "Image",
    "ImageCreate",
    
    # Estate Agent schemas
    "EstateAgentBase",
    "EstateAgentCreate",
    "EstateAgent",
    
    # Listing schemas
    "ListingBase",
    "ListingUpdate",
    "ListingCreate",
    "Listing",
    "ListingSummary",
    
    # API Response schemas
    "Error",
    "ApiResponse",
    "MCPResponse",
    "PaginatedResponse",
    
    # Utility functions
    "get_contracts_version",
    
    # Floorplan schemas
    "FloorplanBase",
    "FloorplanCreate",
    "FloorplanCreateNested",
    "Floorplan",
]
