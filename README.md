# AI Job Finder Telegram Bot

A Telegram bot that helps users find jobs based on their resume using AI-powered analysis and multiple job sources.

## Features

- 📄 PDF resume upload and analysis using Gemini AI
- 🔍 Job matching based on skills, experience, and roles
- 🌐 Aggregates jobs from multiple sources:
  - Arbeitnow (global remote-friendly jobs)
  - Remotive (exclusively remote jobs)
  - IndianAPI (Indian job hub for local city-specific roles)
- 💾 Persistent user data via Supabase (profiles and preferences)
- 💬 Interactive Telegram conversation flow
- 🛡️ Secure: API keys stored in environment variables, file validation

## Job Sources

1. **Arbeitnow** - Global remote-friendly job board
2. **Remotive** - Exclusively remote job listings
3. **IndianAPI** - Indian job hub providing local listings from cities like Bangalore, Mumbai, Delhi, etc.

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   GEMINI_API_KEY=your_gemini_api_key
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   INDIAN_API_KEY=your_indianapi_in_key
   ```
4. Set up Supabase tables using `supabase_setup.sql`
5. Run: `python main.py`

## Deployment

The bot is designed for 24/7 deployment on platforms like Railway or Render:

- Use the provided `Procfile` (`worker: python main.py`)
- Set environment variables in the platform dashboard
- Connect your GitHub repository for automatic deploys

## Files

- `main.py` - Bot entry point and Telegram handlers
- `job_fetcher.py` - Fetches jobs from multiple sources
- `job_matcher.py` - Resume-to-job matching algorithm
- `database.py` - Supabase integration for user persistence
- `resume_analyzer.py` - Gemini-powered resume analysis
- `job_pipeline.py` - Orchestrates fetching and matching
- `supabase_setup.sql` - Table creation for persistence
- `requirements.txt` - Python dependencies
- `Procfile` - Deployment configuration for Railway/Render

## License

MIT
