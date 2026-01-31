"""
Content generation and planning routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.prompt_engine.backend.brain import run_brain
from app.prompt_engine.backend.content_planner import (
    generate_content_calendar,
    research_industry_trends,
    generate_tips
)
from app.prompt_engine.backend.website_scraper import (
    scrape_website,
    summarize_website_for_prompts
)
from app.database import get_db, User
from app.auth import get_user_from_token


router = APIRouter()


# Constants for post limits
FREE_POST_LIMIT = 1
STARTER_MONTHLY_LIMIT = 4
PRO_LIMIT = float('inf')  # Unlimited


def get_current_month():
    """Get current month string for tracking resets."""
    return datetime.utcnow().strftime("%Y-%m")


def check_and_reset_monthly_count(user: User, db: Session):
    """Reset post count if it's a new month."""
    current_month = get_current_month()
    if user.post_count_reset_month != current_month:
        user.posts_generated_this_month = 0
        user.post_count_reset_month = current_month
        db.commit()


class CompanyProfile(BaseModel):
    brand_name: str
    industry: str
    target_audience: str
    brand_values: str
    brand_info: str
    content_goals: str
    platform: str
    tone: Optional[str] = "professional"
    include_cta: Optional[bool] = True
    website_url: Optional[str] = ""
    website_summary: Optional[str] = ""


class WebsiteRequest(BaseModel):
    url: str


class ContentRequest(BaseModel):
    brand_name: str
    industry: str
    target_audience: str
    brand_values: str
    brand_info: str
    content_goals: str
    platform: str
    post_frequency: str
    content_themes: str
    post_topic: str
    tone: str
    post_type: str
    include_cta: bool


class CalendarRequest(BaseModel):
    brand_name: str
    industry: str
    target_audience: str
    brand_values: str
    brand_info: str
    content_goals: str
    platform: str
    tone: Optional[str] = "professional"
    include_cta: Optional[bool] = True
    posts_per_week: Optional[int] = 3
    website_url: Optional[str] = ""
    website_summary: Optional[str] = ""
    # Monthly context
    monthly_promotions: Optional[str] = ""
    monthly_events: Optional[str] = ""
    monthly_focuses: Optional[str] = ""
    past_themes: Optional[list] = []
    feedback: Optional[str] = ""  # User feedback for regeneration
    industry_insights: Optional[str] = ""  # Saved industry insights
    personalized_tips: Optional[str] = ""  # Saved personalized tips


@router.post("/scrape-website")
def scrape_website_endpoint(request: WebsiteRequest):
    """Scrape a website to extract business information and infer company profile."""
    from app.prompt_engine.backend.website_scraper import infer_company_profile
    
    scraped_data = scrape_website(request.url)
    summary = summarize_website_for_prompts(scraped_data)
    
    # Use AI to infer company profile from scraped data
    inferred_profile = {}
    if scraped_data.get("scraped_successfully"):
        inferred_profile = infer_company_profile(scraped_data)
    
    return {
        "url": request.url,
        "scraped_successfully": scraped_data.get("scraped_successfully", False),
        "tagline": scraped_data.get("tagline", ""),
        "description": scraped_data.get("description", ""),
        "about": scraped_data.get("about", "")[:500],
        "summary": summary,
        "key_phrases": scraped_data.get("key_phrases", []),
        "inferred_profile": inferred_profile
    }


