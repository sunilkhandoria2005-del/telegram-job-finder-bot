from resume_analyzer import analyze_resume
from job_pipeline import run_job_pipeline


# ============================================
# READ RESUME
# ============================================

with open(
    "data/resume.txt",
    "r",
    encoding="utf-8"
) as file:

    resume_text = file.read()


# ============================================
# ANALYZE RESUME WITH GEMINI
# ============================================

print("\n🧠 Analyzing resume...")

profile = analyze_resume(resume_text)
print("\n🎯 TARGET ROLES:")
print(profile.target_roles)

print("\n💻 SKILLS:")
print(profile.skills)

print("✅ Resume analyzed successfully")


# ============================================
# RUN JOB PIPELINE
# ============================================

matched_jobs = run_job_pipeline(profile)


# ============================================
# DISPLAY RESULTS
# ============================================

print("\n🔥 TOP MATCHING JOBS")
print("=" * 60)


if matched_jobs:

    for index, job in enumerate(
        matched_jobs[:10],
        start=1
    ):

        print(f"\n{index}. 💼 {job['title']}")
        print(f"🏢 {job['company']}")
        print(f"📍 {job['location']}")
        print(f"🎯 Match: {job['match_score']}%")
        print(f"🔗 {job['url']}")

else:

    print("😕 No matching jobs found.")