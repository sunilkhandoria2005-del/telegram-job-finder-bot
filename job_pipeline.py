from job_fetcher import fetch_jobs
from job_matcher import match_jobs


def run_job_pipeline(
    profile,
    location=None,
    work_mode="any",
    job_type="any"
):
    print("\n[SEARCH] Fetching real jobs...")

    print(f"[LOCATION] Location: {location or 'Any'}")
    print(f"[WORK_MODE] Work mode: {work_mode}")
    print(f"[JOB_TYPE] Job type: {job_type}")

    jobs = fetch_jobs(
        location=location,
        work_mode=work_mode,
        job_type=job_type
    )

    print(f"[FILTERED] Jobs after preference filtering: {len(jobs)}")

    matched_jobs = match_jobs(
        profile,
        jobs,
        minimum_score=30
    )

    print(
        f"[MATCHED] Matching jobs found: "
        f"{len(matched_jobs)}"
    )

    return matched_jobs