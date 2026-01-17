from dotenv import load_dotenv
import os
import json
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


def explain_job(job: dict, user_profile: dict) -> dict:
    """
    Uses an LLM to decide whether a job is worth applying to,
    explains why it fits the user, and highlights missing resume keywords.
    """

    prompt = f"""
You are an AI career advisor.

User profile:
- Target roles: {user_profile["roles_targeted"]}
- Years of experience: {user_profile["experience_years"]}
- Preferred max experience in job postings: {user_profile["max_experience_allowed"]}

Job details:
- Title: {job.get("title")}
- Company: {job.get("company")}
- Required experience (if mentioned): {job.get("required_experience")}

Instructions:
1. Decide whether the user should APPLY or SKIP this job.
2. Explain WHY the job fits or does not fit the user's profile.
3. Identify skills or keywords that are likely EXPECTED for this role but may be MISSING or WEAK in a typical ML/AI resume.
4. Be flexible with experience: if the role slightly exceeds experience, still recommend APPLY if skill overlap is strong.

Return JSON ONLY in the following format:
{
  "decision": "apply" or "skip",
  "fit_explanation": "Why this job fits or does not fit the user's background",
  "missing_keywords": ["keyword1", "keyword2", "keyword3"],
  "confidence_level": "high" | "medium" | "low"
}
"""

    response = client.chat.completions.create(
        model="openai/gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=400
    )

    return json.loads(response.choices[0].message.content)
