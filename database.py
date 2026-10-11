import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client - handle missing credentials gracefully
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = None

def _init_supabase():
    """Initialize Supabase client if credentials are available."""
    global supabase
    if supabase is None and supabase_url and supabase_key:
        try:
            supabase = create_client(supabase_url, supabase_key)
        except Exception as e:
            print(f"[WARNING] Failed to initialize Supabase client: {e}")
            supabase = None
    elif supabase is None:
        print("[WARNING] Supabase credentials not configured. User data will not be persisted.")

# Initialize on import
_init_supabase()


def get_user_profile(telegram_user_id: str):
    """Fetch user profile from Supabase by Telegram user ID."""
    if supabase is None:
        print("[WARNING] Supabase not configured. Returning None for user profile.")
        return None

    try:
        response = supabase.table('user_profiles').select('*').eq('telegram_user_id', telegram_user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"[ERROR] Failed to fetch user profile: {e}")
        return None


def save_user_profile(telegram_user_id: str, profile_data: dict):
    """Save or update user profile in Supabase."""
    if supabase is None:
        print("[WARNING] Supabase not configured. User profile not saved.")
        return None

    try:
        # Check if user exists
        existing = get_user_profile(telegram_user_id)

        if existing:
            # Update existing profile
            response = supabase.table('user_profiles').update(profile_data).eq('telegram_user_id', telegram_user_id).execute()
        else:
            # Insert new profile
            profile_data['telegram_user_id'] = telegram_user_id
            response = supabase.table('user_profiles').insert(profile_data).execute()

        return response.data
    except Exception as e:
        print(f"[ERROR] Failed to save user profile: {e}")
        return None


def get_user_location_preference(telegram_user_id: str):
    """Fetch user's location preference from Supabase."""
    if supabase is None:
        print("[WARNING] Supabase not configured. Returning None for location preference.")
        return None

    try:
        response = supabase.table('user_preferences').select('*').eq('telegram_user_id', telegram_user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"[ERROR] Failed to fetch user location preference: {e}")
        return None


def save_user_location_preference(telegram_user_id: str, location_data: dict):
    """Save or update user's location preference in Supabase."""
    if supabase is None:
        print("[WARNING] Supabase not configured. User location preference not saved.")
        return None

    try:
        # Check if preference exists
        existing = get_user_location_preference(telegram_user_id)

        if existing:
            # Update existing preference
            response = supabase.table('user_preferences').update(location_data).eq('telegram_user_id', telegram_user_id).execute()
        else:
            # Insert new preference
            location_data['telegram_user_id'] = telegram_user_id
            response = supabase.table('user_preferences').insert(location_data).execute()

        return response.data
    except Exception as e:
        print(f"[ERROR] Failed to save user location preference: {e}")
        return None


def init_database():
    """Initialize database tables if they don't exist.
    Note: In a real implementation, you would use Supabase migrations or
    manually create tables through the Supabase dashboard.
    This function is a placeholder to show what tables would be needed."""
    pass
    # In practice, you would create these tables manually:
    # 1. user_profiles table:
    #    - id (uuid, primary key)
    #    - telegram_user_id (text, unique)
    #    - name (text)
    #    - education (jsonb)
    #    - skills (jsonb)
    #    - experience (jsonb)
    #    - projects (jsonb)
    #    - target_roles (jsonb)
    #    - created_at (timestamp)
    #    - updated_at (timestamp)
    #
    # 2. user_preferences table:
    #    - id (uuid, primary key)
    #    - telegram_user_id (text, unique)
    #    - location_preference (text)
    #    - work_mode_preference (text)
    #    - job_type_preference (text)
    #    - updated_at (timestamp)