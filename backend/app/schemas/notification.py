from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.notification import NotificationType, NotificationPriority


class NotificationCreate(BaseModel):
    user_id: UUID
    notification_type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None


class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    notification_type: NotificationType
    title: str
    message: str
    priority: NotificationPriority
    is_read: bool
    read_at: Optional[datetime]
    related_entity_type: Optional[str]
    related_entity_id: Optional[UUID]
    created_at: datetime
    
    class Config:
        from_attributes = True
