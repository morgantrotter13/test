import os
from openai import OpenAI

# Load your OpenAI key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_brain(input_data):
    """
    input_data: dictionary with all frontend form fields
    Returns: AI-generated social media post
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

Generate ONE ready-to-post {input_data['post_type']} social media post below:
"""

    try:
        # Call OpenAI with timeout
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "800")),
            timeout=30.0
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return f"⚠️ Error generating content: {str(e)}"
