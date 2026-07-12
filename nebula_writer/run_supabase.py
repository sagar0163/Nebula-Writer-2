import os

from dotenv import load_dotenv

load_dotenv()

# Run uvicorn
import uvicorn

print("Starting Nebula-Writer with Supabase...")
uvicorn.run("nebula_writer.main:app", host="0.0.0.0", port=8000, reload=False)
