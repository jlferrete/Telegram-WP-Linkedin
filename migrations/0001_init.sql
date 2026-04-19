PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 5000;

CREATE TABLE IF NOT EXISTS state (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS runs (
  run_id TEXT PRIMARY KEY,
  started_at TEXT NOT NULL DEFAULT (datetime('now')),
  finished_at TEXT,
  status TEXT NOT NULL CHECK (status IN ('started','success','error','partial')),
  error TEXT
);

CREATE TABLE IF NOT EXISTS updates (
  update_id INTEGER PRIMARY KEY,
  chat_id INTEGER NOT NULL,
  text TEXT NOT NULL,
  received_at TEXT NOT NULL DEFAULT (datetime('now')),
  run_id TEXT NOT NULL,
  source_payload TEXT,
  FOREIGN KEY (run_id) REFERENCES runs(run_id)
);

CREATE TABLE IF NOT EXISTS publications (
  update_id INTEGER PRIMARY KEY,
  wp_post_id TEXT,
  linkedin_post_id TEXT,
  status TEXT NOT NULL CHECK (status IN ('pending','success','failed','partial')),
  last_error TEXT,
  wp_published_at TEXT,
  linkedin_published_at TEXT,
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (update_id) REFERENCES updates(update_id)
);

CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL,
  update_id INTEGER,
  stage TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('started','success','failed','skipped','retry')),
  detail TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (run_id) REFERENCES runs(run_id),
  FOREIGN KEY (update_id) REFERENCES updates(update_id)
);

CREATE TABLE IF NOT EXISTS process_lock (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  locked INTEGER NOT NULL CHECK (locked IN (0,1)),
  owner TEXT,
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

INSERT OR IGNORE INTO process_lock (id, locked, owner) VALUES (1, 0, NULL);
INSERT OR IGNORE INTO state (key, value) VALUES ('telegram_offset', '0');

CREATE INDEX IF NOT EXISTS idx_runs_status_started_at
  ON runs(status, started_at);

CREATE INDEX IF NOT EXISTS idx_updates_run_id
  ON updates(run_id);

CREATE INDEX IF NOT EXISTS idx_publications_status_updated_at
  ON publications(status, updated_at);

CREATE INDEX IF NOT EXISTS idx_events_run_id_created_at
  ON events(run_id, created_at);

CREATE INDEX IF NOT EXISTS idx_events_update_id_stage
  ON events(update_id, stage);
