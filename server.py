import sqlite3
from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, send
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"
socketio = SocketIO(app)

# User passcodes mapped to usernames with avatars
USERS = {
    "alpha123": {"name": "User1", "avatar": "🦸‍♂️"},
    "beta456": {"name": "User2", "avatar": "🧙‍♂️"},
    "gamma789": {"name": "User3", "avatar": "🦸‍♀️"}
}

# Initialize SQLite Database
conn = sqlite3.connect("chat_history.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, username TEXT, avatar TEXT, timestamp TEXT, message TEXT)")
conn.commit()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        passcode = request.form["passcode"]

        if passcode in USERS:
            session["authenticated"] = True
            session["username"] = USERS[passcode]["name"]
            session["avatar"] = USERS[passcode]["avatar"]
            return redirect("/chat")
        else:
            return render_template("login.html", error="❌ Incorrect passcode!")

    return render_template("login.html")

@app.route("/chat")
def chat():
    if session.get("authenticated"):
        cursor.execute("SELECT username, avatar, timestamp, message FROM messages")
        chat_history = cursor.fetchall()
        return render_template("chat.html", username=session["username"], avatar=session["avatar"], chat_history=chat_history)
    return redirect("/")

@socketio.on("message")
def handle_message(msg):
    user = session.get("username", "Unknown")
    avatar = session.get("avatar", "👤")
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Store message in the database
    cursor.execute("INSERT INTO messages (username, avatar, timestamp, message) VALUES (?, ?, ?, ?)", (user, avatar, timestamp, msg))
    conn.commit()

    full_msg = f"<strong>{avatar} {user} [{timestamp}]:</strong> {msg}"
    send(full_msg, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5001)