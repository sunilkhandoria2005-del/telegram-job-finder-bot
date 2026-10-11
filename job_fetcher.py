import requests
import os
from dotenv import load_dotenv

load_dotenv()


# --------------------------------------------------
# INDIA-COMPATIBLE REMOTE REGIONS
# --------------------------------------------------

INDIA_REMOTE_REGIONS = [
    "india",
    "apac",
    "asia",
    "south asia",
    "worldwide",
    "global",
]


# --------------------------------------------------
# ARBEITNOW
# --------------------------------------------------

def fetch_arbeitnow_jobs():
    """Fetch jobs from Arbeitnow."""

    url = "https://www.arbeitnow.com/api/job-board-api"

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    data = response.json()
    jobs = data.get("data", [])

    print(f"[SUCCESS] Arbeitnow jobs fetched: {len(jobs)}")

    normalized_jobs = []

    for job in jobs:
        normalized_jobs.append({
            "title": job.get("title", ""),
            "company_name": job.get("company_name", ""),
            "location": job.get("location", ""),
            "description": job.get("description", ""),
            "tags": job.get("tags", []),
            "job_types": job.get("job_types", []),
            "remote": job.get("remote", False),
            "url": job.get("url", ""),
            "source": "Arbeitnow",
            "location_match": None,
        })

    return normalized_jobs


# --------------------------------------------------
# REMOTIVE
# --------------------------------------------------

def fetch_remotive_jobs():
    """Fetch remote jobs from Remotive."""

    url = "https://remotive.com/api/remote-jobs"

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    data = response.json()
    jobs = data.get("jobs", [])

    print(f"[SUCCESS] Remotive jobs fetched: {len(jobs)}")

    normalized_jobs = []

    for job in jobs:

        location = job.get(
            "candidate_required_location",
            ""
        )

        normalized_jobs.append({
            "title": job.get("title", ""),
            "company_name": job.get("company_name", ""),
            "location": location,
            "description": job.get("description", ""),
            "tags": job.get("tags", []),
            "job_types": [job.get("job_type", "")],
            "remote": True,
            "url": job.get("url", ""),
            "source": "Remotive",
            "location_match": None,
        })

    return normalized_jobs


# --------------------------------------------------
# ADZUNA
# --------------------------------------------------

def fetch_adzuna_jobs(location=None, work_mode="any", job_type="any"):
    """Fetch jobs from Adzuna API."""

    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")

    if not app_id or not app_key:
        return []  # Return empty list if credentials not configured

    # Determine country based on location (default to 'in' for India)
    country = "in"  # India
    if location:
        location_lower = location.lower()
        if location_lower in ["us", "usa", "united states"]:
            country = "us"
        elif location_lower in ["uk", "united kingdom", "gb"]:
            country = "gb"
        elif location_lower in ["ca", "canada"]:
            country = "ca"
        elif location_lower in ["au", "australia"]:
            country = "au"

    # Build search parameters
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": 50,  # Max allowed per page
        "content-type": "application/json"
    }

    # Add location if specified and not 'any'
    if location and location.lower() != "any":
        params["where"] = location

    url = f"https://api.adzuna.com/v1/api/jobs/{country}/1"

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()
        jobs = data.get("results", [])

        normalized_jobs = []

        for job in jobs:
            # Extract and normalize job data
            normalized_jobs.append({
                "title": job.get("title", ""),
                "company_name": job.get("company", {}).get("display_name", ""),
                "location": job.get("location", {}).get("display_area", ""),
                "description": job.get("description", ""),
                "tags": [job.get("category", {}).get("label", "")] if job.get("category") else [],
                "job_types": [job.get("contract_type", "")] if job.get("contract_type") else [],
                "remote": "remote" in job.get("title", "").lower() or "remote" in job.get("location", {}).get("display_area", "").lower(),
                "url": job.get("redirect_url", ""),
                "source": "Adzuna",
                "location_match": None,  # Will be calculated in filter function
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "salary_is_predicted": job.get("salary_is_predicted", False)
            })

        return normalized_jobs

    except Exception:
        # Silently fail - don't break the pipeline if Adzuna is unavailable
        return []


# --------------------------------------------------
# INDIAN Jobs API (indianapi.in)
# --------------------------------------------------

