import re
from html import unescape


# ============================================
# SKILL / TERM ALIASES
# ============================================

ALIASES = {
    "python": ["python"],
    "sql": ["sql", "mysql", "postgresql", "postgres"],

    "machine learning": [
        "machine learning",
        "ml",
        "machine-learning"
    ],

    "artificial intelligence": [
        "artificial intelligence",
        "ai"
    ],

    "data analysis": [
        "data analysis",
        "data analytics",
        "data analyst"
    ],

    "data analytics": [
        "data analytics",
        "data analysis",
        "data analyst"
    ],

    "prompt engineering": [
        "prompt engineering",
        "prompt engineer"
    ],

    "llm": [
        "llm",
        "large language model",
        "large language models"
    ],

    "ai agents": [
        "ai agent",
        "ai agents",
        "agentic ai"
    ],

    "workflow automation": [
        "workflow automation",
        "automation"
    ],

    "n8n": [
        "n8n"
    ],

    "rest api": [
        "rest api",
        "restful api",
        "api integration"
    ],

    "excel": [
        "excel",
        "microsoft excel"
    ],

    "git": [
        "git"
    ],

    "github": [
        "github"
    ],

    "supabase": [
        "supabase"
    ],

    "postgresql": [
        "postgresql",
        "postgres"
    ],

    # Business & Management
    "management": ["management", "manager", "managing"],
    "marketing": ["marketing", "marketer", "market", "marketing management"],
    "sales": ["sales", "selling", "sales representative", "account executive"],
    "finance": ["finance", "financial", "banking", "investment"],
    "human resources": ["human resources", "hr", "personnel", "talent acquisition"],
    "project management": ["project management", "project manager", "pmp"],
    "operations": ["operations", "operational", "office management"],
    "administration": ["administration", "administrative", "admin"],
    "customer service": ["customer service", "client service", "support", "help desk"],

    # Design & Creative
    "design": ["design", "designer", "designing"],
    "graphic design": ["graphic design", "graphic designer", "visual design"],
    "ui ux": ["ui ux", "ui/ux", "user interface", "user experience", "ui designer", "ux designer"],
    "web design": ["web design", "web designer"],
    "fashion design": ["fashion design", "fashion designer"],
    "interior design": ["interior design", "interior designer"],
    "content writing": ["content writing", "content writer", "copywriting", "copywriter"],
    "journalism": ["journalism", "journalist", "news", "reporting"],
    "public relations": ["public relations", "pr", "media relations"],
    "media": ["media", "multimedia", "broadcasting"],

    # Technology (additional)
    "software development": ["software development", "software engineer", "programming", "developer"],
    "web development": ["web development", "web developer", "frontend", "backend"],
    "data science": ["data science", "data scientist", "analytics"],
    "database administration": ["database administration", "dba", "database administrator"],
    "network engineering": ["network engineering", "network engineer", "it support"],
    "cybersecurity": ["cybersecurity", "information security", "infosec"],
    "quality assurance": ["quality assurance", "qa", "testing", "test engineer"],

    # Healthcare
    "healthcare": ["healthcare", "medical", "health"],
    "nursing": ["nursing", "nurse", "rn", "lpn"],
    "medical assistant": ["medical assistant", "clinical assistant"],
    "pharmacy": ["pharmacy", "pharmacist", "pharmaceutical"],

    # Education
    "education": ["education", "teaching", "teacher", "educator", "instructor"],
    "training": ["training", "trainer", "facilitator"],
    "academic": ["academic", "research", "scholar"],

    # Engineering
    "engineering": ["engineering", "engineer"],
    "mechanical engineering": ["mechanical engineering", "mechanical engineer"],
    "electrical engineering": ["electrical engineering", "electrical engineer"],
    "civil engineering": ["civil engineering", "civil engineer"],
    "chemical engineering": ["chemical engineering", "chemical engineer"],

    # Legal
    "legal": ["legal", "lawyer", "attorney", "counsel", "paralegal"],
    "compliance": ["compliance", "regulatory", "governance"],

    # Finance & Accounting
    "accounting": ["accounting", "accountant", "bookkeeping"],
    "audit": ["audit", "auditor"],
    "tax": ["tax", "taxation", "tax accountant"],

    # Supply Chain & Logistics
    "logistics": ["logistics", "logistic", "supply chain", "warehouse"],
    "procurement": ["procurement", "purchasing", "buyer"],
    "transportation": ["transportation", "transport", "driver", "delivery"],

    # Real Estate & Construction
    "real estate": ["real estate", "realtor", "property", "real estate agent"],
    "construction": ["construction", "construction worker", "contractor", "site supervisor"],

    # Non-profit & Social Services
    "nonprofit": ["nonprofit", "not-for-profit", "ngo", "charity"],
    "social work": ["social work", "social worker", "case manager"],
    "counseling": ["counseling", "counselor", "therapy", "therapist", "psychology"],

    # Hospitality & Tourism
    "hospitality": ["hospitality", "hotel", "restaurant", "food service"],
    "tourism": ["tourism", "tourist", "travel", "hospitality management"],
    "event planning": ["event planning", "event coordinator", "meeting planner"],
}


