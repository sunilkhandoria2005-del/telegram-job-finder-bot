import requests


def fetch_remotive_jobs():
    url = "https://remotive.com/api/remote-jobs"

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    data = response.json()

    jobs = data.get("jobs", [])

    print(f"✅ Remotive jobs fetched: {len(jobs)}")

    return jobs


if __name__ == "__main__":

    print("\n🔎 Testing Remotive Remote Jobs\n")

    jobs = fetch_remotive_jobs()

    for job in jobs[:5]:

        print("\n-------------------------")
        print("Title:", job.get("title"))
        print("Company:", job.get("company_name"))
        print("Location:", job.get("candidate_required_location"))
        print("Job Type:", job.get("job_type"))
        print("Category:", job.get("category"))
        print("URL:", job.get("url"))