def fetch_indianapi_jobs(location=None, work_mode="any", job_type="any"):
    """Fetch jobs from Indian Jobs API (indianapi.in)."""

    api_key = os.getenv("INDIAN_API_KEY")

    if not api_key:
        return []  # Return empty list if credentials not configured

    # Base URL for the API
    base_url = "https://jobs.indianapi.in"
    endpoint = "/jobs"
    url = f"{base_url}{endpoint}"

    # Prepare headers
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }

    # Prepare query parameters
    params = {}

    # Add location if specified and not 'any'
    if location and location.lower() != "any":
        params["location"] = location

    # Add limit parameter (adjust as needed)
    params["limit"] = "50"  # Get up to 50 jobs per request

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()
        # Assuming the API returns a list of jobs directly or under a 'jobs' key
        jobs = data if isinstance(data, list) else data.get("jobs", [])

        normalized_jobs = []

        for job in jobs:
            # Extract and normalize job data
            # Adjust field names based on actual API response
            normalized_jobs.append({
                "title": job.get("title", job.get("job_title", "")),
                "company_name": job.get("company", job.get("company_name", "")),
                "location": job.get("location", job.get("job_location", "")),
                "description": job.get("description", job.get("job_description", "")),
                "tags": job.get("skills", job.get("tags", [])) if isinstance(job.get("skills", job.get("tags", [])), list) else ([job.get("skills", job.get("tags", ""))] if job.get("skills", job.get("tags", "")) else []),
                "job_types": [job.get("job_type", "")] if job.get("job_type") else [],
                "remote": "remote" in job.get("title", job.get("job_title", "")).lower() or "remote" in job.get("location", job.get("job_location", "")).lower(),
                "url": job.get("apply_link", job.get("url", job.get("job_url", ""))),
                "source": "IndianAPI",
                "location_match": None,  # Will be calculated in filter function
                # Additional fields that might be useful
                "experience": job.get("experience", job.get("exp", "")),
                "posted_date": job.get("posted_date", job.get("date_posted", "")),
                "salary": job.get("salary", job.get("compensation", ""))
            })

        print(f"[SUCCESS] IndianAPI jobs fetched: {len(normalized_jobs)}")
        return normalized_jobs

    except Exception as error:
        print(f"[WARNING] IndianAPI failed: {error}")
        return []


# --------------------------------------------------
# LOCATION MATCHING
# --------------------------------------------------

def get_location_match(job_location, requested_location):
    """
    Determine WHY a job matches the requested location.

    Returns:
        India
        APAC
        Asia
        South Asia
        Worldwide
        City/Country name
        None
    """

    if not requested_location:
        return "Any location"

    job_location = str(job_location).lower().strip()
    requested_location = str(requested_location).lower().strip()

    # ----------------------------------------------
    # INDIA
    # ----------------------------------------------

    if requested_location == "india":

        if "india" in job_location:
            return "India"

        if "south asia" in job_location:
            return "South Asia"

        if "apac" in job_location:
            return "APAC"

        if "asia" in job_location:
            return "Asia"

        if "worldwide" in job_location:
            return "Worldwide"

        if "global" in job_location:
            return "Worldwide"

        return None

    # ----------------------------------------------
    # ANY LOCATION
    # ----------------------------------------------

    if requested_location in ["any", "anywhere"]:
        return "Any location"

    # ----------------------------------------------
    # SPECIFIC LOCATION
    # ----------------------------------------------

    if requested_location in job_location:
        return requested_location.title()

    return None


# --------------------------------------------------
# JOB TYPE MATCHING
# --------------------------------------------------

def matches_job_type(job, requested_job_type):

    if requested_job_type in ["any", None]:
        return True

    title = str(job.get("title", "")).lower()

    job_types = job.get("job_types", [])

    if not isinstance(job_types, list):
        job_types = []

    job_type_text = " ".join(
        str(item).lower()
        for item in job_types
    )

    # ----------------------------------------------
    # INTERNSHIP
    # ----------------------------------------------

    if requested_job_type == "internship":

        return (
            "intern" in title
            or "internship" in title
            or "intern" in job_type_text
            or "internship" in job_type_text
        )

    # ----------------------------------------------
    # FULL-TIME
    # ----------------------------------------------

    if requested_job_type == "full-time":

        return (
            "full-time" in job_type_text
            or "full time" in job_type_text
            or "full_time" in job_type_text
        )

    return True


