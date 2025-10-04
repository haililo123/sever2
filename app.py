from flask import Flask, request, jsonify
import os
import psycopg2
import psycopg2.extras
import json

app = Flask(__name__)

# Kết nối DB Neon (lấy từ biến môi trường Render)
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def index():
    return "✅ Flask server dùng Neon Postgres! Dùng /api/state để GET/POST state."

@app.route("/api/state", methods=["GET"])
def get_state():
    """Lấy state mới nhất từ DB"""
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT id, global_index, folder_index, processed_files, created_at
            FROM state
            ORDER BY created_at DESC
            LIMIT 1;
        """)
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            return jsonify(row)
        else:
            # Trường hợp DB trống, trả default
            return jsonify({
                "global_index": 0,
                "folder_index": {},
                "processed_files": []
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/state", methods=["POST"])
def save_state():
    """Lưu state mới vào DB"""
    try:
        data = request.get_json()

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO state (global_index, folder_index, processed_files)
            VALUES (%s, %s, %s);
        """, (
            data.get("global_index", 0),
            json.dumps(data.get("folder_index", {})),
            json.dumps(data.get("processed_files", []))
        ))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "✅ State đã lưu vào Neon Postgres thành công!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
