import os

# Set environment
os.environ["NEBULA_DB"] = "supabase"

# Add backend to path

# Run uvicorn
import uvicorn

print("Starting Nebula-Writer with Supabase...")
uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
