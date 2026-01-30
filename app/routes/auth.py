"""
Authentication routes for Google OAuth.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db, User, CompanyProfile, Calendar, UserInsights
from app.auth import (
    verify_google_token, 
    create_access_token, 
    get_or_create_user,
    require_auth,
    get_current_user
)
from typing import Optional, List
from datetime import datetime

router = APIRouter()


class GoogleAuthRequest(BaseModel):
    access_token: str


class AuthResponse(BaseModel):
    token: str
    user: dict


class CompanyProfileUpdate(BaseModel):
    brand_name: str
    website_url: Optional[str] = ""
    industry: str
    target_audience: str
    brand_values: str
    brand_info: str
    content_goals: str
    platform: str = "Instagram"
    tone: str = "professional"
    include_cta: bool = True
    website_summary: Optional[str] = ""


class CalendarSave(BaseModel):
    month: str
    platform: str
    posts_per_week: int
    total_posts: int
    brand_analysis: Optional[str] = ""
    strategy: Optional[str] = ""
    posts: list


class InsightsUpdate(BaseModel):
    industry_insights: Optional[str] = None
    personalized_tips: Optional[str] = None


# ============ AUTH ENDPOINTS ============

@router.post("/google", response_model=AuthResponse)
async def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Authenticate with Google OAuth token."""
    print(f"🔐 Auth request received with token: {request.access_token[:20]}...")
    
    try:
        # Verify Google token and get user info
        google_user = await verify_google_token(request.access_token)
        print(f"✅ Google user verified: {google_user.get('email')}")
        
        # Get or create user
        user = get_or_create_user(db, google_user)
        print(f"✅ User created/found: {user.email}")
        
        # Create JWT token
        token = create_access_token(user.id, user.email)
        print(f"✅ JWT token created")
        
        return {
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "picture": user.picture
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Auth error: {e}")
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@router.get("/me")
def get_current_user_info(user: User = Depends(require_auth)):
    """Get current authenticated user info."""
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "picture": user.picture,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }


# ============ COMPANY PROFILE ENDPOINTS ============

@router.get("/profile")
def get_company_profile(user: User = Depends(require_auth), db: Session = Depends(get_db)):
    """Get user's company profile."""
    profile = db.query(CompanyProfile).filter(CompanyProfile.user_id == user.id).first()
    
    if not profile:
        return None
    
    return {
        "brand_name": profile.brand_name,
        "website_url": profile.website_url,
        "industry": profile.industry,
        "target_audience": profile.target_audience,
        "brand_values": profile.brand_values,
        "brand_info": profile.brand_info,
        "content_goals": profile.content_goals,
        "platform": profile.platform,
        "tone": profile.tone,
        "include_cta": profile.include_cta,
        "website_summary": profile.website_summary
    }


@router.post("/profile")
def save_company_profile(
    data: CompanyProfileUpdate,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Save or update user's company profile."""
    profile = db.query(CompanyProfile).filter(CompanyProfile.user_id == user.id).first()
    
    if profile:
        # Update existing
        for key, value in data.dict().items():
            setattr(profile, key, value)
        profile.updated_at = datetime.utcnow()
    else:
        # Create new
        profile = CompanyProfile(user_id=user.id, **data.dict())
        db.add(profile)
    
    db.commit()
    return {"success": True, "message": "Profile saved"}


# ============ CALENDAR ENDPOINTS ============

@router.get("/calendars")
def get_user_calendars(user: User = Depends(require_auth), db: Session = Depends(get_db)):
    """Get all calendars for the user."""
    calendars = db.query(Calendar).filter(Calendar.user_id == user.id).order_by(Calendar.created_at.desc()).all()
    
    return [
        {
            "id": cal.id,
            "month": cal.month,
            "platform": cal.platform,
            "posts_per_week": cal.posts_per_week,
            "total_posts": cal.total_posts,
            "is_current": cal.is_current,
            "created_at": cal.created_at.isoformat() if cal.created_at else None,
            "brand_analysis": cal.brand_analysis,
            "strategy": cal.strategy,
            "posts": cal.posts
        }
        for cal in calendars
    ]


@router.get("/calendars/current")
def get_current_calendar(user: User = Depends(require_auth), db: Session = Depends(get_db)):
    """Get the current active calendar."""
    calendar = db.query(Calendar).filter(
        Calendar.user_id == user.id,
        Calendar.is_current == True
    ).first()
    
    if not calendar:
        return None
    
    return {
        "id": calendar.id,
        "month": calendar.month,
        "platform": calendar.platform,
        "posts_per_week": calendar.posts_per_week,
        "total_posts": calendar.total_posts,
        "brand_analysis": calendar.brand_analysis,
        "strategy": calendar.strategy,
        "posts": calendar.posts,
        "created_at": calendar.created_at.isoformat() if calendar.created_at else None
    }


@router.post("/calendars")
def save_calendar(
    data: CalendarSave,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Save a new calendar (marks previous as not current)."""
    # Mark all previous calendars as not current
    db.query(Calendar).filter(Calendar.user_id == user.id).update({"is_current": False})
    
    # Create new calendar
    calendar = Calendar(
        user_id=user.id,
        month=data.month,
        platform=data.platform,
        posts_per_week=data.posts_per_week,
        total_posts=data.total_posts,
        brand_analysis=data.brand_analysis,
        strategy=data.strategy,
        posts=data.posts,
        is_current=True
    )
    db.add(calendar)
    db.commit()
    db.refresh(calendar)
    
    return {"success": True, "calendar_id": calendar.id}


@router.put("/calendars/{calendar_id}")
def update_calendar(
    calendar_id: int,
    data: CalendarSave,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Update an existing calendar (e.g., when marking posts as done)."""
    calendar = db.query(Calendar).filter(
        Calendar.id == calendar_id,
        Calendar.user_id == user.id
    ).first()
    
    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")
    
    calendar.posts = data.posts
    calendar.brand_analysis = data.brand_analysis
    calendar.strategy = data.strategy
    db.commit()
    
    return {"success": True}


# ============ INSIGHTS ENDPOINTS ============

@router.get("/insights")
def get_user_insights(user: User = Depends(require_auth), db: Session = Depends(get_db)):
    """Get user's saved insights and tips."""
    insights = db.query(UserInsights).filter(UserInsights.user_id == user.id).first()
    
    if not insights:
        return {"industry_insights": None, "personalized_tips": None}
    
    return {
        "industry_insights": insights.industry_insights,
        "personalized_tips": insights.personalized_tips,
        "insights_updated_at": insights.insights_updated_at.isoformat() if insights.insights_updated_at else None,
        "tips_updated_at": insights.tips_updated_at.isoformat() if insights.tips_updated_at else None
    }


@router.post("/insights")
def save_user_insights(
    data: InsightsUpdate,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Save user's insights and tips."""
    insights = db.query(UserInsights).filter(UserInsights.user_id == user.id).first()
    
    if not insights:
        insights = UserInsights(user_id=user.id)
        db.add(insights)
    
    if data.industry_insights is not None:
        insights.industry_insights = data.industry_insights
        insights.insights_updated_at = datetime.utcnow()
    
    if data.personalized_tips is not None:
        insights.personalized_tips = data.personalized_tips
        insights.tips_updated_at = datetime.utcnow()
    
    db.commit()
    return {"success": True}
