from pydantic import BaseModel, Field, validator
from datetime import datetime

class NewsItem(BaseModel):
    headline: str = Field(..., description="The news headline")
    priority: int = Field(..., description="Priority level: 1 (High), 2 (Medium), 3 (Low)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Time of emission")
    retry_count: int = 0 

    @validator('priority')
    def validate_priority(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError('Priority must be 1, 2, or 3')
        return v
