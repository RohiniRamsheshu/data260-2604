import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ResearcherBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=5, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        if not re.match(email_pattern, value):
            raise ValueError("Invalid email format")

        return value.lower()


class ResearcherCreate(ResearcherBase):
    pass


class ResearcherResponse(ResearcherBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VulnerabilityBase(BaseModel):
    package_name: str = Field(min_length=1, max_length=255)

    cve_id: str = Field(
        pattern=r"^CVE-\d{4}-\d{4,}$"
    )

    severity: int = Field(
        default=0,
        ge=0,
        le=10
    )

    researcher_id: int = Field(gt=0)


class VulnerabilityCreate(VulnerabilityBase):
    pass


class VulnerabilityResponse(VulnerabilityBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)