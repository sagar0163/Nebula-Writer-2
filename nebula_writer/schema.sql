-- Nebula-Writer Supabase Schema
-- Run this in Supabase SQL Editor to create all tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========== CORE TABLES ==========

-- Entities (Characters, Locations, Items)
CREATE TABLE IF NOT EXISTS entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    entity_type TEXT CHECK(entity_type IN ('character', 'location', 'item')) NOT NULL,
    description TEXT,
    is_alive BOOLEAN DEFAULT true,
    current_location TEXT,
    image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Attributes (Entity properties)
CREATE TABLE IF NOT EXISTS attributes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    effective_from TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Relationships (Directed graph)
CREATE TABLE IF NOT EXISTS relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
    to_entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL,
    strength REAL DEFAULT 0.5,
    description TEXT
);

-- Events (Plot points)
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    chapter INTEGER,
    scene TEXT,
    significance TEXT DEFAULT 'normal',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chapters
CREATE TABLE IF NOT EXISTS chapters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    number INTEGER NOT NULL UNIQUE,
    title TEXT,
    content TEXT,
    summary TEXT,
    word_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Scenes
CREATE TABLE IF NOT EXISTS scenes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chapter_id UUID REFERENCES chapters(id) ON DELETE CASCADE,
    number INTEGER NOT NULL,
    beat TEXT,
    content TEXT
);

-- ========== NEW TABLES ==========

-- Chapter Versions
CREATE TABLE IF NOT EXISTS chapter_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chapter_id UUID REFERENCES chapters(id) ON DELETE CASCADE,
    content TEXT,
    word_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Character Knowledge Tracking
