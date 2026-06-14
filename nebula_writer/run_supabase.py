import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Verify required credentials are present
if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_ANON_KEY"):
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required to run with Supabase.")

os.environ["NEBULA_DB"] = "supabase"

# Add backend to path

# Run uvicorn
import uvicorn

print("Starting Nebula-Writer with Supabase...")
uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
