"""
Parking reservations endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from schemas import ReservationCreate, ReservationResponse
from models import User, Reservation, Spot, Vehicle
from database import get_db
from dependencies import get_current_user

router = APIRouter()


@router.post("", response_model=ReservationResponse, status_code=201)
async def create_reservation(
    reservation_data: ReservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new parking reservation (verified residents only)"""
    # Check if user is verified
    if not current_user.role or current_user.role.name != "resident_verified":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only verified residents can create reservations"
        )
    
    # Verify spot exists
    spot = db.query(Spot).filter(Spot.id == reservation_data.spot_id).first()
    if not spot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spot not found"
        )
    
    # Verify vehicle belongs to user
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == reservation_data.vehicle_id,
        Vehicle.user_id == current_user.id
    ).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found or does not belong to you"
        )
    
    # Verify no conflicting reservations
    conflict = db.query(Reservation).filter(
        Reservation.spot_id == reservation_data.spot_id,
        Reservation.status == "active",
        Reservation.start_at < reservation_data.end_at,
        Reservation.end_at > reservation_data.start_at
    ).first()
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Spot is already reserved for this time period"
        )
    
    # Create reservation
    reservation = Reservation(
        user_id=current_user.id,
        spot_id=reservation_data.spot_id,
        vehicle_id=reservation_data.vehicle_id,
        start_at=reservation_data.start_at,
        end_at=reservation_data.end_at,
        status="active"
    )
    
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    
    return reservation
