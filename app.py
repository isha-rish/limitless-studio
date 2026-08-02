from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
import json

app = Flask(__name__)
app.secret_key = "reedsy_secret_writing_key"

DATA_FILE = "reedsy_vault.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('studio'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    if username:
        session['user'] = username
        data = load_data()
        if username not in data:
            data[username] = {
                "manuscript": [{"id": 1, "title": "Chapter 1: The Beginning", "content": ""}],
                "characters": [],
                "plot": [],
                "synopsis": ""
            }
            save_data(data)
        return redirect(url_for('studio'))
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/studio')
def studio():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('studio.html', username=session['user'])

@app.route('/api/get_data', methods=['GET'])
def get_data():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    data = load_data()
    user_data = data.get(session['user'], {})
    return jsonify(user_data)

@app.route('/api/save_data', methods=['POST'])
def api_save_data():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    req_data = request.json
    data = load_data()
    
    if session['user'] not in data:
        data[session['user']] = {}
        
    data[session['user']]["manuscript"] = req_data.get("manuscript", [])
    data[session['user']]["characters"] = req_data.get("characters", [])
    data[session['user']]["plot"] = req_data.get("plot", [])
    data[session['user']]["synopsis"] = req_data.get("synopsis", "")
    
    save_data(data)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
