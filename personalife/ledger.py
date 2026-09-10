"""Append-only canonical ledger. Commands serialize with BEGIN IMMEDIATE."""
import hashlib
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4
from .clock import stamp

def encode(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)

class Ledger:
    def __init__(self, path):
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, timeout=30, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS schema_version(version INTEGER PRIMARY KEY);
        INSERT OR IGNORE INTO schema_version VALUES(1);
        CREATE TABLE IF NOT EXISTS events(
          seq INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT UNIQUE NOT NULL,
          persona TEXT NOT NULL, at TEXT NOT NULL, kind TEXT NOT NULL,
          data TEXT NOT NULL, previous_hash TEXT NOT NULL, hash TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS events_persona ON events(persona,seq);
        CREATE TRIGGER IF NOT EXISTS immutable_update BEFORE UPDATE ON events
          BEGIN SELECT RAISE(ABORT,'Canonical events cannot be rewritten'); END;
        CREATE TRIGGER IF NOT EXISTS immutable_delete BEFORE DELETE ON events
          BEGIN SELECT RAISE(ABORT,'Canonical events cannot be deleted'); END;
        ''')
        if self.db.execute("SELECT MAX(version) FROM schema_version").fetchone()[0] != 1:
            raise ValueError("Unsupported database schema")

    @contextmanager
    def transaction(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield
        except BaseException:
            self.db.rollback()
            raise
        else:
            self.db.commit()

    def append(self, persona, at, kind, data, event_id=None):
        if not self.db.in_transaction:
            raise RuntimeError("Append requires a command transaction")
        event_id = event_id or str(uuid4())
        payload = encode(data)
        at = stamp(at)
        prior = self.db.execute("SELECT hash FROM events ORDER BY seq DESC LIMIT 1").fetchone()
        previous = prior[0] if prior else ""
        digest = hashlib.sha256(encode([event_id, persona, at, kind, payload, previous]).encode()).hexdigest()
        self.db.execute("INSERT INTO events(id,persona,at,kind,data,previous_hash,hash) VALUES(?,?,?,?,?,?,?)",
                        (event_id, persona, at, kind, payload, previous, digest))
        return event_id

    def read(self, persona=None, after=0, through=None):
        clauses = ["seq > ?"]
        params = [after]
        if persona is not None:
            clauses.append("persona=?")
            params.append(persona)
        if through is not None:
            clauses.append("seq <= ?")
            params.append(through)
        rows = self.db.execute("SELECT * FROM events WHERE " + " AND ".join(clauses) + " ORDER BY seq", params)
        return [{**dict(r), "data": json.loads(r["data"])} for r in rows]

    def verify(self):
        previous = ""
        for r in self.read():
            digest = hashlib.sha256(encode([r["id"], r["persona"], r["at"], r["kind"], encode(r["data"]), previous]).encode()).hexdigest()
            if r["previous_hash"] != previous or digest != r["hash"]:
                raise ValueError("Ledger hash chain mismatch")
            previous = digest
        return True

    def backup(self, destination):
        with sqlite3.connect(destination) as target:
            self.db.backup(target)

    def close(self):
        self.db.close()
