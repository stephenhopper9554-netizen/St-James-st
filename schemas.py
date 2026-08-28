"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


# ============ Auth Schemas ============
class UserSignup(BaseModel):
    email: EmailStr
    password: str
    name: str
    address: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Verification Schemas ============
class VerificationRequest(BaseModel):
    method: str  # document | postcard | invite | third_party


class RedeemInviteRequest(BaseModel):
    code: str


class VerificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    method: str
    status: str
    submitted_at: datetime

    class Config:
        from_attributes = True


# ============ Spot Schemas ============
class SpotProperties(BaseModel):
    id: UUID
    code: Optional[str]
    street_segment: Optional[str]
    type: str
    permit_required: bool
    status: str
    created_at: datetime


class SpotGeometry(BaseModel):
    type: str = "Point"
    coordinates: list[float]  # [lon, lat]


class SpotFeature(BaseModel):
    type: str = "Feature"
    geometry: SpotGeometry
    properties: SpotProperties


class SpotCollection(BaseModel):
    type: str = "FeatureCollection"
    features: list[SpotFeature]


# ============ Reservation Schemas ============
class ReservationCreate(BaseModel):
    spot_id: UUID
    vehicle_id: UUID
    start_at: datetime
    end_at: datetime


class ReservationResponse(BaseModel):
    id: UUID
    user_id: UUID
    spot_id: UUID
    vehicle_id: UUID
    start_at: datetime
    end_at: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Vehicle Schemas ============
class VehicleCreate(BaseModel):
    plate: str
    make: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None


class VehicleResponse(BaseModel):
    id: UUID
    plate: str
    make: Optional[str]
    model: Optional[str]
    color: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