CREATE TABLE IF NOT EXISTS character_knowledge (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
    chapter_id UUID REFERENCES chapters(id) ON DELETE CASCADE,
    knowledge TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Story Templates
CREATE TABLE IF NOT EXISTS story_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    structure JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Consistency Issues
CREATE TABLE IF NOT EXISTS consistency_issues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chapter_id UUID REFERENCES chapters(id) ON DELETE SET NULL,
    entity_id UUID REFERENCES entities(id) ON DELETE SET NULL,
    issue_type TEXT,
    description TEXT,
    severity TEXT DEFAULT 'medium',
    resolved BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Plot Threads (NEW)
CREATE TABLE IF NOT EXISTS plot_threads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'open',
    planted_chapter INTEGER,
    resolved_chapter INTEGER,
    importance TEXT DEFAULT 'normal',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Foreshadowing (NEW)
CREATE TABLE IF NOT EXISTS foreshadowing (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plot_thread_id UUID REFERENCES plot_threads(id) ON DELETE SET NULL,
    chapter_id INTEGER,
    content TEXT NOT NULL,
    hint_level TEXT DEFAULT 'subtle',
    payoff_expected_chapter INTEGER,
    fulfilled BOOLEAN DEFAULT false,
    fulfilled_chapter INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- World Rules (NEW)
CREATE TABLE IF NOT EXISTS world_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category TEXT NOT NULL,
    rule TEXT NOT NULL,
    description TEXT,
    exceptions TEXT,
    applies_to_entities TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Voice Profiles (NEW)
CREATE TABLE IF NOT EXISTS voice_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID REFERENCES entities(id) ON DELETE CASCADE UNIQUE,
    vocabulary_level TEXT DEFAULT 'average',
    speech_patterns TEXT,
    common_phrases TEXT,
    emotional_register TEXT DEFAULT 'neutral',
    formal_level TEXT DEFAULT 'neutral',
    dialect TEXT,
    quirks TEXT,
    sample_dialogue TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Research Citations (NEW)
CREATE TABLE IF NOT EXISTS research_citations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic TEXT NOT NULL,
    fact TEXT NOT NULL,
    source TEXT,
    source_url TEXT,
    linked_entity_id UUID REFERENCES entities(id) ON DELETE SET NULL,
    linked_location TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ========== INDEXES ==========

CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
CREATE INDEX IF NOT EXISTS idx_attributes_entity ON attributes(entity_id);
CREATE INDEX IF NOT EXISTS idx_relationships_from ON relationships(from_entity_id);
CREATE INDEX IF NOT EXISTS idx_chapters_number ON chapters(number);
CREATE INDEX IF NOT EXISTS idx_plot_threads_status ON plot_threads(status);
CREATE INDEX IF NOT EXISTS idx_plot_threads_importance ON plot_threads(importance);

-- ========== DEFAULT DATA ==========

-- Insert Story Templates
INSERT INTO story_templates (name, structure) VALUES
('Three-Act Structure', '{"acts": [{"number": 1, "name": "Setup", "beats": ["Opening image", "Theme stated", "Set-up", "Catalyst"]}, {"number": 2, "name": "Confrontation", "beats": ["Debate", "Break into two", "B story", "Fun and games", "Midpoint", "Bad guys close in", "All is lost", "Dark night of the soul"]}, {"number": 3, "name": "Resolution", "beats": ["Final image", "Closure"]}]}'),
('Hero''s Journey', '{"acts": [{"name": "Act 1 - Departure", "beats": ["Ordinary world", "Call to adventure", "Refusal of call", "Meeting the mentor", "Crossing the threshold"]}, {"name": "Act 2 - Initiation", "beats": ["Tests, allies, enemies", "Ordeal", "Reward"]}, {"name": "Act 3 - Return", "beats": ["The road back", "Resurrection", "Return with elixir"]}]}'),
('Save the Cat', '{"acts": [{"name": "Act 1", "beats": ["Opening image", "Theme stated", "Set-up", "Catalyst", "Debate"]}, {"name": "Act 2A", "beats": ["Break into two", "B story", "Fun and games", "Midpoint"]}, {"name": "Act 2B", "beats": ["Bad guys close in", "All is lost", "Dark night of the soul"]}, {"name": "Act 3", "beats": ["Final image", "Finale"]}]}')
ON CONFLICT DO NOTHING;

-- ========== ROW LEVEL SECURITY (RLS) ==========

-- Enable RLS on all tables
ALTER TABLE entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE attributes ENABLE ROW LEVEL SECURITY;
ALTER TABLE relationships ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE chapters ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenes ENABLE ROW LEVEL SECURITY;
ALTER TABLE chapter_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE character_knowledge ENABLE ROW LEVEL SECURITY;
ALTER TABLE story_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE consistency_issues ENABLE ROW LEVEL SECURITY;
ALTER TABLE plot_threads ENABLE ROW LEVEL SECURITY;
ALTER TABLE foreshadowing ENABLE ROW LEVEL SECURITY;
ALTER TABLE world_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE voice_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_citations ENABLE ROW LEVEL SECURITY;

-- Allow public read/write (for demo - in production, restrict to authenticated users)
CREATE POLICY "Allow all for entities" ON entities FOR ALL USING (true);
CREATE POLICY "Allow all for attributes" ON attributes FOR ALL USING (true);
CREATE POLICY "Allow all for relationships" ON relationships FOR ALL USING (true);
CREATE POLICY "Allow all for events" ON events FOR ALL USING (true);
CREATE POLICY "Allow all for chapters" ON chapters FOR ALL USING (true);
CREATE POLICY "Allow all for scenes" ON scenes FOR ALL USING (true);
CREATE POLICY "Allow all for chapter_versions" ON chapter_versions FOR ALL USING (true);
CREATE POLICY "Allow all for character_knowledge" ON character_knowledge FOR ALL USING (true);
CREATE POLICY "Allow all for story_templates" ON story_templates FOR ALL USING (true);
CREATE POLICY "Allow all for consistency_issues" ON consistency_issues FOR ALL USING (true);
CREATE POLICY "Allow all for plot_threads" ON plot_threads FOR ALL USING (true);
CREATE POLICY "Allow all for foreshadowing" ON foreshadowing FOR ALL USING (true);
CREATE POLICY "Allow all for world_rules" ON world_rules FOR ALL USING (true);
CREATE POLICY "Allow all for voice_profiles" ON voice_profiles FOR ALL USING (true);
CREATE POLICY "Allow all for research_citations" ON research_citations FOR ALL USING (true);