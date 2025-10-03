# server_state.py
import json
import sqlite3
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Shared State Server")

# cho phép mọi client trong LAN truy cập
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "state.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS state (
        id INTEGER PRIMARY KEY,
        data TEXT
    )
    """)
    cur.execute("INSERT OR IGNORE INTO state (id, data) VALUES (1, ?)", 
                (json.dumps({"global_index": 0, "folder_index": {}, "processed_files": []}),))
    conn.commit()
    conn.close()

init_db()

class StateUpdate(BaseModel):
    data: dict

@app.get("/state")
def get_state():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT data FROM state WHERE id=1")
    row = cur.fetchone()
    conn.close()
    return json.loads(row[0]) if row else {}

@app.post("/state/update")
def update_state(payload: StateUpdate):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE state SET data=? WHERE id=1", (json.dumps(payload.data),))
    conn.commit()
    conn.close()
    return {"status": "ok"}
