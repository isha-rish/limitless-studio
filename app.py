import os
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "limitless_writer_vault_secret_key"

DB_FILE = "vault.json"

# Default Database Structure if vault.json doesn't exist
DEFAULT_DB = {
    "users": {
        "creator": {
            "password": "password123",
            "books": [
                {
                    "id": 1,
                    "title": "The Infinite Starfall",
                    "genre": "Sci-Fi",
                    "format": "long", # 'short' or 'long'
                    "description": "An epic journey across the galaxy.",
                    "single_content": "", # Used if format is 'short'
                    "chapters": [
                        {"id": 1, "title": "Chapter 1: Ignition", "content": "The stars burned brighter than usual that night..."}
                    ],
                    "characters": [
                        {"id": 1, "name": "Captain Vexa", "role": "Commander", "description": "Fearless explorer of the void."}
                    ],
                    "worldbuilding": [
                        {"id": 1, "title": "Sector 4", "content": "A lawless cluster of floating space stations."}
                    ],
                    "storyboard": "Act 1: Launch\nAct 2: The Anomaly\nAct 3: Discovery"
                }
            ]
        }
    }
}

def load_db():
    if not os.path.exists(DB_FILE):
        save_db(DEFAULT_DB)
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return DEFAULT_DB

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    if "user" not in session:
        return render_template('login.html')
    return render_template('index.html', username=session["user"])

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    
    db = load_db()
    if username in db["users"] and db["users"][username]["password"] == password:
        session["user"] = username
        return jsonify({"status": "success"})
    elif username not in db["users"] and username:
        # Register new user automatically
        db["users"][username] = {"password": password, "books": []}
        save_db(db)
        session["user"] = username
        return jsonify({"status": "success"})
    
    return jsonify({"status": "error", "message": "Invalid credentials."}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop("user", None)
    return jsonify({"status": "success"})

@app.route('/api/load', methods=['GET'])
def get_user_data():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    db = load_db()
    user = session["user"]
    return jsonify({"username": user, "books": db["users"][user]["books"]})

@app.route('/api/save', methods=['POST'])
def save_user_data():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    db = load_db()
    user = session["user"]
    data = request.json
    if "books" in data:
        db["users"][user]["books"] = data["books"]
        save_db(db)
    return jsonify({"status": "success", "message": "Vault successfully synchronized."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)