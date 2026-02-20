import os
from openai import OpenAI
from app.config import settings

# Load OpenAI key from settings
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def run_brain(input_data):
    """
    input_data: dictionary with all frontend form fields
    Returns: dict with post content and image suggestion
    """

    # Build a full prompt for AI using all fields
    prompt = f"""
You are a social media strategist. Write a {input_data['post_type']} social media post
for the following brand. Make sure the tone is {input_data['tone']}, and include a call-to-action
if 'include_cta' is True. Keep the post suitable for {input_data['platform']} and aligned with the brand's goals.

Brand Name: {input_data['brand_name']}
Industry: {input_data['industry']}
Target Audience: {input_data['target_audience']}
Brand Values: {input_data['brand_values']}
Brand Info: {input_data['brand_info']}
Content Goals: {input_data['content_goals']}
Post Topic: {input_data['post_topic']}
Content Themes: {input_data['content_themes']}
Post Frequency: {input_data['post_frequency']}
Include CTA: {input_data['include_cta']}

Provide your response in this exact format:

POST:
[The complete post, ready to copy-paste. Include 3-5 hashtags at the end.]

IMAGE IDEA:
[One sentence describing a simple photo the business owner can take with their phone in 5 minutes]

IMPORTANT: Do NOT use any markdown formatting (no **, ##, backticks, etc). Write in plain text only. Use emojis sparingly — maximum 1-2 per post, only if they add meaning. Never start with an emoji or use multiple in a row.
"""

    try:
        # Call OpenAI with timeout
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS,
            timeout=30.0
        )
        from app.prompt_engine.backend.content_planner import clean_markdown
        result = clean_markdown(response.choices[0].message.content)
        
        # Parse post and image idea
        post_content = result
        image_idea = ""
        
        if "IMAGE IDEA:" in result:
            parts = result.split("IMAGE IDEA:")
            post_content = parts[0].replace("POST:", "").strip()
            image_idea = parts[1].strip() if len(parts) > 1 else ""
        elif "POST:" in result:
            post_content = result.replace("POST:", "").strip()
        
        return {
            "post": clean_markdown(post_content),
            "image_idea": clean_markdown(image_idea) or "Take a photo that showcases your product or workspace with natural lighting."
        }
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return {
            "post": f"Error generating content: {str(e)}",
            "image_idea": ""
        }
