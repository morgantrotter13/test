"""
Website Scraper - Extracts business information from company websites.
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
import re


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def scrape_website(url: str) -> Dict[str, Any]:
    """
    Scrape a website to extract business-relevant information.
    
    Returns:
        Dict with: description, services, about, contact_info, social_proof, key_phrases
    """
    print(f"🌐 Scraping website: {url}")
    
    result = {
        "url": url,
        "description": "",
        "services_products": [],
        "about": "",
        "tagline": "",
        "key_phrases": [],
        "social_proof": [],
        "contact_info": "",
        "scraped_successfully": False
    }
    
    try:
        # Normalize URL
        if not url.startswith('http'):
            url = 'https://' + url
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Get meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            result["description"] = clean_text(meta_desc.get('content', ''))
        
        # Get title/tagline
        title = soup.find('title')
        if title:
            result["tagline"] = clean_text(title.get_text())
        
        # Look for hero/main heading
        h1 = soup.find('h1')
        if h1:
            h1_text = clean_text(h1.get_text())
            if h1_text and len(h1_text) < 200:
                result["tagline"] = h1_text
        
        # Extract main content
        main_content = ""
        
        # Look for about section
        about_sections = soup.find_all(['section', 'div'], 
            class_=lambda x: x and any(term in str(x).lower() for term in ['about', 'story', 'mission']))
        for section in about_sections[:2]:
            text = clean_text(section.get_text())
            if len(text) > 50:
                main_content += text + " "
        
        # Look for services/products
        service_sections = soup.find_all(['section', 'div'], 
            class_=lambda x: x and any(term in str(x).lower() for term in ['service', 'product', 'offer', 'solution']))
        for section in service_sections[:2]:
            text = clean_text(section.get_text())
            if len(text) > 30:
                result["services_products"].append(text[:300])
        
        # Get all paragraph text for context
        paragraphs = soup.find_all('p')
        for p in paragraphs[:15]:
            text = clean_text(p.get_text())
            if len(text) > 40 and len(text) < 500:
                main_content += text + " "
        
        # Look for testimonials/reviews
        testimonial_sections = soup.find_all(['blockquote', 'div'], 
            class_=lambda x: x and any(term in str(x).lower() for term in ['testimonial', 'review', 'quote']))
        for section in testimonial_sections[:3]:
            text = clean_text(section.get_text())
            if len(text) > 20 and len(text) < 300:
                result["social_proof"].append(text)
        
        # Extract key phrases (look for emphasized text)
        strong_text = soup.find_all(['strong', 'b', 'em'])
        for item in strong_text[:10]:
            text = clean_text(item.get_text())
            if len(text) > 3 and len(text) < 100:
                result["key_phrases"].append(text)
        
        # Store main content as about
        result["about"] = main_content[:2000] if main_content else ""
        
        result["scraped_successfully"] = True
        print(f"✅ Website scraped successfully")
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Could not scrape website: {e}")
        result["about"] = "Website could not be accessed"
    except Exception as e:
        print(f"⚠️ Error scraping website: {e}")
        result["about"] = "Error processing website"
    
    return result


def summarize_website_for_prompts(scraped_data: Dict[str, Any]) -> str:
    """
    Create a concise summary of the website for use in prompts.
    """
    if not scraped_data.get("scraped_successfully"):
        return ""
    
    summary_parts = []
    
    if scraped_data.get("tagline"):
        summary_parts.append(f"Tagline: {scraped_data['tagline']}")
    
    if scraped_data.get("description"):
        summary_parts.append(f"Description: {scraped_data['description']}")
    
    if scraped_data.get("about"):
        # Truncate to key info
        about = scraped_data["about"][:800]
        summary_parts.append(f"About: {about}")
    
    if scraped_data.get("services_products"):
        services = ", ".join(scraped_data["services_products"][:3])
        summary_parts.append(f"Services/Products: {services}")
    
    if scraped_data.get("key_phrases"):
        phrases = ", ".join(scraped_data["key_phrases"][:5])
        summary_parts.append(f"Key phrases they use: {phrases}")
    
    if scraped_data.get("social_proof"):
        proof = scraped_data["social_proof"][0]
        summary_parts.append(f"Customer quote: {proof}")
    
    return "\n".join(summary_parts)


def infer_company_profile(scraped_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Use AI to infer company profile details from scraped website data.
    """
    from app.prompt_engine.backend.content_planner import call_llm
    
    if not scraped_data.get("scraped_successfully"):
        return {}
    
    # Build context from scraped data
    context = summarize_website_for_prompts(scraped_data)
    
    prompt = f"""Based on this website information, extract the following business details.
Be concise and accurate - only include what you can reasonably infer.

WEBSITE DATA:
{context}

Provide the following in this exact format (each field on its own line):

BRAND_NAME: [The company/brand name]
INDUSTRY: [Their industry, e.g., "Food & Beverage", "Professional Services", "E-commerce", "Health & Wellness"]
ABOUT: [2-3 sentences about what they do, their products/services, and what makes them unique]
TARGET_AUDIENCE: [Who their ideal customers are - be specific about demographics and needs]
BRAND_VALUES: [3-5 core values or qualities they emphasize]
CONTENT_GOALS: [What social media goals would benefit this business - be specific]
TONE: [One of: professional, casual, playful, authoritative, inspirational, educational - pick the best fit]

Be specific and tailored to THIS business. Don't use generic filler text."""

    result = call_llm(prompt, temperature=0.3, max_tokens=600)
    
    # Parse the response
    profile = {}
    lines = result.strip().split('\n')
    
    field_map = {
        'BRAND_NAME': 'brand_name',
        'INDUSTRY': 'industry',
        'ABOUT': 'brand_info',
        'TARGET_AUDIENCE': 'target_audience',
        'BRAND_VALUES': 'brand_values',
        'CONTENT_GOALS': 'content_goals',
        'TONE': 'tone'
    }
    
    for line in lines:
        for key, field in field_map.items():
            if line.upper().startswith(key + ':'):
                value = line.split(':', 1)[1].strip()
                # Clean up common AI formatting
                value = value.strip('[]"\'')
                profile[field] = value
                break
    
    # Normalize tone to valid options
    valid_tones = ['professional', 'casual', 'playful', 'authoritative', 'inspirational', 'educational']
    if profile.get('tone'):
        tone_lower = profile['tone'].lower()
        for valid in valid_tones:
            if valid in tone_lower:
                profile['tone'] = valid
                break
        else:
            profile['tone'] = 'professional'
    
    return profile
