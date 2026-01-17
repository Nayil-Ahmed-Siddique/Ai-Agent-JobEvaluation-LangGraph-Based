from playwright.sync_api import sync_playwright
import json
import re


def is_masked(text: str) -> bool:
    return "*" in text


def is_relevant_role(title: str, roles: list[str]) -> bool:
    title = title.lower()
    return any(role in title for role in roles)


def extract_experience(text: str):
    match = re.search(r"(\d+)\s*\+?\s*years?", text.lower())
    if match:
        return int(match.group(1))
    return None


def discover_jobs():
    with open("user_profile.json", "r") as f:
        user_profile = json.load(f)

    roles_targeted = [r.lower() for r in user_profile["roles_targeted"]]
    max_experience_allowed = user_profile["max_experience_allowed"]

    jobs = []
    skipped_jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(
            "https://www.linkedin.com/jobs/search/?keywords="
            "machine%20learning%20OR%20artificial%20intelligence%20OR%20"
            "data%20science%20OR%20genai%20OR%20llm%20OR%20ai%20engineer"
        )

        job_cards = page.locator("ul.jobs-search__results-list li")
        count = job_cards.count()

        for i in range(count):
            card = job_cards.nth(i)
            title = card.locator("h3").inner_text()
            company = card.locator("h4").inner_text()
            job_text = card.inner_text()

            required_experience = extract_experience(job_text)

            if is_masked(title) or is_masked(company):
                skipped_jobs.append({
                    "title": title,
                    "company": company,
                    "reason": "masked"
                })
                continue

            if not is_relevant_role(title, roles_targeted):
                skipped_jobs.append({
                    "title": title,
                    "company": company,
                    "reason": "role_mismatch"
                })
                continue

            if required_experience is not None and required_experience > max_experience_allowed:
                skipped_jobs.append({
                    "title": title,
                    "company": company,
                    "required_experience": required_experience,
                    "reason": "experience_too_high"
                })
                continue

            jobs.append({
                "title": title,
                "company": company,
                "required_experience": required_experience
            })

        browser.close()

    # 🔴 THIS IS THE KEY CONTRACT
    return {
        "jobs": jobs,
        "skipped_jobs": skipped_jobs
    }


def get_jobs():
    return discover_jobs()


if __name__ == "__main__":
    print(discover_jobs())
