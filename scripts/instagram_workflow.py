"""
Modular Instagram workflow using OpenAI Chat Completions.

Steps:
1. Brand analysis — summarize brand voice and audience.
2. Strategy selection — choose best Instagram strategy based on brand summary and goal.
3. Post generation — produce a complete Instagram post (hook, caption, visual idea, CTA).

Features:
- Optional modifier applied to each step's prompt (e.g., "make it more educational").
- Debug prints for each step.
- Safe error handling with try/except and timeout.

Usage:
- Set OPENAI_API_KEY in your environment.
- Run this file directly to execute the sample test at the bottom.
"""

import os
from typing import Optional
from dataclasses import dataclass
from openai import OpenAI, OpenAIError


# -------------- Configuration --------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "600"))
TIMEOUT = float(os.getenv("OPENAI_TIMEOUT", "30"))


# -------------- Prompt Templates --------------
BRAND_ANALYSIS_PROMPT = """You are a brand analyst. Given the business info:
{business_info}

Provide a concise brand summary including:
- Brand voice and tone
- Target audience
- Core value props
- Visual/creative style cues
"""

STRATEGY_PROMPT = """You are a social strategist. Based on the brand summary and goal, pick the best Instagram strategy.

Brand summary:
{brand_summary}

Goal:
{goal}

Provide:
- Strategy approach
- Content pillars (3-5)
- Posting cadence & timing
- Engagement tactics
- Hashtag guidance
"""

POST_PROMPT = """You are a social copywriter. Based on the brand summary and strategy, write a complete Instagram post.

Brand summary:
{brand_summary}

Strategy:
{strategy}

Goal:
{goal}

Deliver:
- Hook
- Caption (concise, scannable)
- Visual idea
- Call to action (CTA)
- Suggested hashtags (light)
"""


# -------------- Data Structures --------------
@dataclass
class StepResult:
    rendered_prompt: str
    output: Optional[str]
    error: Optional[str] = None


# -------------- LLM Helper --------------
def call_llm(prompt: str, model: str = MODEL, temperature: float = TEMPERATURE, max_tokens: int = MAX_TOKENS) -> StepResult:
    if not OPENAI_API_KEY:
        return StepResult(rendered_prompt=prompt, output=None, error="OPENAI_API_KEY not set")

    client = OpenAI(api_key=OPENAI_API_KEY)
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=TIMEOUT,
        )
        return StepResult(rendered_prompt=prompt, output=resp.choices[0].message.content, error=None)
    except OpenAIError as e:
        return StepResult(rendered_prompt=prompt, output=None, error=f"OpenAIError: {e}")
    except Exception as e:
        return StepResult(rendered_prompt=prompt, output=None, error=f"Unhandled error: {e}")


# -------------- Workflow Function --------------
def run_instagram_workflow(business_info: str, goal: str, modifier: Optional[str] = None, model: str = MODEL) -> dict:
    """
    Run the Instagram workflow: brand analysis -> strategy -> post generation.
    Optional modifier is appended to each prompt (e.g., "make it more educational").
    Returns a dict with step results and final output.
    """
    # Step 1: Brand analysis
    prompt1 = BRAND_ANALYSIS_PROMPT.format(business_info=business_info)
    if modifier:
        prompt1 += f"\nModifier: {modifier}"
    res1 = call_llm(prompt1, model=model)
    print("\n[DEBUG] Brand Analysis Prompt:\n", res1.rendered_prompt)
    print("\n[DEBUG] Brand Analysis Output:\n", res1.output or res1.error)
    if res1.error or not res1.output:
        return {"brand_analysis": res1, "strategy": None, "post": None, "final": None}

    # Step 2: Strategy selection
    prompt2 = STRATEGY_PROMPT.format(brand_summary=res1.output, goal=goal)
    if modifier:
        prompt2 += f"\nModifier: {modifier}"
    res2 = call_llm(prompt2, model=model)
    print("\n[DEBUG] Strategy Prompt:\n", res2.rendered_prompt)
    print("\n[DEBUG] Strategy Output:\n", res2.output or res2.error)
    if res2.error or not res2.output:
        return {"brand_analysis": res1, "strategy": res2, "post": None, "final": None}

    # Step 3: Post generation
    prompt3 = POST_PROMPT.format(brand_summary=res1.output, strategy=res2.output, goal=goal)
    if modifier:
        prompt3 += f"\nModifier: {modifier}"
    res3 = call_llm(prompt3, model=model)
    print("\n[DEBUG] Post Prompt:\n", res3.rendered_prompt)
    print("\n[DEBUG] Post Output:\n", res3.output or res3.error)

    final_output = res3.output if res3.output else None

    return {
        "brand_analysis": res1,
        "strategy": res2,
        "post": res3,
        "final": final_output,
    }


# -------------- Test Runner --------------
if __name__ == "__main__":
    SAMPLE_BUSINESS = """
    We are a boutique coffee roaster and café focused on sustainable sourcing,
    small-batch roasting, and community events. We host weekly cuppings and
    latte art classes, and sell beans online and in-store.
    """
    SAMPLE_GOAL = "Increase Instagram engagement and drive foot traffic for events."
    SAMPLE_MODIFIER = "Make it slightly educational and emphasize local community."

    print("Running Instagram workflow sample...\n")
    results = run_instagram_workflow(
        business_info=SAMPLE_BUSINESS.strip(),
        goal=SAMPLE_GOAL,
        modifier=SAMPLE_MODIFIER,
    )

    print("\n==== FINAL RESULTS ====")
    print("\n[Brand Analysis]\n", results["brand_analysis"].output or results["brand_analysis"].error)
    print("\n[Strategy]\n", results["strategy"].output or (results["strategy"].error if results["strategy"] else "No strategy"))
    print("\n[Post]\n", results["post"].output or (results["post"].error if results["post"] else "No post"))
    print("\n[Final Output]\n", results["final"] or "No final output")
