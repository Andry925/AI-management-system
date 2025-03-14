import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, field_validator, ValidationError


class UserRequestSchema(BaseModel):
    username: str = Field(min_length=10, max_length=50)
    email: EmailStr = Field(min_length=10, max_length=50)
    password: str = Field(min_length=10, max_length=50)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @field_validator('password')
    @classmethod
    def validate_password(cls, values):
        pattern = r'^(?=.*[A-Z])(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        if not bool(re.match(pattern, values)):
            raise ValidationError('Password must contain at least 8 characters')
        return values


class UserResponseSchema(BaseModel):
    username: str
    email: str
    created_at: datetime
    updated_at: datetime
