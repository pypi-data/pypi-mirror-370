"""
Pydantic schemas for the Listings DB API.

These schemas define the data shape for API requests and responses,
ensuring type validation and serialization are handled correctly by FastAPI.
They are based on the database models but are decoupled to provide a stable
public interface for the API.
"""
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

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
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# --- Location Schemas ---
class LocationBase(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class LocationCreate(LocationBase):
    address: Optional[AddressCreate] = None

class Location(LocationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    address: Optional[Address] = None
    
    model_config = ConfigDict(from_attributes=True)


# --- Image Schemas ---
class ImageBase(BaseModel):
    url: str
    filename: Optional[str] = None
    alt_text: Optional[str] = None
    agent_reference: Optional[str] = None
    listing_id: int
    original_image_id: int

class ImageCreate(ImageBase):
    pass

class Image(ImageBase):
    id: int
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    original_width: Optional[int] = None
    original_height: Optional[int] = None
    original_content_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    image_analysis: Optional[str] = None
    image_data: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

class ImageWithData(Image):
    image_data_base64: Optional[str] = None # Base64 encoded

# Schema for creating an image with image data
class ImageCreateWithData(BaseModel):
    url: str
    filename: Optional[str] = None
    alt_text: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    image_data: Optional[str] = None  # Base64 encoded string
    original_width: Optional[int] = None
    original_height: Optional[int] = None
    original_content_type: Optional[str] = None
    agent_reference: Optional[str] = None

# Schema for creating an image nested within a listing request
class ImageCreateNested(BaseModel):
    url: str
    filename: Optional[str] = None
    alt_text: Optional[str] = None
    agent_reference: Optional[str] = None
    image_analysis: Optional[str] = None
    image_data: Optional[str] = None
    original_image_id: Optional[int] = None

# --- Floorplan Schemas ---
class FloorplanBase(BaseModel):
    url: str
    filename: Optional[str] = None
    alt_text: Optional[str] = None
    agent_reference: Optional[str] = None
    listing_id: int
    original_floorplan_id: Optional[int] = None
    image_analysis: Optional[str] = None
    image_data: Optional[str] = None

class FloorplanCreate(FloorplanBase):
    pass

class Floorplan(FloorplanBase):
    id: int
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    original_width: Optional[int] = None
    original_height: Optional[int] = None
    original_content_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    image_analysis: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class FloorplanWithData(Floorplan):
    image_data_base64: Optional[str] = None # Base64 encoded

# Schema for creating a floorplan with image data
class FloorplanCreateWithData(BaseModel):
    url: str
    filename: Optional[str] = None
    alt_text: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    image_data: Optional[str] = None  # Base64 encoded string
    original_width: Optional[int] = None
    original_height: Optional[int] = None
    original_content_type: Optional[str] = None
    agent_reference: Optional[str] = None

# Schema for creating a floorplan nested within a listing request
class FloorplanCreateNested(BaseModel):
    url: str
    filename: Optional[str] = None
    alt_text: Optional[str] = None
    agent_reference: Optional[str] = None
    image_analysis: Optional[str] = None
    image_data: Optional[str] = None
    original_floorplan_id: Optional[int] = None


# --- EstateAgent Schemas ---
class EstateAgentBase(BaseModel):
    name: str
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    base_url: Optional[str] = None
    search_endpoint: Optional[str] = None
    api_client_type: Optional[str] = None
    web_client_type: Optional[str] = None

class EstateAgentCreate(EstateAgentBase):
    address: Optional[AddressCreate] = None

class EstateAgent(EstateAgentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    address: Optional[Address] = None

    model_config = ConfigDict(from_attributes=True)


# --- Listing Schemas ---
class ListingBase(BaseModel):
    title: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    description_analysis: Optional[str] = None
    price: Optional[float] = None
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    reception_rooms: Optional[int] = None
    council_tax_band: Optional[str] = None
    tenancy: Optional[str] = None
    annual_service_charge: Optional[float] = None
    lease_years: Optional[int] = None
    epc_rating: Optional[str] = None
    agent_reference: Optional[str] = None
    external_url: Optional[str] = None
    agency_url: Optional[str] = None
    vox_number: Optional[str] = None
    property_tags: Optional[str] = None # Must be a string for the DB
    is_active: bool = True
    estate_agent_id: Optional[int] = None

class ListingUpdate(ListingBase):
    location: Optional[LocationCreate] = None
    images: Optional[List[ImageCreateNested]] = None
    floorplans: Optional[List[FloorplanCreateNested]] = None

class ListingCreate(ListingUpdate):
    estate_agent_id: int

class Listing(ListingBase):
    id: int
    first_seen: datetime
    last_updated: datetime
    created_at: datetime
    updated_at: datetime
    location: Optional[Location] = None
    estate_agent: Optional[EstateAgent] = None
    images: List[Image] = []
    floorplans: List[Floorplan] = []

    model_config = ConfigDict(from_attributes=True)

class ListingWithImages(ListingBase):
    id: int
    first_seen: datetime
    last_updated: datetime
    created_at: datetime
    updated_at: datetime
    location: Optional[Location] = None
    estate_agent: Optional[EstateAgent] = None
    images: List[Image] = []
    floorplans: List[Floorplan] = []

    model_config = ConfigDict(from_attributes=True) 


# --- Prompt Schemas ---
class PromptBase(BaseModel):
    name: str
    prompt: str
    version: int = 1

class PromptCreate(PromptBase):
    pass

class Prompt(PromptBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# --- Enrichment Orchestration Schemas ---

# Description Analytics Schemas
class DescriptionAnalyticsRunBase(BaseModel):
    description_output: Optional[str] = None
    description: Optional[str] = None
    original_listing_id: Optional[int] = None
    enriched_listing_id: Optional[int] = None
    model: Optional[str] = None
    temperature: Optional[str] = None
    prompt_id: Optional[int] = None

class DescriptionAnalyticsRunCreate(DescriptionAnalyticsRunBase):
    timestamp: Optional[datetime] = None

class DescriptionAnalyticsRun(DescriptionAnalyticsRunBase):
    id: int
    timestamp: datetime
    enrichment_orchestration_run_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    prompt: Optional[Prompt] = None
    
    model_config = ConfigDict(from_attributes=True)

# Image Analytics Schemas  
class ImageAnalyticsRunBase(BaseModel):
    image_data: Optional[str] = None
    image_analytics_output: Optional[str] = None
    original_image_id: Optional[int] = None
    enriched_image_id: Optional[int] = None
    model: Optional[str] = None
    temperature: Optional[str] = None
    settings_json: Optional[str] = None
    prompt_id: Optional[int] = None
    enrichment_orchestration_run_id: Optional[int] = None

class ImageAnalyticsRunCreate(ImageAnalyticsRunBase):
    timestamp: Optional[datetime] = None

class ImageAnalyticsRun(ImageAnalyticsRunBase):
    id: int
    timestamp: datetime
    created_at: datetime
    updated_at: datetime
    prompt: Optional[Prompt] = None
    model_config = ConfigDict(from_attributes=True)

# Floorplan Analytics Schemas
class FloorplanAnalyticsRunBase(BaseModel):
    image_data: Optional[str] = None
    image_analytics_output: Optional[str] = None
    original_floorplan_id: Optional[int] = None
    enriched_floorplan_id: Optional[int] = None
    model: Optional[str] = None
    temperature: Optional[str] = None
    settings_json: Optional[str] = None
    prompt_id: Optional[int] = None

class FloorplanAnalyticsRunCreate(FloorplanAnalyticsRunBase):
    timestamp: Optional[datetime] = None

class FloorplanAnalyticsRun(FloorplanAnalyticsRunBase):
    id: int
    timestamp: datetime
    enrichment_orchestration_run_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    prompt: Optional[Prompt] = None
    
    model_config = ConfigDict(from_attributes=True)

# Orchestration Run Schemas
class EnrichmentOrchestrationRunBase(BaseModel):
    enrichment_orchestration_set_id: int
    run_sequence_number: int
    original_listing_id: Optional[int] = None
    enriched_listing_id: Optional[int] = None

class EnrichmentOrchestrationRunCreate(EnrichmentOrchestrationRunBase):
    timestamp: Optional[datetime] = None
    description_analytics: Optional[DescriptionAnalyticsRunCreate] = None
    image_analytics: Optional[List[ImageAnalyticsRunCreate]] = None
    floorplan_analytics: Optional[List[FloorplanAnalyticsRunCreate]] = None

class EnrichmentOrchestrationRun(EnrichmentOrchestrationRunBase):
    id: int
    timestamp: datetime
    created_at: datetime
    updated_at: datetime
    description_analytics: Optional[DescriptionAnalyticsRun] = None
    image_analytics: List[ImageAnalyticsRun] = []
    floorplan_analytics: List[FloorplanAnalyticsRun] = []
    
    model_config = ConfigDict(from_attributes=True)

# Orchestration Set Schemas
class EnrichmentOrchestrationSetBase(BaseModel):
    pass

class EnrichmentOrchestrationSetCreate(EnrichmentOrchestrationSetBase):
    timestamp: Optional[datetime] = None
    orchestration_runs: Optional[List[EnrichmentOrchestrationRunCreate]] = None

class EnrichmentOrchestrationSet(EnrichmentOrchestrationSetBase):
    id: int
    timestamp: datetime
    created_at: datetime
    updated_at: datetime
    orchestration_runs: List[EnrichmentOrchestrationRun] = []
    
    model_config = ConfigDict(from_attributes=True) 