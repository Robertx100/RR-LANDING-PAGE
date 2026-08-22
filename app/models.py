from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base

class ContactSubmission(Base):
    __tablename__ = "contact_submissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(200), nullable=False, index=True)
    link = Column(String, nullable=False)
    
    # Optional consultation fields
    constraint = Column(Text, nullable=True)
    fix_attempt = Column(Text, nullable=True)
    performance_gap = Column(Text, nullable=True)
    impact_bottleneck = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (UniqueConstraint('email', name='_user_email_uc'),)
