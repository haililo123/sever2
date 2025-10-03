# app.py
from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

# Đường dẫn file state.json (lưu cùng thư mục với app.py)
STATE_PATH = os.path.join(os.path.dirname(__file__), "state.json")

@app.route("/")
def index():
    return "✅ Server hoạt động! Dùng /api/state để GET/POST state.json"

@app.route("/api/state", methods=["GET"])
def get_state():
    """Trả về nội dung state.json nếu có, nếu không thì trả mặc định"""
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({
            "global_index": 0,
            "folder_index": {},
            "processed_files": []
        })

@app.route("/api/state", methods=["POST"])
def save_state():
    """Lưu nội dung được gửi từ client vào file state.json"""
    try:
        data = request.get_json()
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return jsonify({"message": "✅ Đã lưu state.json thành công!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
