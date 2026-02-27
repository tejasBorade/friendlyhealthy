"""
API Routes for Medicine Favorites
Sprint 1.2: Templates & Favorites
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.doctor import Doctor
from app.models.prescription_extras import DoctorMedicineFavorite
from app.schemas.template import (
    MedicineFavoriteCreate,
    MedicineFavoriteUpdate,
    MedicineFavoriteResponse,
    MedicineFavoriteListResponse
)
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/favorites", tags=["Medicine Favorites"])


@router.post("", response_model=MedicineFavoriteResponse, status_code=status.HTTP_201_CREATED)
async def create_favorite(
    favorite_data: MedicineFavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a medicine to favorites (Doctor only).
    
    Favorites allow quick access to frequently prescribed medicines.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create favorites"
        )
    
    # Get doctor
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Create favorite
    favorite = DoctorMedicineFavorite(
        doctor_id=doctor.id,
        medicine_name=favorite_data.medicine_name,
        dosage=favorite_data.dosage,
        frequency=favorite_data.frequency,
        usage_instructions=favorite_data.usage_instructions,
        duration_days=favorite_data.duration_days,
        category=favorite_data.category,
        usage_count=0
    )
    
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    
    return favorite


@router.get("", response_model=MedicineFavoriteListResponse)
async def get_favorites(
    search: Optional[str] = Query(None, description="Search by medicine name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all medicine favorites for the current doctor.
    
    Supports search and pagination. Sorted by usage count (most used first).
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can view favorites"
        )
    
    # Get doctor
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Build query
    query = select(DoctorMedicineFavorite).where(
        DoctorMedicineFavorite.doctor_id == doctor.id
    )
    
    # Apply filters
    if search:
        query = query.where(
            DoctorMedicineFavorite.medicine_name.ilike(f"%{search}%")
        )
    
    if category:
        query = query.where(DoctorMedicineFavorite.category == category)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(
        DoctorMedicineFavorite.usage_count.desc(),
        DoctorMedicineFavorite.medicine_name
    )
    query = query.offset(offset).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    favorites = result.scalars().all()
    
    return MedicineFavoriteListResponse(
        favorites=favorites,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/search", response_model=List[MedicineFavoriteResponse])
async def search_favorites(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Quick search favorites while typing (autocomplete).
    
    Returns top matches by usage count.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can search favorites"
        )
    
    # Get doctor
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Search query
    query = (
        select(DoctorMedicineFavorite)
        .where(
            DoctorMedicineFavorite.doctor_id == doctor.id,
            DoctorMedicineFavorite.medicine_name.ilike(f"%{q}%")
        )
        .order_by(
            DoctorMedicineFavorite.usage_count.desc(),
            DoctorMedicineFavorite.medicine_name
        )
        .limit(limit)
    )
    
    result = await db.execute(query)
    favorites = result.scalars().all()
    
    return favorites


@router.get("/{favorite_id}", response_model=MedicineFavoriteResponse)
async def get_favorite(
    favorite_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific favorite by ID."""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can view favorites"
        )
    
    # Get doctor
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Get favorite
    result = await db.execute(
        select(DoctorMedicineFavorite).where(
            DoctorMedicineFavorite.id == favorite_id,
            DoctorMedicineFavorite.doctor_id == doctor.id
        )
    )
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
    
    return favorite


@router.put("/{favorite_id}", response_model=MedicineFavoriteResponse)
async def update_favorite(
    favorite_id: UUID,
    favorite_data: MedicineFavoriteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a favorite medicine."""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can update favorites"
        )
    
    # Get doctor
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Get favorite
    result = await db.execute(
        select(DoctorMedicineFavorite).where(
            DoctorMedicineFavorite.id == favorite_id,
            DoctorMedicineFavorite.doctor_id == doctor.id
        )
    )
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
    
    # Update fields
    if favorite_data.medicine_name is not None:
        favorite.medicine_name = favorite_data.medicine_name
    if favorite_data.dosage is not None:
        favorite.dosage = favorite_data.dosage
    if favorite_data.frequency is not None:
        favorite.frequency = favorite_data.frequency
    if favorite_data.usage_instructions is not None:
        favorite.usage_instructions = favorite_data.usage_instructions
    if favorite_data.duration_days is not None:
        favorite.duration_days = favorite_data.duration_days
    if favorite_data.category is not None:
        favorite.category = favorite_data.category
    
    await db.commit()
    await db.refresh(favorite)
    
    return favorite


@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite(
    favorite_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a favorite medicine."""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can delete favorites"
        )
    
    # Get doctor
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Get favorite
    result = await db.execute(
        select(DoctorMedicineFavorite).where(
            DoctorMedicineFavorite.id == favorite_id,
            DoctorMedicineFavorite.doctor_id == doctor.id
        )
    )
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
    
    await db.delete(favorite)
    await db.commit()
    
    return None


@router.post("/{favorite_id}/use")
async def use_favorite(
    favorite_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Increment usage count for a favorite.
    
    Called when this favorite is used in a prescription.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can use favorites"
        )
    
    # Get doctor
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Get favorite
    result = await db.execute(
        select(DoctorMedicineFavorite).where(
            DoctorMedicineFavorite.id == favorite_id,
            DoctorMedicineFavorite.doctor_id == doctor.id
        )
    )
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
    
    favorite.usage_count += 1
    await db.commit()
    
    return {"success": True, "usage_count": favorite.usage_count}


@router.get("/categories/list")
async def get_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of all categories used by the doctor.
    
    Useful for filtering favorites by category.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can view categories"
        )
    
    # Get doctor
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Get unique categories
    query = (
        select(DoctorMedicineFavorite.category)
        .where(
            DoctorMedicineFavorite.doctor_id == doctor.id,
            DoctorMedicineFavorite.category.isnot(None)
        )
        .distinct()
        .order_by(DoctorMedicineFavorite.category)
    )
    
    result = await db.execute(query)
    categories = [row[0] for row in result.all()]
    
    return {"categories": categories}
