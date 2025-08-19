"""
Pydantic schemas for the Listings DB contracts.

These schemas define the data shape for API requests and responses,
ensuring type validation and serialization are handled correctly by FastAPI.
They are the single source of truth for data contracts within the Finder application ecosystem.
"""
import enum
from pydantic import BaseModel, ConfigDict, Field, field_serializer
from typing import List, Optional, Generic, TypeVar, Any, Dict
from datetime import datetime
import importlib.metadata
import base64

# --- Enums ---
class PropertyType(enum.Enum):
    DETACHED = "detached"
    SEMI_DETACHED = "semi_detached"
    TERRACED = "terraced"
    END_OF_TERRACE = "end_of_terrace"
    FLAT = "flat"

class TenancyType(enum.Enum):
    FREEHOLD = "freehold"
    LEASEHOLD = "leasehold"

class ClientType(enum.Enum):
    THOMAS_AND_MAY_API = "thomas_and_may_api"
    THOMAS_AND_MAY_WEB = "thomas_and_may_web"
    GENERIC = "generic"

# --- Generic API Schemas ---
T = TypeVar("T")

def get_contracts_version() -> str:
    """Fetches the version of the finder_contracts package."""
    try:
        return importlib.metadata.version("listings-db-contracts")
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0-dev"

class Error(BaseModel):
    """Represents a standard error object."""
    message: str
    code: Optional[str] = None

class ApiResponse(BaseModel, Generic[T]):
    """A standardized API response container."""
    version: str = Field(default_factory=get_contracts_version)
    status_code: int = 200
    results: List[T] = Field(default_factory=list)
    errors: List[Error] = Field(default_factory=list)

class MCPResponse(BaseModel):
    """Wrapper for MCP responses that standardizes the client interface."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    status_code: int = 200
    
    @classmethod
    def from_api_response(cls, api_response: Dict[str, Any], status_code: int = 200) -> 'MCPResponse':
        """Create MCPResponse from standardized ApiResponse dictionary."""
        try:
            if api_response.get('errors'):
                error_messages = [error.get('message', 'Unknown error') for error in api_response['errors']]
                return cls(
                    success=False, 
                    error='; '.join(error_messages),
                    status_code=api_response.get('status_code', status_code)
                )
            results = api_response.get('results', [])
            return cls(
                success=True, 
                data=results[0] if len(results) == 1 else results,
                status_code=api_response.get('status_code', status_code)
            )
        except (KeyError, TypeError, IndexError) as e:
            return cls(
                success=False, 
                error=f"Failed to parse API response: {e}",
                status_code=status_code
            )

# --- Address Schemas ---
class AddressBase(BaseModel):
    postcode: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    address_line_3: Optional[str] = None
    address_line_4: Optional[str] = None
    county: Optional[str] = None
    country: Optional[str] = 'UK'

class AddressCreate(AddressBase):
    pass

class Address(AddressBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# --- Location Schemas ---  
class LocationBase(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class LocationCreate(LocationBase):
    address: Optional[AddressCreate] = None

class Location(LocationBase):
    id: int
    address: Optional[Address] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# --- Image Schemas ---
class ImageBase(BaseModel):
    url: str
    filename: Optional[str] = None
    alt_text: Optional[str] = None
    agent_reference: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    original_width: Optional[int] = None
    original_height: Optional[int] = None
    original_content_type: Optional[str] = None

class ImageCreateNested(ImageBase):
    image_data: Optional[bytes] = None # Base64 encoded

    @field_serializer('image_data')
    def serialize_image_data(self, image_data: bytes, _info):
        if image_data:
            return base64.b64encode(image_data).decode('utf-8')
        return None

class Image(ImageBase):
    id: int
    listing_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    image_data: Optional[bytes] = None # Base64 encoded

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('image_data')
    def serialize_image_data(self, image_data: bytes, _info):
        if image_data:
            return base64.b64encode(image_data).decode('utf-8')
        return None

class ImageCreate(ImageBase):
    listing_id: Optional[int] = None
    image_data: Optional[str] = None # Base64 encoded

# --- Floorplan Schemas ---
class FloorplanBase(BaseModel):
    url: str
    filename: Optional[str] = None
    alt_text: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    original_width: Optional[int] = None
    original_height: Optional[int] = None
    original_content_type: Optional[str] = None
    agent_reference: Optional[str] = None

class FloorplanCreate(FloorplanBase):
    listing_id: Optional[int] = None
    image_data: Optional[str] = None # Base64 encoded

class FloorplanCreateNested(FloorplanBase):
    image_data: Optional[str] = None # Base64 encoded

class Floorplan(FloorplanBase):
    id: int
    listing_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    image_data: Optional[bytes] = None # Base64 encoded

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('image_data')
    def serialize_image_data(self, image_data: bytes, _info):
        if image_data:
            return base64.b64encode(image_data).decode('utf-8')
        return None

# --- EstateAgent Schemas ---
class EstateAgentBase(BaseModel):
    name: str
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    base_url: Optional[str] = None
    search_endpoint: Optional[str] = None
    api_client_type: Optional[ClientType] = None
    web_client_type: Optional[ClientType] = None

class EstateAgentCreate(EstateAgentBase):
    address: Optional[AddressCreate] = None

class EstateAgent(EstateAgentBase):
    id: int
    address: Optional[Address] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# --- Listing Schemas ---
class ListingBase(BaseModel):
    title: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None
    property_type: Optional[PropertyType] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    reception_rooms: Optional[int] = None
    council_tax_band: Optional[str] = None
    tenancy: Optional[TenancyType] = None
    annual_service_charge: Optional[float] = None
    lease_years: Optional[int] = None
    epc_rating: Optional[str] = None
    agent_reference: Optional[str] = None
    external_url: Optional[str] = None
    agency_url: Optional[str] = None
    vox_number: Optional[str] = None
    property_tags: Optional[str] = None
    is_active: bool = True
    
class ListingUpdate(ListingBase):
    location: Optional[LocationCreate] = None
    images: Optional[List[ImageCreateNested]] = None
    floorplans: Optional[List[FloorplanCreateNested]] = None
    estate_agent_id: Optional[int] = None

class ListingCreate(ListingUpdate):
    estate_agent_id: int

class Listing(ListingBase):
    id: int
    first_seen: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    location: Optional[Location] = None
    estate_agent: Optional[EstateAgent] = None
    images: List[Image] = Field(default_factory=list)
    floorplans: List[Floorplan] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class ListingSummary(ListingBase):
    id: int
    first_seen: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    location: Optional[Location] = None
    estate_agent: Optional[EstateAgent] = None
    
    model_config = ConfigDict(from_attributes=True)


# --- API Response Schemas ---
class PaginatedResponse(BaseModel, Generic[TypeVar("T")]):
    """A standardized paginated API response container."""
    version: str = Field(default_factory=get_contracts_version)
    status_code: int = 200
    results: List[T] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 10
    total_pages: int = 0
    errors: List[Error] = Field(default_factory=list)
