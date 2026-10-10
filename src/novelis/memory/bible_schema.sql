-- ====================================================================
-- Novelis Fiction Operating System (FOS)
-- Story Bible SQLite Schema (Normative Standard per NSPEC-002 v1.0.0)
-- ====================================================================

-- 1. Characters: Persistent physical and psychological profiles
CREATE TABLE IF NOT EXISTS characters (
    char_id TEXT PRIMARY KEY,               -- e.g. 'char_aria'
    canonical_name TEXT NOT NULL,           -- e.g. 'Aria Valen'
    aliases TEXT,                           -- JSON array of strings: '["The Silver Crow", "Aria"]'
    age INTEGER,
    physical_traits TEXT NOT NULL,          -- Strict immutable traits: '{"eyes": "blue", "hair": "silver", "height": "165cm"}'
    core_motivation TEXT NOT NULL,          -- Primary drive
    life_status TEXT NOT NULL CHECK(life_status IN ('ALIVE', 'DECEASED', 'MISSING', 'UNINITIALIZED')),
    created_epoch INTEGER NOT NULL DEFAULT 0,
    updated_epoch INTEGER NOT NULL DEFAULT 0
);

-- 2. Character Knowledge Scope: Mencegah kebocoran informasi antar-karakter (No Metagaming)
CREATE TABLE IF NOT EXISTS character_knowledge (
    knowledge_id TEXT PRIMARY KEY,
    char_id TEXT NOT NULL REFERENCES characters(char_id) ON DELETE CASCADE,
    proposition TEXT NOT NULL,              -- e.g. 'Father was an Imperial spy'
    learned_epoch INTEGER NOT NULL,         -- Simulation Epoch when learned
    source_entity_id TEXT,                  -- Who or what revealed it
    is_belief BOOLEAN NOT NULL DEFAULT 1    -- 1 if believed true, 0 if suspicion
);

-- 3. Locations: Geography, environment, and world laws
CREATE TABLE IF NOT EXISTS locations (
    loc_id TEXT PRIMARY KEY,                -- e.g. 'loc_sunken_temple'
    name TEXT NOT NULL,
    parent_loc_id TEXT REFERENCES locations(loc_id),
    environmental_conditions TEXT,          -- JSON: '{"climate": "subterranean humid", "hazard": "toxic spores"}'
    cultural_rules TEXT,                    -- Laws or traditions binding this location
    status TEXT NOT NULL DEFAULT 'ACCESSIBLE'
);

-- 4. Relational Matrix: Directed interpersonal edges
CREATE TABLE IF NOT EXISTS relations (
    source_char_id TEXT NOT NULL REFERENCES characters(char_id) ON DELETE CASCADE,
    target_char_id TEXT NOT NULL REFERENCES characters(char_id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,            -- e.g. 'MENTOR', 'RIVAL', 'SIBLING', 'ENEMY'
    sentiment_score REAL NOT NULL,          -- Continuous scale: -1.0 (pure hatred) to +1.0 (deep love)
    trust_score REAL NOT NULL,              -- Continuous scale: 0.0 (zero trust) to 1.0 (unconditional trust)
    notes TEXT,                             -- Contextual summary of dynamic
    updated_epoch INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (source_char_id, target_char_id)
);

-- 5. Plot Threads: Tracked narrative promises and Chekhov's guns
CREATE TABLE IF NOT EXISTS plot_threads (
    thread_id TEXT PRIMARY KEY,             -- e.g. 'thr_father_amulet'
    title TEXT NOT NULL,
    description TEXT NOT NULL,              -- The promise made to the reader
    opened_epoch INTEGER NOT NULL,
    target_resolution_epoch INTEGER,        -- Projected payoff horizon
    status TEXT NOT NULL CHECK(status IN ('OPEN', 'PROGRESSING', 'RESOLVED', 'ABANDONED')),
    payoff_condition TEXT NOT NULL,         -- What must occur to satisfy this promise
    associated_characters TEXT              -- JSON array of char_ids
);

-- 6. Timeline Events: Monotonic simulation events
CREATE TABLE IF NOT EXISTS timeline_events (
    event_id TEXT PRIMARY KEY,
    epoch_id INTEGER NOT NULL UNIQUE,
    structural_chapter_idx INTEGER NOT NULL,
    structural_scene_idx INTEGER NOT NULL,
    in_universe_timestamp TEXT,             -- e.g. 'Year 342, 14th of Sunfall, Dusk'
    summary TEXT NOT NULL,
    state_delta_json TEXT NOT NULL          -- JSON serialized delta applied to Canon
);

-- Indices for rapid query performance
CREATE INDEX IF NOT EXISTS idx_char_knowledge_char ON character_knowledge(char_id);
CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_char_id);
CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_char_id);
CREATE INDEX IF NOT EXISTS idx_plot_threads_status ON plot_threads(status);
CREATE INDEX IF NOT EXISTS idx_timeline_events_epoch ON timeline_events(epoch_id);
