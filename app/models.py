from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Influencer(Base):
    __tablename__ = "influencers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    linkedin_url = Column(String(500), nullable=False, unique=True)
    relevance_reason = Column(Text, nullable=True)

    posts = relationship(
        "LinkedInPost",
        back_populates="influencer",
        cascade="all, delete-orphan",
    )


class LinkedInPost(Base):
    __tablename__ = "linkedin_posts"

    id = Column(Integer, primary_key=True, index=True)
    influencer_id = Column(
        Integer,
        ForeignKey("influencers.id"),
        nullable=False,
    )
    post_text = Column(Text, nullable=False)
    post_url = Column(String(500), nullable=False, unique=True)
    posted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    influencer = relationship(
        "Influencer",
        back_populates="posts",
    )

    responses = relationship(
        "GeneratedResponse",
        back_populates="post",
        cascade="all, delete-orphan",
    )


class GeneratedResponse(Base):
    __tablename__ = "generated_responses"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(
        Integer,
        ForeignKey("linkedin_posts.id"),
        nullable=False,
    )
    response_text = Column(Text, nullable=False)
    status = Column(String(50), default="draft", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    posted_at = Column(DateTime, nullable=True)

    post = relationship(
        "LinkedInPost",
        back_populates="responses",
    )