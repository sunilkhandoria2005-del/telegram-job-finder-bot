from types import SimpleNamespace
from job_matcher import match_jobs


# Fake resume profile for testing
profile = SimpleNamespace(
    skills=[
        "Python",
        "SQL",
        "Machine Learning",
        "Git"
    ]
)


# Fake jobs for testing
jobs = [
    {
        "title": "Python Developer Intern",
        "company_name": "ABC Technologies",
        "location": "Bengaluru",
        "remote": True,
        "description": """
        Looking for a Python developer intern.
        Knowledge of Python, SQL and Git is required.
        """,
        "url": "https://example.com/python-job"
    },

    {
        "title": "Machine Learning Intern",
        "company_name": "AI Solutions",
        "location": "Remote",
        "remote": True,
        "description": """
        Looking for candidates with Machine Learning,
        Python and SQL skills.
        """,
        "url": "https://example.com/ml-job"
    },

    {
        "title": "Graphic Designer",
        "company_name": "Creative Studio",
        "location": "Delhi",
        "remote": False,
        "description": """
        Looking for a graphic designer with
        Photoshop and Illustrator experience.
        """,
        "url": "https://example.com/design-job"
    }
]


# Run matcher
matched_jobs = match_jobs(profile, jobs, minimum_score=30)


print("\n🎯 MATCHED JOBS")
print("=" * 50)

for job in matched_jobs:
    print(f"\n💼 {job['title']}")
    print(f"🏢 {job['company']}")
    print(f"📍 {job['location']}")
    print(f"🎯 Match Score: {job['match_score']}%")
    print(f"🔗 {job['url']}")