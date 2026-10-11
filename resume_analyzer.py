import os
import time

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
from typing import List

load_dotenv()


# ==========================================
# Resume Profile Structure
# ==========================================

class ResumeProfile(BaseModel):
    name: str
    education: List[str]
    skills: List[str]
    experience: List[str]
    projects: List[str]
    target_roles: List[str]


# ==========================================
# Analyze Resume
# ==========================================

def analyze_resume(resume_text: str):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing from .env"
        )

    client = genai.Client(
        api_key=api_key
    )

    # ======================================
    # Prompt
    # ======================================

    prompt = f"""
You are an AI resume analyzer.

Analyze the resume below and extract structured information.

IMPORTANT RULES:

1. Only use information actually present in the resume.
2. Do not invent skills, experience, education, or projects.
3. Identify suitable entry-level job or internship roles based
   only on the candidate's actual skills, education and projects.
4. Keep the extracted information concise.
5. Return the result according to the required JSON schema.

RESUME:

{resume_text}
"""

    # ======================================
    # Models to try
    # ======================================

    models = [
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.8-flash"
]

    last_error = None

    # ======================================
    # Try models
    # ======================================

    for model in models:

        print(f"\n[MODEL] Trying Gemini model: {model}")

        for attempt in range(2):

            try:

                print(
                    f"   Attempt {attempt + 1}/2..."
                )

                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": ResumeProfile,
                    },
                )

                # ==================================
                # Convert response to profile
                # ==================================

                profile = ResumeProfile.model_validate_json(
                    response.text
                )

                print(
                    f"[SUCCESS] Resume analyzed using {model}"
                )

                return profile

            except Exception as error:

                last_error = error

                error_text = str(error)

                print(
                    f"[WARNING] {model} failed: {error_text}"
                )

                # Wait before retrying
                if attempt == 0:

                    print(
                        "⏳ Waiting before retry..."
                    )

                    time.sleep(3)

        print(
            f"➡️ Moving to next Gemini model..."
        )

    # ======================================
    # All models failed
    # ======================================

    raise RuntimeError(
        "[ERROR] All Gemini models failed.\n\n"
        f"Last error: {last_error}"
    )