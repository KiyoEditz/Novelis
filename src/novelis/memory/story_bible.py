"""Novelis Story Bible (Relational Hard Canon Engine)
Normative SQLite Implementation per NSPEC-002 v1.0.0.
"""

from pathlib import Path
import sqlite3
import json
from typing import Any, Optional, Dict, List
from novelis.config import config


class StoryBible:
    """Authoritative relational storage for Hard Canon entities, world rules,
    character relationships, epistemic knowledge, and plot threads.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or config.STORY_BIBLE_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a configured SQLite connection with foreign keys enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_database(self) -> None:
        """Initializes tables using bible_schema.sql if not already present."""
        schema_file = Path(__file__).parent / "bible_schema.sql"
        if schema_file.exists():
            with open(schema_file, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            with self._get_connection() as conn:
                conn.executescript(schema_sql)

    # -------------------------------------------------------------------------
    # Character Operations
    # -------------------------------------------------------------------------

    def upsert_character(
        self,
        char_id: str,
        canonical_name: str,
        physical_traits: Dict[str, Any],
        core_motivation: str,
        age: Optional[int] = None,
        aliases: Optional[List[str]] = None,
        life_status: str = "ALIVE",
        epoch: int = 0
    ) -> None:
        """Inserts or updates a persistent character profile."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO characters (
                    char_id, canonical_name, aliases, age, physical_traits,
                    core_motivation, life_status, created_epoch, updated_epoch
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(char_id) DO UPDATE SET
                    canonical_name = excluded.canonical_name,
                    aliases = excluded.aliases,
                    age = excluded.age,
                    physical_traits = excluded.physical_traits,
                    core_motivation = excluded.core_motivation,
                    life_status = excluded.life_status,
                    updated_epoch = excluded.updated_epoch;
                """,
                (
                    char_id,
                    canonical_name,
                    json.dumps(aliases or []),
                    age,
                    json.dumps(physical_traits),
                    core_motivation,
                    life_status,
                    epoch,
                    epoch
                )
            )

    def get_character(self, char_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a character record by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM characters WHERE char_id = ?", (char_id,))
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            data["aliases"] = json.loads(data["aliases"]) if data["aliases"] else []
            data["physical_traits"] = json.loads(data["physical_traits"]) if data["physical_traits"] else {}
            return data

    def get_characters(self, char_ids: List[str]) -> List[Dict[str, Any]]:
        """Batch retrieves characters by IDs."""
        if not char_ids:
            return []
        placeholders = ",".join("?" for _ in char_ids)
        with self._get_connection() as conn:
            cursor = conn.execute(f"SELECT * FROM characters WHERE char_id IN ({placeholders})", char_ids)
            results = []
            for row in cursor.fetchall():
                data = dict(row)
                data["aliases"] = json.loads(data["aliases"]) if data["aliases"] else []
                data["physical_traits"] = json.loads(data["physical_traits"]) if data["physical_traits"] else {}
                results.append(data)
            return results

    # -------------------------------------------------------------------------
    # Epistemic Knowledge Operations (No Metagaming)
    # -------------------------------------------------------------------------

    def add_knowledge(
        self,
        knowledge_id: str,
        char_id: str,
        proposition: str,
        learned_epoch: int,
        source_entity_id: Optional[str] = None,
        is_belief: bool = True
    ) -> None:
        """Records a new fact or belief acquired by a character."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO character_knowledge (
                    knowledge_id, char_id, proposition, learned_epoch, source_entity_id, is_belief
                ) VALUES (?, ?, ?, ?, ?, ?);
                """,
                (knowledge_id, char_id, proposition, learned_epoch, source_entity_id, 1 if is_belief else 0)
            )

    def get_character_knowledge(self, char_id: str) -> List[Dict[str, Any]]:
        """Retrieves all propositions known/believed by a character."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM character_knowledge WHERE char_id = ? ORDER BY learned_epoch ASC",
                (char_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    # -------------------------------------------------------------------------
    # Location Operations
    # -------------------------------------------------------------------------

    def upsert_location(
        self,
        loc_id: str,
        name: str,
        parent_loc_id: Optional[str] = None,
        environmental_conditions: Optional[Dict[str, Any]] = None,
        cultural_rules: Optional[str] = None,
        status: str = "ACCESSIBLE"
    ) -> None:
        """Inserts or updates a world location."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO locations (
                    loc_id, name, parent_loc_id, environmental_conditions, cultural_rules, status
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(loc_id) DO UPDATE SET
                    name = excluded.name,
                    parent_loc_id = excluded.parent_loc_id,
                    environmental_conditions = excluded.environmental_conditions,
                    cultural_rules = excluded.cultural_rules,
                    status = excluded.status;
                """,
                (
                    loc_id,
                    name,
                    parent_loc_id,
                    json.dumps(environmental_conditions or {}),
                    cultural_rules,
                    status
                )
            )

    def get_location(self, loc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a location by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM locations WHERE loc_id = ?", (loc_id,))
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            data["environmental_conditions"] = json.loads(data["environmental_conditions"]) if data["environmental_conditions"] else {}
            return data

    # -------------------------------------------------------------------------
    # Interpersonal Relations
    # -------------------------------------------------------------------------

    def set_relation(
        self,
        source_char_id: str,
        target_char_id: str,
        relation_type: str,
        sentiment_score: float,
        trust_score: float,
        notes: Optional[str] = None,
        epoch: int = 0
    ) -> None:
        """Updates or establishes a directed relationship between characters."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO relations (
                    source_char_id, target_char_id, relation_type,
                    sentiment_score, trust_score, notes, updated_epoch
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_char_id, target_char_id) DO UPDATE SET
                    relation_type = excluded.relation_type,
                    sentiment_score = excluded.sentiment_score,
                    trust_score = excluded.trust_score,
                    notes = excluded.notes,
                    updated_epoch = excluded.updated_epoch;
                """,
                (source_char_id, target_char_id, relation_type, sentiment_score, trust_score, notes, epoch)
            )

    def get_relations_for_character(self, char_id: str) -> List[Dict[str, Any]]:
        """Retrieves all outgoing relationship edges for a character."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM relations WHERE source_char_id = ? ORDER BY trust_score DESC",
                (char_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    # -------------------------------------------------------------------------
    # Plot Threads (Tracked Narrative Promises)
    # -------------------------------------------------------------------------

    def add_plot_thread(
        self,
        thread_id: str,
        title: str,
        description: str,
        opened_epoch: int,
        payoff_condition: str,
        target_resolution_epoch: Optional[int] = None,
        status: str = "OPEN",
        associated_characters: Optional[List[str]] = None
    ) -> None:
        """Registers a new narrative promise or Chekhov's gun."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO plot_threads (
                    thread_id, title, description, opened_epoch, target_resolution_epoch,
                    status, payoff_condition, associated_characters
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    thread_id,
                    title,
                    description,
                    opened_epoch,
                    target_resolution_epoch,
                    status,
                    payoff_condition,
                    json.dumps(associated_characters or [])
                )
            )

    def get_open_plot_threads(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves active (OPEN or PROGRESSING) plot promises."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM plot_threads
                WHERE status IN ('OPEN', 'PROGRESSING')
                ORDER BY opened_epoch ASC LIMIT ?
                """,
                (limit,)
            )
            results = []
            for row in cursor.fetchall():
                data = dict(row)
                data["associated_characters"] = json.loads(data["associated_characters"]) if data["associated_characters"] else []
                results.append(data)
            return results

    def update_plot_thread_status(self, thread_id: str, status: str) -> None:
        """Updates the lifecycle status of a plot thread."""
        with self._get_connection() as conn:
            conn.execute("UPDATE plot_threads SET status = ? WHERE thread_id = ?", (status, thread_id))

    # -------------------------------------------------------------------------
    # Timeline Events & Atomic Delta Commits
    # -------------------------------------------------------------------------

    def record_timeline_event(
        self,
        event_id: str,
        epoch_id: int,
        chapter_idx: int,
        scene_idx: int,
        summary: str,
        state_delta: Dict[str, Any],
        in_universe_timestamp: Optional[str] = None
    ) -> None:
        """Records an immutable simulation event to the timeline."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO timeline_events (
                    event_id, epoch_id, structural_chapter_idx, structural_scene_idx,
                    in_universe_timestamp, summary, state_delta_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    event_id,
                    epoch_id,
                    chapter_idx,
                    scene_idx,
                    in_universe_timestamp,
                    summary,
                    json.dumps(state_delta)
                )
            )
