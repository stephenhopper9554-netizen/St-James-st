"""
SQLAlchemy models for St-James-st parking app
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, GEOMETRY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    
    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String)
    phone = Column(String)
    address = Column(String)
    role_id = Column(Integer, ForeignKey("roles.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    role = relationship("Role", back_populates="users")
    vehicles = relationship("Vehicle", back_populates="user", cascade="all, delete-orphan")
    verifications = relationship("ResidentVerification", back_populates="user", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="user", cascade="all, delete-orphan")


class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plate = Column(String, nullable=False)
    make = Column(String)
    model = Column(String)
    color = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="vehicles")
    reservations = relationship("Reservation", back_populates="vehicle")


class ResidentVerification(Base):
    __tablename__ = "resident_verifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    method = Column(String, nullable=False)  # document | postcard | invite | third_party
    status = Column(String, default="pending", nullable=False)  # pending | approved | rejected
    submitted_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    review_notes = Column(Text)
    
    user = relationship("User", back_populates="verifications", foreign_keys=[user_id])
    documents = relationship("VerificationDocument", back_populates="verification", cascade="all, delete-orphan")


class VerificationDocument(Base):
    __tablename__ = "verification_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_id = Column(UUID(as_uuid=True), ForeignKey("resident_verifications.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String)
    s3_key = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    verification = relationship("ResidentVerification", back_populates="documents")


class InviteCode(Base):
    __tablename__ = "invite_codes"
    
    code = Column(String, primary_key=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    used_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    used_at = Column(DateTime)


class Spot(Base):
    __tablename__ = "spots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True)
    geom = Column(GEOMETRY("POINT", 4326))
    street_segment = Column(String)
    type = Column(String)  # curb | driveway | permit | visitor
    permit_required = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default={})
    
    status = relationship("SpotStatus", back_populates="spot", uselist=False, cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="spot")
    sensors = relationship("Sensor", back_populates="spot")


class SpotStatus(Base):
    __tablename__ = "spot_status"
    
    spot_id = Column(UUID(as_uuid=True), ForeignKey("spots.id", ondelete="CASCADE"), primary_key=True)
    status = Column(String, nullable=False)  # free | occupied | reserved | unknown
    source = Column(String)  # sensor | manual | reservation
    last_seen = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, default={})
    
    spot = relationship("Spot", back_populates="status")


class Reservation(Base):
    __tablename__ = "reservations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    spot_id = Column(UUID(as_uuid=True), ForeignKey("spots.id"), nullable=False)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    status = Column(String, default="active", nullable=False)  # active | completed | cancelled | no-show
    created_at = Column(DateTime, default=datetime.utcnow)
    payment_ref = Column(String)
    
    user = relationship("User", back_populates="reservations")
    spot = relationship("Spot", back_populates="reservations")
    vehicle = relationship("Vehicle", back_populates="reservations")


class Sensor(Base):
    __tablename__ = "sensors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spot_id = Column(UUID(as_uuid=True), ForeignKey("spots.id"), nullable=False)
    protocol = Column(String)  # mqtt | lorawan | webhook
    identifier = Column(String)
    last_heartbeat = Column(DateTime)
    metadata = Column(JSON, default={})
    
    spot = relationship("Spot", back_populates="sensors")
    events = relationship("TelemetryEvent", back_populates="sensor", cascade="all, delete-orphan")


class TelemetryEvent(Base):
    __tablename__ = "telemetry_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("sensors.id"), nullable=False)
    received_at = Column(DateTime, default=datetime.utcnow)
    payload = Column(JSON)
    
    sensor = relationship("Sensor", back_populates="events")


class EnforcementReport(Base):
    __tablename__ = "enforcement_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    officer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    spot_id = Column(UUID(as_uuid=True), ForeignKey("spots.id"))
    plate = Column(String)
    photo_s3_key = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    meta = Column(JSON, default={})
