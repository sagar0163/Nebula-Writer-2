import os
import sys

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Verify environment
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set in the environment or .env file.")
    sys.exit(1)

os.environ["NEBULA_DB"] = "supabase"

# Add backend to path

# Run uvicorn
import uvicorn

print("Starting Nebula-Writer with Supabase...")
uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
