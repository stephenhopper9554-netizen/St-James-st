"""
Parking spots endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from geoalchemy2 import func

from schemas import SpotCollection, SpotFeature, SpotGeometry, SpotProperties
from models import User, Spot, SpotStatus
from database import get_db
from dependencies import get_current_user

router = APIRouter()


@router.get("", response_model=SpotCollection)
async def list_spots(
    bbox: str = Query(None, description="Bounding box: minLon,minLat,maxLon,maxLat"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List parking spots with optional geospatial filtering"""
    query = db.query(Spot)
    
    # Apply bounding box filter if provided
    if bbox:
        try:
            coords = [float(x) for x in bbox.split(",")]
            if len(coords) != 4:
                raise ValueError
            min_lon, min_lat, max_lon, max_lat = coords
            
            # Use PostGIS to filter by bounding box
            query = query.filter(
                and_(
                    func.ST_X(Spot.geom) >= min_lon,
                    func.ST_X(Spot.geom) <= max_lon,
                    func.ST_Y(Spot.geom) >= min_lat,
                    func.ST_Y(Spot.geom) <= max_lat,
                )
            )
        except (ValueError, IndexError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid bbox format. Use: minLon,minLat,maxLon,maxLat"
            )
    
    spots = query.all()
    
    # Convert to GeoJSON
    features = []
    for spot in spots:
        status_record = db.query(SpotStatus).filter(SpotStatus.spot_id == spot.id).first()
        status_value = status_record.status if status_record else "unknown"
        
        # Extract coordinates from PostGIS geometry
        coords = None
        if spot.geom:
            # Get lon, lat from geometry
            result = db.query(func.ST_X(spot.geom), func.ST_Y(spot.geom)).first()
            if result:
                coords = [result[0], result[1]]
        
        feature = SpotFeature(
            geometry=SpotGeometry(coordinates=coords or [0, 0]),
            properties=SpotProperties(
                id=spot.id,
                code=spot.code,
                street_segment=spot.street_segment,
                type=spot.type,
                permit_required=spot.permit_required,
                status=status_value,
                created_at=spot.created_at
            )
        )
        features.append(feature)
    
    return SpotCollection(features=features)
