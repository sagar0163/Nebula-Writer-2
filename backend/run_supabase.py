import os
import sys
from pathlib import Path

# Set environment
os.environ['SUPABASE_URL'] = 'https://slovnfrjidipspogvktb.supabase.co'
os.environ['SUPABASE_ANON_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNsMW5mcmppZGlwc3BvZ3ZrdGIiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTc0NjMxMDY1MCwiZXhwIjoxOTYxODg2NjUwfQ.sb_publishable_MC-oV3wdAsZDVnkWSMqKYQ_KngPn_-J'
os.environ['NEBULA_DB'] = 'supabase'

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Run uvicorn
import uvicorn
print("Starting Nebula-Writer with Supabase...")
uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)