# --------------------------------------------------
# WORK MODE MATCHING
# --------------------------------------------------

def matches_work_mode(job, requested_work_mode):

    if requested_work_mode in ["any", None]:
        return True

    is_remote = bool(job.get("remote", False))

    # ----------------------------------------------
    # REMOTE
    # ----------------------------------------------

    if requested_work_mode == "remote":
        return is_remote

    # ----------------------------------------------
    # ON-SITE
    # ----------------------------------------------

    if requested_work_mode == "onsite":
        return not is_remote

    return True


# --------------------------------------------------
# MAIN FETCH FUNCTION
# --------------------------------------------------

def fetch_jobs(
    location=None,
    work_mode="any",
    job_type="any"
):
    """
    Fetch jobs from multiple sources and apply filters.

    Example:

        fetch_jobs(
            location="India",
            work_mode="remote",
            job_type="any"
        )
    """

    print("\n[SEARCH] Fetching jobs from multiple sources...\n")

    all_jobs = []

    # ----------------------------------------------
    # ARBEITNOW
    # ----------------------------------------------

    try:
        arbeitnow_jobs = fetch_arbeitnow_jobs()
        all_jobs.extend(arbeitnow_jobs)

    except Exception as error:
        print(f"[WARNING] Arbeitnow failed: {error}")

    # ----------------------------------------------
    # REMOTIVE
    # ----------------------------------------------

    try:
        remotive_jobs = fetch_remotive_jobs()
        all_jobs.extend(remotive_jobs)

    except Exception as error:
        print(f"[WARNING] Remotive failed: {error}")

    # ----------------------------------------------
    # ADZUNA
    # ----------------------------------------------

    try:
        adzuna_jobs = fetch_adzuna_jobs(
            location=location,
            work_mode=work_mode,
            job_type=job_type
        )
        all_jobs.extend(adzuna_jobs)

    except Exception as error:
        # Silently fail - don't break the pipeline if Adzuna is unavailable
        pass

    # ----------------------------------------------
    # INDIAN API
    # ----------------------------------------------

    try:
        indianapi_jobs = fetch_indianapi_jobs(
            location=location,
            work_mode=work_mode,
            job_type=job_type
        )
        all_jobs.extend(indianapi_jobs)

    except Exception as error:
        # Silently fail - don't break the pipeline if IndianAPI is unavailable
        print(f"[WARNING] IndianAPI failed: {error}")
        pass

    print(
        f"\n[TOTAL] Total jobs from all sources: "
        f"{len(all_jobs)}"
    )

    # ----------------------------------------------
    # FILTER JOBS
    # ----------------------------------------------

    filtered_jobs = []

    for job in all_jobs:

        # ------------------------------------------
        # LOCATION
        # ------------------------------------------

        location_match = get_location_match(
            job.get("location", ""),
            location
        )

        if location_match is None:
            continue

        # ------------------------------------------
        # WORK MODE
        # ------------------------------------------

        if not matches_work_mode(
            job,
            work_mode
        ):
            continue

        # ------------------------------------------
        # JOB TYPE
        # ------------------------------------------

        if not matches_job_type(
            job,
            job_type
        ):
            continue

        # Save WHY the job matched
        job["location_match"] = location_match

        filtered_jobs.append(job)

    print(
        f"[FILTERED] Jobs after filters: "
        f"{len(filtered_jobs)}"
    )

    return filtered_jobs


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("\n🧪 TESTING INDIA + REMOTE")
    print("=" * 60)

    jobs = fetch_jobs(
        location="India",
        work_mode="remote",
        job_type="any"
    )

    print("\n🔥 MATCHING JOBS")
    print("=" * 60)

    for index, job in enumerate(
        jobs[:10],
        start=1
    ):

        print(
            f"\n{index}. "
            f"{job['title']}"
        )

        print(
            f"🏢 Company: "
            f"{job['company_name']}"
        )

        print(
            f"📍 Location: "
            f"{job['location']}"
        )

        print(
            f"🎯 Location Match: "
            f"{job['location_match']}"
        )

        print(
            f"🏠 Remote: "
            f"{job['remote']}"
        )

        print(
            f"📋 Type: "
            f"{job['job_types']}"
        )

        print(
            f"🌐 Source: "
            f"{job['source']}"
        )

        print(
            f"🔗 {job['url']}"
        )