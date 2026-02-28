from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime
from app.core.database import get_db
from app.models.notification import Notification
from app.models.user import User, UserRole
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class NotificationBase(BaseModel):
    user_id: int
    notification_type: str = Field(..., max_length=50)
    title: str = Field(..., max_length=200)
    message: str
    priority: str | None = Field(None, max_length=20)
    send_via: str | None = Field(None, max_length=20)


class NotificationCreate(NotificationBase):
    pass


class NotificationResponse(NotificationBase):
    id: int
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UnreadCountResponse(BaseModel):
    count: int


@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    is_read: bool | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's notifications."""
    query = select(Notification).where(Notification.user_id == current_user.id)
    
    if is_read is not None:
        query = query.where(Notification.is_read == is_read)
    
    query = query.offset(skip).limit(limit).order_by(Notification.created_at.desc())
    
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    return notifications


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get count of unread notifications."""
    result = await db.execute(
        select(func.count()).select_from(Notification).where(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        )
    )
    count = result.scalar()
    
    return {"count": count}


@router.patch("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark notification as read."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_read = True
    await db.commit()
    
    return {"message": "Notification marked as read"}


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: NotificationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a notification (Admin/System only)."""
    if current_user.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    notification = Notification(**notification_data.model_dump())
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    
    return notification
