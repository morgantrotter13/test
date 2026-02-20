"""
Database models and setup for user accounts and content storage.
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./social_planner.db")

# Handle PostgreSQL URL format from Railway/Heroku
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite needs special connect_args, PostgreSQL doesn't
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255))
    picture = Column(String(500))  # Google profile picture URL
    google_id = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)
    
    # Stripe subscription fields
    stripe_customer_id = Column(String(255), unique=True, nullable=True)
    is_subscribed = Column(Boolean, default=False)
    subscription_status = Column(String(50), default="none")  # none, active, cancelled, past_due
    subscription_plan = Column(String(50), nullable=True)  # growth
    subscription_end = Column(DateTime, nullable=True)
    
    # Relationships
    company_profile = relationship("CompanyProfile", back_populates="user", uselist=False)
    calendars = relationship("Calendar", back_populates="user", order_by="desc(Calendar.created_at)")
    insights = relationship("UserInsights", back_populates="user", uselist=False)


class CompanyProfile(Base):
    """Company profile for a user."""
    __tablename__ = "company_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    brand_name = Column(String(255))
    website_url = Column(String(500))
    industry = Column(String(255))
    target_audience = Column(Text)
    brand_values = Column(Text)
    brand_info = Column(Text)
    content_goals = Column(Text)
    platform = Column(String(50), default="Instagram")
    tone = Column(String(50), default="professional")
    include_cta = Column(Boolean, default=True)
    website_summary = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="company_profile")


class Calendar(Base):
    """Generated content calendar."""
    __tablename__ = "calendars"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    month = Column(String(50))  # e.g., "February 2026"
    platform = Column(String(50))
    posts_per_week = Column(Integer)
    total_posts = Column(Integer)
    
    # Store full calendar data as JSON
    brand_analysis = Column(Text)
    strategy = Column(Text)
    posts = Column(JSON)  # List of post objects
    
    is_current = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="calendars")


class UserInsights(Base):
    """Stored industry insights and tips for a user."""
    __tablename__ = "user_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    industry_insights = Column(Text)
    personalized_tips = Column(Text)
    insights_updated_at = Column(DateTime)
    tips_updated_at = Column(DateTime)
    
    user = relationship("User", back_populates="insights")


# Create all tables
def init_db():
    Base.metadata.create_all(bind=engine)


# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize database on import
init_db()
