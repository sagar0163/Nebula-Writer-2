import os
import sys

# Ensure environment variables are provided
if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_ANON_KEY"):
    print("Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set in the environment variables.", file=sys.stderr)
    sys.exit(1)

os.environ["NEBULA_DB"] = "supabase"

# Add backend to path

# Run uvicorn
import uvicorn

print("Starting Nebula-Writer with Supabase...")
uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
