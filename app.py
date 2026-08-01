import os
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "limitless_writer_vault_secret_key"

DB_FILE = "vault.json"

DEFAULT_DB = {
    "users": {
        "creator": {
            "password": "password123",
            "books": [
                {
                    "id": 1,
                    "title": "The Infinite Starfall",
                    "genre": "Sci-Fi",
                    "description": "An epic journey across the galaxy.",
                    "chapters": [
                        {"id": 1, "title": "Chapter 1: Ignition", "content": "The stars burned brighter than usual that night..."}
                    ],
                    "characters": [
                        {"id": 1, "name": "Captain Vexa", "role": "Commander", "description": "Fearless explorer of the void.", "archetype": "Leader", "power": 85}
                    ],
                    "timeline": [
                        {"id": 1, "phase": "Ignition", "details": "The stars flare unexpectedly across Sector 4."},
                        {"id": 2, "phase": "The Anomaly", "details": "Captain Vexa discovers the encrypted data stream."}
                    ]
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
    db = load_db()
    user = session["user"]
    books = db["users"][user]["books"]
    return render_template('dashboard.html', username=user, books=books)

@app.route('/studio/<int:book_id>')
def studio(book_id):
    if "user" not in session:
        return redirect(url_for('index'))
    db = load_db()
    user = session["user"]
    book = next((b for b in db["users"][user]["books"] if b["id"] == book_id), None)
    if not book:
        return redirect(url_for('index'))
    return render_template('studio.html', book=book)

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
        db["users"][username] = {"password": password, "books": []}
        save_db(db)
        session["user"] = username
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid credentials."}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop("user", None)
    return jsonify({"status": "success"})

@app.route('/api/create_book', methods=['POST'])
def create_book():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    db = load_db()
    user = session["user"]
    new_book = {
        "id": int(os.urandom(4).hex(), 16),
        "title": data.get("title", "Untitled Epic"),
        "genre": data.get("genre", "General Fiction"),
        "description": data.get("description", "A new creative universe."),
        "chapters": [{"id": 1, "title": "Chapter 1", "content": "Begin your story here..."}],
        "characters": [{"id": 1, "name": "Protagonist", "role": "Hero", "description": "Main lead.", "archetype": "Explorer", "power": 70}],
        "timeline": [{"id": 1, "phase": "Act I: Inciting Incident", "details": "The journey begins."}]
    }
    db["users"][user]["books"].append(new_book)
    save_db(db)
    return jsonify({"status": "success", "book_id": new_book["id"]})

@app.route('/api/save_book/<int:book_id>', methods=['POST'])
def save_book(book_id):
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    db = load_db()
    user = session["user"]
    books = db["users"][user]["books"]
    for i, b in enumerate(books):
        if b["id"] == book_id:
            books[i] = data
            save_db(db)
            return jsonify({"status": "success"})
    return jsonify({"error": "Book not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
