"""
Content generation and planning routes.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
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


router = APIRouter()


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


@router.post("/generate")
def generate_content(request: ContentRequest):
    """Generate a single social media post using AI."""
    result = run_brain(request.dict())
    # result is now a dict with "post" and "image_idea"
    if isinstance(result, dict):
        return {
            "result": result.get("post", ""),
            "image_idea": result.get("image_idea", "")
        }
    # Backward compatibility if result is a string
    return {"result": result, "image_idea": ""}


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
