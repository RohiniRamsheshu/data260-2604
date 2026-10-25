from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DocumentStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"


class DocumentCategory(str, Enum):
    dependency = "dependency"
    application = "application"
    infrastructure = "infrastructure"


class VulnerabilityDocumentCreate(BaseModel):
    package_name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    status: DocumentStatus = DocumentStatus.open
    category: DocumentCategory
    discovered_at: datetime
    cve_id: Optional[str] = Field(default=None, max_length=50)


class VulnerabilityDocumentUpdate(BaseModel):
    package_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    status: Optional[DocumentStatus] = None
    category: Optional[DocumentCategory] = None
    discovered_at: Optional[datetime] = None
    cve_id: Optional[str] = Field(default=None, max_length=50)


class VulnerabilityDocumentResponse(VulnerabilityDocumentCreate):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
