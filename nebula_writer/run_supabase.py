import os

# Set environment
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables must be set.")

os.environ["SUPABASE_URL"] = supabase_url
os.environ["SUPABASE_ANON_KEY"] = supabase_key
os.environ["NEBULA_DB"] = "supabase"

# Add backend to path

# Run uvicorn
import uvicorn

print("Starting Nebula-Writer with Supabase...")
uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
