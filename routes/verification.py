"""
Resident verification endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from schemas import VerificationRequest, RedeemInviteRequest, VerificationResponse
from models import User, ResidentVerification, InviteCode, Role
from database import get_db
from dependencies import get_current_user

router = APIRouter()


@router.post("/request", response_model=VerificationResponse)
async def request_verification(
    req: VerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request verification by specified method"""
    # Create verification record
    verification = ResidentVerification(
        user_id=current_user.id,
        method=req.method,
        status="pending"
    )
    
    db.add(verification)
    db.commit()
    db.refresh(verification)
    
    return verification


@router.post("/redeem-invite")
async def redeem_invite(
    req: RedeemInviteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Redeem an invite code to verify residency"""
    # Find the invite code
    invite = db.query(InviteCode).filter(InviteCode.code == req.code).first()
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite code not found"
        )
    
    # Check if already used
    if invite.used_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite code already used"
        )
    
    # Check if expired
    if invite.expires_at and datetime.utcnow() > invite.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite code expired"
        )
    
    # Mark invite as used
    invite.used_by = current_user.id
    invite.used_at = datetime.utcnow()
    
    # Update user role to resident_verified
    verified_role = db.query(Role).filter(Role.name == "resident_verified").first()
    if verified_role:
        current_user.role_id = verified_role.id
    
    db.commit()
    
    return {"message": "Invite code redeemed successfully", "verified": True}
