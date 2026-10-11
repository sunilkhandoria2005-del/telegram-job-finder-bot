import os
import pymupdf
from pydantic import BaseModel

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)

from resume_analyzer import analyze_resume
from job_pipeline import run_job_pipeline
from database import get_user_profile, save_user_profile, get_user_location_preference, save_user_location_preference


# ============================================
# LOAD ENVIRONMENT VARIABLES
# ============================================

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# ============================================
# START COMMAND
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    # Check if user exists in database
    existing_user = get_user_profile(user_id)
    existing_location = get_user_location_preference(user_id)

    if existing_user and existing_location:
        # Returning user with complete data
        welcome_msg = (
            "[BOT] Welcome back to AI Job Finder!\n\n"
            f"[INFO] Found your saved profile.\n"
            f"[INFO] Last location preference: {existing_location.get('location_preference', 'Not set')}\n\n"
            "[NOTE] You can:\n"
            "1. Upload a new resume to update your profile, OR\n"
            "2. Send '/use_saved' to use your saved resume data\n"
            "Then enter your location preference to search for jobs."
        )
        # Store the existing data in context for potential use
        context.user_data['existing_user_data'] = existing_user
        context.user_data['existing_location_data'] = existing_location
    elif existing_user:
        # Returning user but no location preference
        welcome_msg = (
            "[BOT] Welcome back to AI Job Finder!\n\n"
            f"[INFO] Found your saved profile.\n"
            "[INFO] No location preference found.\n\n"
            "[NOTE] Please upload a new resume to update your profile, OR\n"
            "Send '/use_saved' to use your saved resume data\n"
            "Then enter your location preference to search for jobs."
        )
        context.user_data['existing_user_data'] = existing_user
    else:
        # New user
        welcome_msg = (
            "[BOT] Welcome to AI Job Finder!\n\n"
            "I find jobs based on your resume.\n\n"
            "[NOTE] Please upload your resume as a PDF to begin."
        )

    await update.message.reply_text(welcome_msg)


# ============================================
# HANDLE RESUME
# ============================================

async def handle_resume(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    document = update.message.document

    # ----------------------------------------
    # Security: File size limit (10MB max)
    # ----------------------------------------
    if document.file_size and document.file_size > 10 * 1024 * 1024:  # 10MB
        await update.message.reply_text(
            "[ERROR] File too large. Please upload a resume smaller than 10MB."
        )
        return

    # ----------------------------------------
    # Check PDF
    # ----------------------------------------

    if document.mime_type != "application/pdf":

        await update.message.reply_text(
            "[ERROR] Please upload your resume as a PDF file."
        )

        return

    # ----------------------------------------
    # Security: Validate filename to prevent path traversal
    # ----------------------------------------
    if not document.file_name:
        await update.message.reply_text(
            "[ERROR] Invalid file. Please upload a valid PDF file."
        )
        return

    # Remove any path components from filename for security
    import os
    safe_filename = os.path.basename(document.file_name)
    # Limit filename length and remove potentially dangerous characters
    safe_filename = "".join(c for c in safe_filename if c.isalnum() or c in "._- ")[:100]
    if not safe_filename or not safe_filename.lower().endswith('.pdf'):
        safe_filename = "resume.pdf"

    # ----------------------------------------
    # Tell user resume was received
    # ----------------------------------------

    await update.message.reply_text(
        "[NOTE] Resume received!\n\n"
        "[WAIT] Reading your resume..."
    )

    try:

        # ------------------------------------
        # Download PDF
        # ------------------------------------

        telegram_file = await document.get_file()

        os.makedirs("uploads", exist_ok=True)

        file_path = os.path.join(
            "uploads",
            safe_filename
        )

        await telegram_file.download_to_drive(
            file_path
        )

        # ------------------------------------
        # Extract text from PDF
        # ------------------------------------

        pdf = pymupdf.open(file_path)

        resume_text = ""

        for page in pdf:
            resume_text += page.get_text()

        pdf.close()

        # ------------------------------------
        # Security: Limit extracted text size to prevent memory exhaustion
        # ------------------------------------
        if len(resume_text) > 500000:  # 500KB max text
            await update.message.reply_text(
                "[ERROR] Resume text is too large. Please upload a shorter resume."
            )
            # Clean up uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)
            return

        # ------------------------------------
        # Check extracted text
        # ------------------------------------

        if not resume_text.strip():

            await update.message.reply_text(
                "[ERROR] I couldn't extract text from this PDF.\n\n"
                "Please upload a text-based PDF resume."
            )

            # Clean up uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)
            return

        # ------------------------------------
        # Save extracted text
        # ------------------------------------

        os.makedirs("data", exist_ok=True)

        with open(
            "data/resume.txt",
            "w",
            encoding="utf-8"
        ) as file:

            file.write(resume_text)

        # ------------------------------------
        # Start AI analysis
        # ------------------------------------

        await update.message.reply_text(
            "[SUCCESS] Resume successfully read!\n\n"
            "🧠 Analyzing your resume with AI..."
        )

        # ------------------------------------
        # AI ANALYSIS
        # ------------------------------------

        profile = analyze_resume(resume_text)

        # ------------------------------------
        # Security: Clean up uploaded file after processing
        # ------------------------------------
        if os.path.exists(file_path):
            os.remove(file_path)

        # ------------------------------------
        # Format AI results
        # ------------------------------------

        skills = "\n".join(
            f"• {skill}"
            for skill in profile.skills
        )

        education = "\n".join(
            f"• {item}"
            for item in profile.education
        )

        experience = "\n".join(
            f"• {item}"
            for item in profile.experience
        )

        projects = "\n".join(
            f"• {item}"
            for item in profile.projects
        )

        roles = "\n".join(
            f"• {role}"
            for role in profile.target_roles
        )

        # ------------------------------------
        # Send AI analysis
        # ------------------------------------

        message = (
            "[BOT] AI RESUME ANALYSIS\n\n"

            f"👤 Name:\n"
            f"{profile.name or 'Not detected'}\n\n"

            f"🎓 Education:\n"
            f"{education or 'Not detected'}\n\n"

            f"💻 Skills:\n"
            f"{skills or 'Not detected'}\n\n"

            f"💼 Experience:\n"
            f"{experience or 'Not detected'}\n\n"

            f"🚀 Projects:\n"
            f"{projects or 'Not detected'}\n\n"

            f"🎯 Suitable Roles:\n"
            f"{roles or 'Not detected'}"
        )

        await update.message.reply_text(message)

        # ====================================
        # SAVE USER PROFILE TO DATABASE
        # ====================================

        user_id = str(update.effective_user.id)
        profile_data = {
            'name': profile.name or '',
            'education': profile.education or [],
            'skills': profile.skills or [],
            'experience': profile.experience or [],
            'projects': profile.projects or [],
            'target_roles': profile.target_roles or []
        }

        # Save profile to database
        save_result = save_user_profile(user_id, profile_data)
        if save_result:
            print(f"[INFO] User profile saved for user {user_id}")
        else:
            print(f"[WARNING] Failed to save user profile for user {user_id}")

        # ====================================
        # ASK FOR LOCATION PREFERENCE
        # ====================================

        await update.message.reply_text(
            "[LOCATION] Please enter your preferred job location (e.g., 'New York', 'London', 'Remote', 'India'):\n\n"
            "[NOTE] You can also type 'any' for no location preference."
        )

        # Store profile in context for later use
        context.user_data['resume_profile'] = profile

        return WAITING_FOR_LOCATION

    # ========================================
    # ERROR HANDLING
    # ========================================

    except Exception as error:

        print(
            "\n[ERROR] ERROR:",
            error
        )

        await update.message.reply_text(
            "[ERROR] Something went wrong while "
            "processing your resume.\n\n"
            "Please check the VS Code terminal."
        )

        # ------------------------------------
        # Security: Clean up uploaded file on error
        # ------------------------------------
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)


