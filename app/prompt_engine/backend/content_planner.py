"""
Content Planner - Generates monthly content calendars using the full prompt workflow:
1. Brand Analysis
2. Strategy Development  
3. Post Generation (for each post)
"""
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from openai import OpenAI
from jinja2 import Template
from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)
MODEL = settings.OPENAI_MODEL


# Load prompt templates
def load_prompt(filename: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "prompts")
    filepath = os.path.join(prompts_dir, filename)
    with open(filepath, "r") as f:
        return f.read()


def call_llm(prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
    """Make a call to the LLM."""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=60.0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


def get_posting_days(posts_per_week: int, weeks: int = 4) -> List[datetime]:
    """Generate optimal posting days for the month."""
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    
    if posts_per_week >= 5:
        best_days = [0, 1, 2, 3, 4]  # Mon-Fri
    elif posts_per_week >= 3:
        best_days = [0, 2, 4]  # Mon, Wed, Fri
    elif posts_per_week >= 2:
        best_days = [1, 3]  # Tue, Thu
    else:
        best_days = [2]  # Wed
    
    posting_dates = []
    for week in range(weeks):
        week_start = start_of_week + timedelta(weeks=week)
        for day_offset in best_days[:posts_per_week]:
            post_date = week_start + timedelta(days=day_offset)
            if post_date >= today:
                posting_dates.append(post_date)
    
    return posting_dates[:posts_per_week * weeks]


def run_brand_analysis(company_profile: Dict[str, Any]) -> str:
    """Step 1: Run brand analysis prompt."""
    print("🔍 Running Brand Analysis...")
    
    template = Template(load_prompt("brand_analysis.txt"))
    prompt = template.render(
        brand_name=company_profile["brand_name"],
        industry=company_profile["industry"],
        target_audience=company_profile["target_audience"],
        brand_values=company_profile["brand_values"],
        brand_info=company_profile["brand_info"]
    )
    
    # Add website context if available
    if company_profile.get("website_summary"):
        prompt += f"""

WEBSITE ANALYSIS (use this to deeply understand the business):
{company_profile['website_summary']}

Use this website information to ensure all content is authentic and truly represents what this business actually does and offers.
"""
    
    # Add instruction to avoid markdown
    prompt += "\n\nIMPORTANT: Do NOT use any markdown formatting (no **, ##, `, etc). Write in plain text only."
    
    result = call_llm(prompt, temperature=0.7, max_tokens=1200)
    print("✅ Brand Analysis Complete")
    return clean_markdown(result)


def run_strategy(
    company_profile: Dict[str, Any], 
    brand_analysis: str, 
    posts_per_week: int,
    monthly_context: Dict[str, Any] = None
) -> str:
    """Step 2: Run strategy prompt based on brand analysis and monthly context."""
    print("📋 Developing Content Strategy...")
    
    if monthly_context is None:
        monthly_context = {}
    
    # Build monthly context string
    monthly_additions = []
    if monthly_context.get("promotions"):
        monthly_additions.append(f"UPCOMING PROMOTIONS: {monthly_context['promotions']}")
    if monthly_context.get("events"):
        monthly_additions.append(f"EVENTS & MILESTONES: {monthly_context['events']}")
    if monthly_context.get("focuses"):
        monthly_additions.append(f"SPECIAL FOCUSES: {monthly_context['focuses']}")
    
    monthly_context_str = "\n".join(monthly_additions) if monthly_additions else ""
    
    template = Template(load_prompt("strategy.txt"))
    prompt = template.render(
        brand_analysis_output=brand_analysis,
        content_goals=company_profile["content_goals"],
        platform=company_profile["platform"],
        post_frequency=f"{posts_per_week} posts per week",
        content_themes=f"Mix of educational, promotional, engagement, and storytelling content for {datetime.now().strftime('%B %Y')}"
    )
    
    # Add website data for authentic strategy
    if company_profile.get("website_summary"):
        prompt += f"""

WEBSITE & BUSINESS DATA (base all strategies on this real information):
{company_profile['website_summary']}

Use this to:
- Recommend content pillars based on their ACTUAL products/services
- Suggest post topics that relate to what they REALLY offer
- Create engagement tactics specific to their real business
- Ensure hashtag recommendations match their actual industry and offerings
"""
    
    # Add industry insights if available
    if monthly_context.get("industry_insights"):
        prompt += f"""

INDUSTRY INSIGHTS (incorporate these research findings into the strategy):
{monthly_context['industry_insights'][:800]}

Use these insights to inform:
- Content types that work best
- Optimal posting times
- Hashtag strategies
- What competitors are doing well
"""
    
    # Add personalized tips if available
    if monthly_context.get("personalized_tips"):
        prompt += f"""

PERSONALIZED TIPS (apply these recommendations):
{monthly_context['personalized_tips'][:600]}

Incorporate these tips into the overall strategy.
"""
    
    # Add monthly context to the prompt
    if monthly_context_str:
        prompt += f"\n\nTHIS MONTH'S PRIORITIES:\n{monthly_context_str}\n\nIncorporate these into the content strategy!"
    
    prompt += "\n\nIMPORTANT: Do NOT use any markdown formatting (no **, ##, `, etc). Write in plain text only."
    
    result = call_llm(prompt, temperature=0.7, max_tokens=1200)
    print("✅ Content Strategy Complete")
    return clean_markdown(result)


def run_post_generation(
    company_profile: Dict[str, Any], 
    brand_analysis: str, 
    strategy: str,
    post_topic: str,
    post_number: int,
    post_date: datetime,
    industry_insights: str = "",
    personalized_tips: str = ""
) -> Dict[str, str]:
    """Step 3: Generate a single post using brand analysis and strategy."""
    print(f"📝 Generating Post #{post_number} for {post_date.strftime('%A, %b %d')}...")
    
    template = Template(load_prompt("post_generation.txt"))
    
    # Build enhanced prompt for calendar posts
    enhanced_prompt = template.render(
        brand_analysis_output=brand_analysis,
        strategy_output=strategy,
        post_topic=post_topic,
        tone=company_profile.get("tone", "professional"),
        platform=company_profile["platform"],
        post_type="engaging social media post",
        include_cta=company_profile.get("include_cta", True)
    )
    
    # Add website context for more relevant posts
    website_context = ""
    if company_profile.get("website_summary"):
        website_context = f"""

BUSINESS CONTEXT (make sure the post is relevant to what they actually do):
{company_profile['website_summary'][:500]}

The post MUST relate to their actual products, services, or business. Don't make up offerings they don't have.
"""
    
    # Platform-specific length guidelines
    platform = company_profile["platform"]
    length_guide = {
        "Instagram": "Keep the caption 100-150 characters before hashtags. Short, punchy, and scroll-stopping. Hook in first line.",
        "Facebook": "Keep it 40-100 characters for best engagement. Brief and conversational.",
        "LinkedIn": "Keep it 50-100 words. Professional but personable. Start with a hook.",
        "TikTok": "Keep it under 100 characters. Fun, trendy, and action-oriented."
    }.get(platform, "Keep it concise - 2-3 short sentences max.")
    
    # Add industry insights context
    insights_context = ""
    if industry_insights:
        insights_context = f"""

INDUSTRY INSIGHTS (apply these to make the post more effective):
{industry_insights[:400]}
"""

    # Add personalized tips context
    tips_context = ""
    if personalized_tips:
        tips_context = f"""

TIPS TO APPLY:
{personalized_tips[:300]}
"""

    # Add image request to the prompt
    full_prompt = enhanced_prompt + website_context + insights_context + tips_context + f"""

POST LENGTH REQUIREMENT:
{length_guide}
DO NOT write long paragraphs. Short sentences. Easy to read. Gets to the point fast.

Additionally, provide:

IMAGE IDEA:
Suggest ONE simple image a small business owner can take with their phone in 5 minutes. One sentence only.

BEST TIME TO POST:
Just the time of day, like "10am" or "6pm". Do NOT include the day of the week.

IMPORTANT: 
- Keep the post SHORT and punchy - optimized for {platform}
- Write it exactly as it should appear (ready to copy-paste)
- Make sure content is RELEVANT to their actual business
- Do NOT invent events, promotions, sales, dates, statistics, testimonials, or specific details that were not provided. Only reference what is real and verifiable from the company data given.
- If no specific event or promotion was mentioned, write evergreen content that highlights what the business actually does, its values, or its expertise.
- No markdown formatting
- Use emojis sparingly — maximum 1-2 per post, only if they add meaning. Never start with an emoji or use multiple in a row.
- Hashtags at the end (3-5 relevant ones)"""
    
    result = call_llm(full_prompt, temperature=0.75, max_tokens=600)
    
    # Parse the response
    post_content = result
    image_idea = ""
    best_time = "9:00 AM - 11:00 AM"
    
    if "IMAGE IDEA:" in result:
        parts = result.split("IMAGE IDEA:")
        post_content = parts[0].replace("POST CONTENT:", "").strip()
        if len(parts) > 1:
            remaining = parts[1]
            if "BEST TIME TO POST:" in remaining:
                image_parts = remaining.split("BEST TIME TO POST:")
                image_idea = image_parts[0].strip()
                best_time = image_parts[1].strip() if len(image_parts) > 1 else best_time
            else:
                image_idea = remaining.strip()
    
    print(f"✅ Post #{post_number} Generated")
    
    return {
        "post_content": clean_markdown(post_content),
        "image_idea": clean_markdown(image_idea) or "Create a branded visual that aligns with your brand identity",
        "best_time": clean_markdown(best_time)
    }


def generate_post_topics(
    strategy: str, 
    num_posts: int, 
    platform: str,
    monthly_context: Dict[str, Any] = None,
    company_profile: Dict[str, Any] = None
) -> List[str]:
    """Generate unique post topics based on the strategy, avoiding past themes."""
    print(f"💡 Generating {num_posts} Fresh Post Topics...")
    
    if monthly_context is None:
        monthly_context = {}
    if company_profile is None:
        company_profile = {}
    
    # Build avoid list
    past_themes = monthly_context.get("past_themes", [])
    avoid_section = ""
    if past_themes:
        avoid_section = f"""
IMPORTANT - DO NOT use these topics (already covered in previous months):
{chr(10).join(f'- {theme}' for theme in past_themes[:20])}

Generate COMPLETELY FRESH ideas that are different from the above!
"""
    
    # Build monthly priorities
    priorities = []
    if monthly_context.get("promotions"):
        priorities.append(f"Include posts about: {monthly_context['promotions']}")
    if monthly_context.get("events"):
        priorities.append(f"Include posts about: {monthly_context['events']}")
    if monthly_context.get("focuses"):
        priorities.append(f"Emphasize: {monthly_context['focuses']}")
    
    priorities_section = "\n".join(priorities) if priorities else ""
    
    # Add user feedback if provided
    feedback_section = ""
    if monthly_context.get("feedback"):
        feedback_section = f"""
USER FEEDBACK - IMPORTANT:
The user wants these changes: {monthly_context['feedback']}
Make sure to incorporate this feedback into the topics!
"""
    
    # Add website context for relevant topics
    website_section = ""
    if company_profile.get("website_summary"):
        website_section = f"""
BUSINESS INFORMATION (topics MUST relate to their actual offerings):
{company_profile['website_summary'][:600]}

Every topic must be directly relevant to what this business actually does, sells, or offers.
Do NOT suggest generic topics - make them specific to THIS business.
"""
    
    prompt = f"""Based on this content strategy:

{strategy}

Generate exactly {num_posts} unique, specific post topics for {platform} for the month of {datetime.now().strftime('%B %Y')}.

{avoid_section}

{f"THIS MONTH'S PRIORITIES:{chr(10)}{priorities_section}" if priorities_section else ""}

{feedback_section}

{website_section}

Requirements:
- Mix of content types: educational, promotional, engagement, storytelling, behind-the-scenes
- Each topic should be specific and actionable
- Consider seasonal/timely relevance for {datetime.now().strftime('%B')}
- Align with the content pillars from the strategy
- Make each topic FRESH and UNIQUE

Return ONLY a numbered list with {num_posts} topics, one per line. No explanations.
"""
    
    result = call_llm(prompt, temperature=0.8, max_tokens=800)
    
    # Parse topics
    topics = []
    for line in result.strip().split('\n'):
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith('-')):
            # Remove numbering
            topic = line.lstrip('0123456789.-) ').strip()
            if topic:
                topics.append(topic)
    
    # Ensure we have enough topics
    while len(topics) < num_posts:
        topics.append(f"Engaging content about your brand - Post {len(topics) + 1}")
    
    print(f"✅ Generated {len(topics)} Topics")
    return topics[:num_posts]


