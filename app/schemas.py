from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class InfluencerBase(BaseModel):
    name: str
    title: Optional[str] = None
    company: Optional[str] = None
    linkedin_url: str
    relevance_reason: Optional[str] = None


class InfluencerCreate(InfluencerBase):
    pass


class InfluencerRead(InfluencerBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class LinkedInPostBase(BaseModel):
    influencer_id: int
    post_text: str
    post_url: str
    posted_at: Optional[datetime] = None


class LinkedInPostCreate(LinkedInPostBase):
    pass


class LinkedInPostRead(LinkedInPostBase):
    id: int
    created_at: datetime
    influencer: Optional[InfluencerRead] = None

    model_config = ConfigDict(from_attributes=True)


class GeneratedResponseCreate(BaseModel):
    post_id: int
    response_text: str
    status: str = "draft"


class GeneratedResponseRead(BaseModel):
    id: int
    post_id: int
    response_text: str
    status: str
    created_at: datetime
    posted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)