# ============================================
# RECEIVE LOCATION INPUT
# ============================================

async def receive_location(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """Receive location input from user and start job search."""

    user_id = str(update.effective_user.id)

    # Security: Limit input length to prevent abuse
    location_input = update.message.text.strip()[:100]  # Max 100 characters

    # Handle special case: if user just sends the suggested location (e.g., by tapping it)
    suggested_location = context.user_data.get('suggested_location')
    if suggested_location and location_input.lower() == suggested_location.lower():
        location = suggested_location
    else:
        # Validate location input
        location = location_input
        if not location:
            await update.message.reply_text(
                "[ERROR] Please provide a valid location."
            )
            return WAITING_FOR_LOCATION

        # Security: Basic input sanitization - remove potentially dangerous characters
        # Allow alphanumeric, spaces, commas, periods, hyphens, and common location symbols
        import re
        location = re.sub(r'[^\w\s,\.\-\@\#]', '', location)

    # Get the stored profile
    profile = context.user_data.get('resume_profile')

    if not profile:
        await update.message.reply_text(
            "[ERROR] Session expired. Please upload your resume again."
        )
        return ConversationHandler.END

    # Show searching message
    await update.message.reply_text(
        f"[SEARCH] Searching for jobs in: {location}\n\n"
        "[WAIT] Please wait..."
    )

    try:
        # Run job pipeline with user-provided location
        matched_jobs = run_job_pipeline(
            profile=profile,
            location=location if location.lower() != 'any' else None,
            work_mode="any",
            job_type="any"
        )

        # Clear the stored profile and suggested location
        if 'resume_profile' in context.user_data:
            del context.user_data['resume_profile']
        if 'suggested_location' in context.user_data:
            del context.user_data['suggested_location']

        # Save location preference to database
        location_data = {
            'location_preference': location,
            'work_mode_preference': 'any',
            'job_type_preference': 'any'
        }
        save_location_result = save_user_location_preference(user_id, location_data)
        if save_location_result:
            print(f"[INFO] Location preference saved for user {user_id}: {location}")
        else:
            print(f"[WARNING] Failed to save location preference for user {user_id}")

        # Send results
        if matched_jobs:
            job_message = "[BOT] TOP JOB MATCHES\n\n"

            for index, job in enumerate(
                matched_jobs[:10],
                start=1
            ):
                job_message += (
                    f"{index}. [JOB] {job['title']}\n"
                    f"[COMPANY] {job['company']}\n"
                    f"[LOCATION] {job['location']}\n"
                    f"[MATCH] {job['match_score']}%\n"
                    f"[URL] {job['url']}\n\n"
                )

            await update.message.reply_text(job_message)
        else:
            await update.message.reply_text(
                "[INFO] No matching jobs found for your location and profile.\n\n"
                "[NOTE] Try broadening your search by typing 'any' for location, "
                "or upload an updated resume with more skills."
            )

    except Exception as error:
        # Clear the stored profile on error
        if 'resume_profile' in context.user_data:
            del context.user_data['resume_profile']
        if 'suggested_location' in context.user_data:
            del context.user_data['suggested_location']

        await update.message.reply_text(
            f"[ERROR] An error occurred while searching for jobs.\n\n"
            f"[DETAILS] Please try again later."
        )
        print(f"[ERROR] Job search failed: {error}")

    return ConversationHandler.END


# ============================================
# USE SAVED PROFILE COMMAND
# ============================================

async def use_saved_profile(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """Handle the /use_saved command to use existing profile data."""

    user_id = str(update.effective_user.id)

    # Check if we have existing user data in context (from start command)
    existing_user_data = context.user_data.get('existing_user_data')
    existing_location_data = context.user_data.get('existing_location_data')

    if not existing_user_data:
        # Try to fetch from database directly
        existing_user_data = get_user_profile(user_id)
        existing_location_data = get_user_location_preference(user_id)

    if not existing_user_data:
        await update.message.reply_text(
            "[ERROR] No saved profile found. Please upload a resume first."
        )
        return

    # Convert the database record to a ResumeProfile-like object
    # Since we're going to pass this to run_job_pipeline, we need to make sure
    # it has the expected attributes

    # Create a simple object that mimics the ResumeProfile structure
    class SavedProfile:
        def __init__(self, data):
            self.name = data.get('name', '') if data else ''
            self.education = data.get('education', []) if data else []
            self.skills = data.get('skills', []) if data else []
            self.experience = data.get('experience', []) if data else []
            self.projects = data.get('projects', []) if data else []
            self.target_roles = data.get('target_roles', []) if data else []

    profile = SavedProfile(existing_user_data)

    # Store the profile in context for use in receive_location
    context.user_data['resume_profile'] = profile

    # Check if we have saved location preference
    if existing_location_data and existing_location_data.get('location_preference'):
        saved_location = existing_location_data['location_preference']
        await update.message.reply_text(
            f"[INFO] Using your saved resume profile.\n\n"
            f"[INFO] Your saved location preference is: {saved_location}\n\n"
            "[LOCATION] Would you like to use this location, or enter a different one?\n\n"
            "[NOTE] Enter a location (e.g., 'New York', 'London', 'Remote', 'India')\n"
            "or type 'any' for no preference, or just send the saved location to use it."
        )
        # Store the saved location as a default suggestion
        context.user_data['suggested_location'] = saved_location
    else:
        await update.message.reply_text(
            "[INFO] Using your saved resume profile.\n\n"
            "[LOCATION] Please enter your preferred job location (e.g., 'New York', 'London', 'Remote', 'India'):\n\n"
            "[NOTE] You can also type 'any' for no location preference."
        )

    return WAITING_FOR_LOCATION


# ============================================
# MAIN FUNCTION
# ============================================

def main():

    # ----------------------------------------
    # Check Telegram token
    # ----------------------------------------

    if not TOKEN:

        raise ValueError(
            "[ERROR] TELEGRAM_BOT_TOKEN is missing "
            "from .env"
        )

    # ----------------------------------------
    # Create Telegram application
    # ----------------------------------------

    application = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    # ----------------------------------------
    # Register /start command
    # ----------------------------------------

    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    # ----------------------------------------
    # Register PDF handler
    # ----------------------------------------

    application.add_handler(
        MessageHandler(
            filters.Document.PDF,
            handle_resume
        )
    )

    # ----------------------------------------
    # Register command handler for using saved profile
    # ----------------------------------------

    application.add_handler(
        CommandHandler("use_saved", use_saved_profile)
    )

    # ----------------------------------------
    # Register conversation handler for location input
    # ----------------------------------------

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, receive_location)],
        states={
            WAITING_FOR_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_location)]
        },
        fallbacks=[CommandHandler('start', start), CommandHandler('use_saved', use_saved_profile)]
    )

    application.add_handler(conv_handler)

    # ----------------------------------------
    # Start bot
    # ----------------------------------------

    print(
        "[BOT] AI Job Finder Bot is running..."
    )

    application.run_polling()


# ============================================
# CONVERSATION STATES
# ============================================

WAITING_FOR_LOCATION = 1


# ============================================
# RUN PROGRAM
# ============================================

if __name__ == "__main__":

    main()