def generate_content_calendar(
    company_profile: Dict[str, Any], 
    posts_per_week: int = 3,
    monthly_context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Generate a full month's content calendar using the complete prompt workflow:
    1. Brand Analysis (once)
    2. Strategy Development (once)
    3. Post Generation (for each post)
    
    monthly_context can include:
    - promotions: upcoming sales/offers
    - events: events/milestones
    - focuses: special content focuses
    - past_themes: themes to avoid (from previous months)
    """
    print("\n" + "="*50)
    print("🚀 STARTING CONTENT CALENDAR GENERATION")
    print("="*50 + "\n")
    
    if monthly_context is None:
        monthly_context = {}
    
    posting_dates = get_posting_days(posts_per_week, weeks=4)
    total_posts = len(posting_dates)
    
    # Step 1: Brand Analysis
    brand_analysis = run_brand_analysis(company_profile)
    
    # Step 2: Content Strategy (with monthly context)
    strategy = run_strategy(company_profile, brand_analysis, posts_per_week, monthly_context)
    
    # Step 3: Generate Post Topics (avoiding past themes, using website data)
    topics = generate_post_topics(
        strategy, 
        total_posts, 
        company_profile["platform"],
        monthly_context,
        company_profile
    )
    
    # Step 4: Generate Each Post
    print(f"\n📆 Generating {total_posts} Posts...\n")
    posts = []
    
    for i, post_date in enumerate(posting_dates):
        topic = topics[i] if i < len(topics) else f"Engaging content for {company_profile['brand_name']}"
        
        try:
            post_data = run_post_generation(
                company_profile=company_profile,
                brand_analysis=brand_analysis,
                strategy=strategy,
                post_topic=topic,
                post_number=i + 1,
                post_date=post_date,
                industry_insights=monthly_context.get("industry_insights", "") if monthly_context else "",
                personalized_tips=monthly_context.get("personalized_tips", "") if monthly_context else ""
            )
            
            posts.append({
                "date": post_date.strftime("%Y-%m-%d"),
                "day_of_week": post_date.strftime("%A"),
                "theme": topic,
                "post_content": post_data["post_content"],
                "image_idea": post_data["image_idea"],
                "best_time": post_data["best_time"],
                "status": "scheduled"
            })
        except Exception as e:
            print(f"❌ Error generating post {i+1}: {e}")
            posts.append({
                "date": post_date.strftime("%Y-%m-%d"),
                "day_of_week": post_date.strftime("%A"),
                "theme": topic,
                "post_content": f"Error generating post: {str(e)}",
                "image_idea": "",
                "best_time": "",
                "status": "error"
            })
    
    print("\n" + "="*50)
    print("✅ CONTENT CALENDAR COMPLETE!")
    print(f"   Generated {len(posts)} posts for {datetime.now().strftime('%B %Y')}")
    print("="*50 + "\n")
    
    return {
        "company": company_profile["brand_name"],
        "platform": company_profile["platform"],
        "month": datetime.now().strftime("%B %Y"),
        "posts_per_week": posts_per_week,
        "total_posts": len(posts),
        "brand_analysis": brand_analysis,
        "strategy": strategy,
        "posts": posts
    }


def clean_markdown(text: str) -> str:
    """Remove markdown formatting from text for clean user-facing display."""
    import re
    if not text:
        return text
    # Remove bold markers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    # Remove italic markers (but be careful with asterisks in hashtags)
    text = re.sub(r'(?<!\w)\*([^*]+)\*(?!\w)', r'\1', text)
    text = re.sub(r'(?<!\w)_([^_]+)_(?!\w)', r'\1', text)
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove code blocks
    text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Remove horizontal rules
    text = re.sub(r'^[\-\*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Remove blockquotes
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    # Clean up extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def regenerate_one_post(
    company_profile: Dict[str, Any],
    post_date: str,
    post_theme: str,
    brand_analysis: str = "",
    strategy: str = "",
    feedback: str = ""
) -> Dict[str, Any]:
    """Regenerate a single post with optional feedback."""
    print(f"🔄 Regenerating post for {post_date}...")
    
    platform = company_profile["platform"]
    
    # Platform-specific length guidelines
    length_guide = {
        "Instagram": "Keep the caption 100-150 characters before hashtags. Short, punchy, and scroll-stopping.",
        "Facebook": "Keep it 40-100 characters for best engagement. Brief and conversational.",
        "LinkedIn": "Keep it 50-100 words. Professional but personable. Start with a hook.",
        "TikTok": "Keep it under 100 characters. Fun, trendy, and action-oriented."
    }.get(platform, "Keep it concise - 2-3 short sentences max.")
    
    # Build the prompt
    prompt = f"""Generate a COMPLETELY NEW social media post for {company_profile['brand_name']}.
The previous post was about "{post_theme}" — write something fresh and different.

BUSINESS INFO:
- Industry: {company_profile['industry']}
- Target Audience: {company_profile['target_audience']}
- Brand Values: {company_profile['brand_values']}
- About: {company_profile['brand_info'][:300]}

ORIGINAL TOPIC: {post_theme}
PLATFORM: {platform}
TONE: {company_profile.get('tone', 'professional')}
INCLUDE CTA: {company_profile.get('include_cta', True)}
"""

    if company_profile.get("website_summary"):
        prompt += f"""
BUSINESS CONTEXT (make it relevant to what they actually do):
{company_profile['website_summary'][:400]}
"""

    if feedback:
        prompt += f"""
USER FEEDBACK - The user wants these specific changes. Follow their feedback closely:
{feedback}
"""
    else:
        prompt += """
No specific feedback — just create a completely different post with a fresh angle and new theme.
"""

    prompt += f"""
POST LENGTH: {length_guide}

Provide response in this EXACT format:

THEME:
[A short 3-6 word theme/topic for this post — different from the original]

POST:
[The complete post, ready to copy-paste. Short and punchy. Include 3-5 hashtags at the end. Must be COMPLETELY different from any previous version.]

IMAGE IDEA:
[One sentence - simple photo idea they can take with their phone in 5 minutes]

BEST TIME:
[Just the time of day like "10am" or "6pm". Do NOT include the day of the week.]

IMPORTANT:
- Generate entirely NEW content — different theme, different angle, different wording.
- No markdown formatting.
- Keep post SHORT and optimized for {platform}.
- Use emojis sparingly — maximum 1-2 per post, only if they add meaning.
- Do NOT invent events, promotions, sales, dates, statistics, or testimonials that were not provided. Only reference real details from the business info above.
- Write authentically as if you are the business owner.
"""

    result = call_llm(prompt, temperature=0.8, max_tokens=600)
    
    # Parse the response
    new_theme = post_theme  # fallback to original
    post_content = result
    image_idea = ""
    best_time = ""
    
    # Extract theme
    if "THEME:" in result and "POST:" in result:
        theme_section = result.split("POST:")[0]
        new_theme = theme_section.replace("THEME:", "").strip()
    
    # Extract post content, image idea, and best time
    if "POST:" in result:
        after_post = result.split("POST:", 1)[1]
        
        if "IMAGE IDEA:" in after_post:
            post_content = after_post.split("IMAGE IDEA:")[0].strip()
            remaining = after_post.split("IMAGE IDEA:", 1)[1]
            
            if "BEST TIME:" in remaining:
                image_idea = remaining.split("BEST TIME:")[0].strip()
                best_time = remaining.split("BEST TIME:", 1)[1].strip()
            else:
                image_idea = remaining.strip()
        else:
            post_content = after_post.strip()
    
    print(f"✅ Post regenerated with new theme: {new_theme}")
    
    # Parse the date to get day of week
    from datetime import datetime
    try:
        date_obj = datetime.strptime(post_date, "%Y-%m-%d")
        day_of_week = date_obj.strftime("%A")
    except:
        day_of_week = ""
    
    return {
        "date": post_date,
        "day_of_week": day_of_week,
        "theme": clean_markdown(new_theme) or post_theme,
        "post_content": clean_markdown(post_content),
        "image_idea": clean_markdown(image_idea) or "Take a simple photo related to this topic with your phone",
        "best_time": clean_markdown(best_time) or "Weekday morning 9-11am",
        "status": "scheduled"
    }


def research_industry_trends(company_profile: Dict[str, Any]) -> str:
    """Research top-performing content in the company's industry."""
    prompt = f"""
You are a social media marketing expert helping {company_profile['brand_name']}.

Analyze what content performs best for {company_profile['industry']} businesses targeting {company_profile['target_audience']} on {company_profile['platform']}.

Provide your response in this EXACT format (no markdown, no bold, no headers):

TOP PERFORMING CONTENT TYPES
• [First type and why it works]
• [Second type and why it works]
• [Third type and why it works]

BEST TIMES TO POST
• [Day and time recommendation 1]
• [Day and time recommendation 2]

HASHTAG STRATEGY
• [Hashtag recommendation 1]
• [Hashtag recommendation 2]
• [Hashtag recommendation 3]

TRENDING TOPICS RIGHT NOW
• [Current trend 1]
• [Current trend 2]

COMPETITOR INSIGHTS
• [What successful competitors are doing]

Keep each bullet point concise (1-2 sentences max). Be specific to their industry.
"""
    result = call_llm(prompt, temperature=0.7, max_tokens=800)
    return clean_markdown(result)


def generate_tips(company_profile: Dict[str, Any]) -> str:
    """Generate personalized tips for the company's social media strategy."""
    prompt = f"""
You are a social media consultant helping {company_profile['brand_name']}.

Their goal: {company_profile['content_goals']}
Platform: {company_profile['platform']}
Audience: {company_profile['target_audience']}

Provide 6 actionable tips in this EXACT format (no markdown, no bold, no headers):

QUICK WIN - DO TODAY
[One specific action they can take right now]

ENGAGEMENT BOOSTER
[One tactic to increase engagement with their audience]

CONTENT TIP
[One way to improve their content quality]

GROWTH HACK
[One strategy to grow their following]

AVOID THIS MISTAKE
[One common mistake in their industry to avoid]

PRO TIP
[One advanced strategy for when they're ready]

Keep each tip to 2-3 sentences. Be specific to {company_profile['industry']}, not generic.
"""
    result = call_llm(prompt, temperature=0.7, max_tokens=600)
    return clean_markdown(result)
