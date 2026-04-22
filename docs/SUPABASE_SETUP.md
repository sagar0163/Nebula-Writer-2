# Nebula-Writer Supabase Setup

## Step 1: Create Supabase Account

1. Go to [supabase.com](https://supabase.com)
2. Click "Start your free project"
3. Enter your email and password
4. Create a new project (e.g., "nebula-writer")
5. Wait for the project to provision (1-2 minutes)

## Step 2: Get Credentials

1. In your Supabase dashboard, go to **Settings** → **API**
2. Copy the **Project URL** (something.supabase.co)
3. Copy the **anon public** key under **Project API keys**

## Step 3: Run Schema

1. In Supabase dashboard, go to **SQL Editor**
2. Copy the contents of `backend/schema.sql`
3. Run the SQL

## Step 4: Set Environment Variables

```bash
# Linux/Mac
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_ANON_KEY=your-anon-key
export NEBULA_DB=supabase

# Optional - if using Supabase auth
export SUPABASE_SERVICE_KEY=your-service-role-key
```

Or copy `.env.example` to `.env` and fill in your values.

## Step 5: Start the Server

```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## Database Comparison

| Feature | SQLite (Local) | Supabase (Cloud) |
|---------|----------------|-----------------|
| Setup | Auto-created | Manual setup |
| Access | Local only | Anywhere |
| Sync | No | Real-time |
| Auth | None | Built-in |
| Pricing | Free | Free tier |
| Max storage | File size | 500MB free |

## Rollback

To switch back to SQLite:
```bash
export NEBULA_DB=sqlite
# or remove the NEBULA_DB variable
```