@router.get("/post-usage")
def get_post_usage(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get user's post usage and limits."""
    if not authorization:
        # Not logged in - show free post status from localStorage
        return {
            "can_generate": True,  # Frontend will track free post
            "posts_used": 0,
            "posts_limit": 1,
            "posts_remaining": 1,
            "plan": "free",
            "message": "1 free post available"
        }
    
    # Get user from token
    token = authorization.replace("Bearer ", "")
    user = get_user_from_token(token, db)
    
    if not user:
        return {"can_generate": True, "posts_used": 0, "posts_limit": 1, "plan": "free"}
    
    # Reset count if new month
    check_and_reset_monthly_count(user, db)
    
    # Determine limits based on subscription
    if user.subscription_plan == "pro":
        return {
            "can_generate": True,
            "posts_used": user.posts_generated_this_month,
            "posts_limit": -1,  # Unlimited
            "posts_remaining": -1,
            "plan": "pro",
            "message": "Unlimited posts"
        }
    elif user.subscription_plan == "starter":
        remaining = STARTER_MONTHLY_LIMIT - user.posts_generated_this_month
        return {
            "can_generate": remaining > 0,
            "posts_used": user.posts_generated_this_month,
            "posts_limit": STARTER_MONTHLY_LIMIT,
            "posts_remaining": max(0, remaining),
            "plan": "starter",
            "message": f"{remaining} of {STARTER_MONTHLY_LIMIT} posts remaining this month"
        }
    else:
        # Free user
        return {
            "can_generate": not user.free_post_used,
            "posts_used": 1 if user.free_post_used else 0,
            "posts_limit": FREE_POST_LIMIT,
            "posts_remaining": 0 if user.free_post_used else 1,
            "plan": "free",
            "free_post_used": user.free_post_used,
            "message": "Free post used" if user.free_post_used else "1 free post available"
        }


@router.post("/generate")
def generate_content(
    request: ContentRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Generate a single social media post using AI."""
    user = None
    
    # Check if user is authenticated
    if authorization:
        token = authorization.replace("Bearer ", "")
        user = get_user_from_token(token, db)
    
    # Check limits if user exists
    if user:
        check_and_reset_monthly_count(user, db)
        
        if user.subscription_plan == "pro":
            # Pro users: unlimited, just increment count
            pass
        elif user.subscription_plan == "starter":
            # Starter users: check limit
            if user.posts_generated_this_month >= STARTER_MONTHLY_LIMIT:
                raise HTTPException(
                    status_code=403, 
                    detail=f"Monthly limit reached. Upgrade to Pro for unlimited posts."
                )
        else:
            # Free users: check if already used free post
            if user.free_post_used:
                raise HTTPException(
                    status_code=403,
                    detail="Free post already used. Choose a plan to continue."
                )
    
    # Generate the post
    result = run_brain(request.dict())
    
    # Update usage tracking
    if user:
        if user.subscription_plan in ["pro", "starter"]:
            user.posts_generated_this_month += 1
        else:
            user.free_post_used = True
        db.commit()
    
    return {"result": result}


@router.post("/calendar")
def generate_calendar(request: CalendarRequest):
    """Generate a full month's content calendar with posts and image ideas."""
    company_profile = {
        "brand_name": request.brand_name,
        "industry": request.industry,
        "target_audience": request.target_audience,
        "brand_values": request.brand_values,
        "brand_info": request.brand_info,
        "content_goals": request.content_goals,
        "platform": request.platform,
        "tone": request.tone,
        "include_cta": request.include_cta,
        "website_url": request.website_url,
        "website_summary": request.website_summary
    }
    
    monthly_context = {
        "promotions": request.monthly_promotions,
        "events": request.monthly_events,
        "focuses": request.monthly_focuses,
        "past_themes": request.past_themes or [],
        "feedback": request.feedback or "",
        "industry_insights": request.industry_insights or "",
        "personalized_tips": request.personalized_tips or ""
    }
    
    calendar = generate_content_calendar(
        company_profile, 
        request.posts_per_week,
        monthly_context
    )
    return calendar


@router.post("/research")
def get_industry_research(request: CompanyProfile):
    """Get AI-powered industry research and trends."""
    company_profile = request.dict()
    insights = research_industry_trends(company_profile)
    return {"insights": insights}


@router.post("/tips")
def get_tips(request: CompanyProfile):
    """Get personalized tips for social media strategy."""
    company_profile = request.dict()
    tips = generate_tips(company_profile)
    return {"tips": tips}


class RegeneratePostRequest(BaseModel):
    brand_name: str
    industry: str
    target_audience: str
    brand_values: str
    brand_info: str
    content_goals: str
    platform: str
    tone: Optional[str] = "professional"
    include_cta: Optional[bool] = True
    website_url: Optional[str] = ""
    website_summary: Optional[str] = ""
    # Post details
    post_date: str
    post_theme: str
    brand_analysis: Optional[str] = ""
    strategy: Optional[str] = ""
    feedback: Optional[str] = ""  # What they want different


@router.post("/regenerate-post")
def regenerate_single_post(request: RegeneratePostRequest):
    """Regenerate a single post in the calendar."""
    from app.prompt_engine.backend.content_planner import regenerate_one_post
    
    company_profile = {
        "brand_name": request.brand_name,
        "industry": request.industry,
        "target_audience": request.target_audience,
        "brand_values": request.brand_values,
        "brand_info": request.brand_info,
        "content_goals": request.content_goals,
        "platform": request.platform,
        "tone": request.tone,
        "include_cta": request.include_cta,
        "website_summary": request.website_summary
    }
    
    new_post = regenerate_one_post(
        company_profile=company_profile,
        post_date=request.post_date,
        post_theme=request.post_theme,
        brand_analysis=request.brand_analysis,
        strategy=request.strategy,
        feedback=request.feedback
    )
    
    return new_post