# ============================================
# CLEAN HTML
# ============================================

def clean_html(text):
    if not text:
        return ""

    text = unescape(text)

    text = re.sub(
        r"<(script|style).*?>.*?</\1>",
        " ",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    text = re.sub(r"<[^>]+>", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip().lower()


# ============================================
# NORMALIZE TEXT
# ============================================

def normalize(text):
    text = str(text).lower()

    text = text.replace("-", " ")
    text = text.replace("/", " ")
    text = text.replace(".", " ")
    text = text.replace("_", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================
# WORD / TERM MATCHING
# ============================================

def contains_term(term, text):

    term = normalize(term)
    text = normalize(text)

    if not term:
        return False

    pattern = r"\b" + re.escape(term) + r"\b"

    return re.search(pattern, text) is not None


# ============================================
# CHECK SKILL MATCH
# ============================================

def term_matches(term, job_text):

    term = normalize(term)

    # Direct match
    if contains_term(term, job_text):
        return True

    # Alias match
    aliases = ALIASES.get(term, [])

    for alias in aliases:

        if contains_term(alias, job_text):
            return True

    return False


# ============================================
# ROLE MATCHING
# ============================================

def calculate_role_score(target_roles, job_title):

    if not target_roles:
        return 0, []

    title = normalize(job_title)

    matched_roles = []
    best_role_score = 0

    for role in target_roles:

        role_normalized = normalize(role)

        # Exact title match
        if contains_term(role_normalized, title):

            matched_roles.append(role)

            best_role_score = max(
                best_role_score,
                100
            )

            continue

        # Role contains job title (reverse matching)
        if contains_term(title, role_normalized):

            matched_roles.append(role)

            best_role_score = max(
                best_role_score,
                90  # Slightly lower than exact match but still high
            )

            continue

        # Compare important words
        role_words = [
            word
            for word in role_normalized.split()
            if len(word) > 2
        ]

        title_words = [
            word
            for word in title.split()
            if len(word) > 2
        ]

        if not role_words and not title_words:
            continue

        # Calculate bidirectional word matching
        role_in_title = sum(
            1
            for word in role_words
            if contains_term(word, title)
        )

        title_in_role = sum(
            1
            for word in title_words
            if contains_term(word, role_normalized)
        )

        # Calculate scores for both directions
        role_word_score = (
            role_in_title / len(role_words)
        ) * 100 if role_words else 0

        title_word_score = (
            title_in_role / len(title_words)
        ) * 100 if title_words else 0

        # Take the better of the two directional scores
        word_score = max(role_word_score, title_word_score)

        if word_score > 0:

            matched_roles.append(role)

            best_role_score = max(
                best_role_score,
                word_score
            )

    return round(best_role_score), matched_roles


# ============================================
# CANDIDATE EXPERIENCE LEVEL
# ============================================

def get_candidate_level(profile):

    target_roles = profile.target_roles or []
    experience = profile.experience or []

    role_text = " ".join(target_roles).lower()
    experience_text = " ".join(experience).lower()

    # Expanded junior keywords for various fields
    junior_keywords = [
        "intern",
        "internship",
        "entry level",
        "entry-level",
        "junior",
        "fresher",
        "trainee",
        "graduate",
        "associate",
        "assistant",
        "aide",
        "coordinator",
        "specialist",
        "analyst",
        "officer",
        "representative",
        "assistant",
        "junior",
        "entry",
        "beginner"
    ]

    for keyword in junior_keywords:

        if keyword in role_text:
            return "junior"

    # Expanded senior keywords for various fields
    senior_keywords = [
        "senior",
        "lead",
        "principal",
        "director",
        "head",
        "chief",
        "manager",
        "supervisor",
        "controller",
        "officer",
        "executive",
        "vp",
        "vice president",
        "president",
        "CEO",
        "CFO",
        "CTO",
        "partner",
        "owner",
        "founder",
        "manager",
        "supervisor",
        "head of",
        "in charge"
    ]

    for keyword in senior_keywords:
        if keyword in role_text:
            return "senior"

    year_matches = re.findall(
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
        experience_text
    )

    if year_matches:

        try:

            max_years = max(
                float(value)
                for value in year_matches
            )

            if max_years >= 5:
                return "senior"

            if max_years >= 2:
                return "mid"

        except ValueError:
            pass

    return "junior"


# ============================================
# JOB EXPERIENCE LEVEL
# ============================================

def get_job_level(job_title, description):

    text = normalize(
        f"{job_title} {description}"
    )

    # Expanded senior keywords for various fields
    senior_keywords = [
        "senior",
        "sr ",
        "lead",
        "principal",
        "director",
        "head of",
        "chief",
        "manager",
        "supervisor",
        "controller",
        "officer",
        "executive",
        "vp",
        "vice president",
        "president",
        "partner",
        "owner",
        "founder",
        "head",
        "in charge",
        "controller",
        "director",
        "head of department",
        "manager",
        "supervisor"
    ]

    for keyword in senior_keywords:
        if keyword in text:
            return "senior"

    # Expanded junior keywords for various fields
    junior_keywords = [
        "intern",
        "internship",
        "entry level",
        "entry-level",
        "junior",
        "trainee",
        "graduate",
        "associate",
        "assistant",
        "aide",
        "coordinator",
        "specialist",
        "analyst",
        "officer",
        "representative",
        "assistant",
        "junior",
        "entry",
        "beginner",
        "staff",
        "associate"
    ]

    for keyword in junior_keywords:
        if keyword in text:
            return "junior"

    return "mid"


# ============================================
# EXPERIENCE COMPATIBILITY
# ============================================

def experience_adjustment(
    candidate_level,
    job_level
):

    if (
        candidate_level == "junior"
        and job_level == "senior"
    ):
        return -25

    if (
        candidate_level == "senior"
        and job_level == "junior"
    ):
        return -10

    if (
        candidate_level == "mid"
        and job_level == "senior"
    ):
        return -10

    if candidate_level == job_level:
        return 5

    return 0


# ============================================
# CALCULATE MATCH SCORE
# ============================================

def calculate_match_score(profile, job):

    candidate_skills = profile.skills or []
    target_roles = profile.target_roles or []

    title = job.get("title", "")
    description = job.get("description", "")
    tags = job.get("tags", [])

    if not isinstance(tags, list):
        tags = []

    # Build job text
    cleaned_description = clean_html(description)

    tag_text = normalize(
        " ".join(tags)
    )

    job_text = " ".join([
        normalize(title),
        cleaned_description,
        tag_text
    ])

    # ========================================
    # SKILL MATCHING
    # ========================================

    matched_skills = []

    for skill in candidate_skills:

        if term_matches(
            skill,
            job_text
        ):
            matched_skills.append(skill)

    # ========================================
    # SKILL SCORE
    # ========================================

    skill_score = 0

    if candidate_skills:

        skill_score = (
            len(matched_skills)
            / len(candidate_skills)
        ) * 100

    # ========================================
    # ROLE SCORE
    # ========================================

    role_score, matched_roles = calculate_role_score(
        target_roles,
        title
    )

    # ========================================
    # EXPERIENCE LEVEL
    # ========================================

    candidate_level = get_candidate_level(profile)

    job_level = get_job_level(
        title,
        description
    )

    experience_change = experience_adjustment(
        candidate_level,
        job_level
    )

    # ========================================
    # IMPROVED SCORING ALGORITHM
    # ========================================
    # Dynamic weighting based on profile completeness
    # Ensures fair evaluation across different fields

    # Base weights - can be adjusted based on available data
    skill_weight = 0.50
    role_weight = 0.40
    experience_weight = 0.10

    # Adjust weights if certain data is missing
    if not candidate_skills:
        # If no skills, rely more on role matching
        skill_weight = 0.30
        role_weight = 0.60
        experience_weight = 0.10
    elif not target_roles:
        # If no target roles, rely more on skill matching
        skill_weight = 0.70
        role_weight = 0.20
        experience_weight = 0.10

    # Calculate weighted components
    skill_component = skill_score * skill_weight
    role_component = role_score * role_weight

    # Experience component - positive for compatibility, negative for mismatch
    if experience_change >= 0:
        experience_component = experience_change * 2  # Positive experience gets boost
    else:
        experience_component = experience_change  # Negative experience penalized directly

    # Calculate base score
    base_score = skill_component + role_component + experience_component

    # Apply experience penalties if negative
    if experience_change < 0:
        final_score = base_score + experience_change  # Additional penalty
    else:
        final_score = base_score

    # Ensure score is within bounds
    final_score = max(0, min(100, round(final_score)))

    # ========================================
    # BONUS FOR HIGH QUALITY MATCHES
    # ========================================
    # Give bonus points for exceptional matches in key areas

    # Skill match bonus: if 80%+ skills match, add bonus
    if skill_score >= 80 and candidate_skills:
        final_score = min(100, final_score + 5)

    # Role match bonus: if 80%+ role match, add bonus
    if role_score >= 80 and target_roles:
        final_score = min(100, final_score + 5)

    # Perfect experience match bonus
    if experience_change > 0 and candidate_level == job_level:
        final_score = min(100, final_score + 5)

    # Ensure final score is within bounds after bonuses
    final_score = max(0, min(100, round(final_score)))

    return {
        "score": final_score,
        "matched_skills": matched_skills,
        "matched_roles": matched_roles,
        "candidate_level": candidate_level,
        "job_level": job_level,
        "skill_score": round(skill_score),
        "role_score": role_score,
    }


# ============================================
# MATCH ALL JOBS
# ============================================

def match_jobs(
    profile,
    jobs,
    minimum_score=30
):

    matched_jobs = []

    for job in jobs:

        result = calculate_match_score(
            profile,
            job
        )

        score = result["score"]

        if score >= minimum_score:

            job_result = {

                "title": job.get(
                    "title",
                    "Unknown"
                ),

                "company": job.get(
                    "company_name",
                    "Unknown"
                ),

                "location": job.get(
                    "location",
                    "Unknown"
                ),

                "remote": job.get(
                    "remote",
                    False
                ),

                "url": job.get(
                    "url",
                    ""
                ),

                # NEW
                "source": job.get(
                    "source",
                    "Unknown"
                ),

                # NEW
                "location_match": job.get(
                    "location_match",
                    "Unknown"
                ),

                "match_score": score,

                "matched_skills": result[
                    "matched_skills"
                ],

                "matched_roles": result[
                    "matched_roles"
                ],

                "candidate_level": result[
                    "candidate_level"
                ],

                "job_level": result[
                    "job_level"
                ],

                "skill_score": result[
                    "skill_score"
                ],

                "role_score": result[
                    "role_score"
                ],
            }

            matched_jobs.append(
                job_result
            )

    # ========================================
    # SORT BEST MATCHES FIRST
    # ========================================

    matched_jobs.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return matched_jobs