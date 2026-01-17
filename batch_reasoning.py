import json
from llm_reasoner import explain_job


def evaluate_jobs(jobs, user_profile):
    """
    Takes a list of discovered jobs and evaluates each one using the LLM.
    Returns a list of enriched job decisions.
    """
    evaluated_jobs = []

    for job in jobs:
        # 🔒 Normalize job format
        if isinstance(job, str):
            job = {
                "title": job,
                "company": "Unknown",
                "required_experience": None
            }

        try:
            llm_result = explain_job(job, user_profile)

            evaluated_jobs.append({
                "title": job.get("title"),
                "company": job.get("company"),
                "required_experience": job.get("required_experience"),
                "decision": llm_result.get("decision"),
                "reason": llm_result.get("reason"),
                "focus_keywords": llm_result.get("focus_keywords")
            })

        except Exception as e:
            evaluated_jobs.append({
                "title": job.get("title", "Unknown"),
                "company": job.get("company", "Unknown"),
                "error": str(e)
            })

    return evaluated_jobs


# Optional standalone run (for debugging only)
if __name__ == "__main__":
    from job_discovery import get_jobs

    with open("user_profile.json", "r") as f:
        user_profile = json.load(f)

    jobs = get_jobs()
    results = evaluate_jobs(jobs, user_profile)

    print(json.dumps(results, indent=2))
