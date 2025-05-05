from flask import Flask, request, redirect, render_template, session
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Secret key for session management
socketio = SocketIO(app)

# Predefined passcodes for three users
PASSCODES = {"User1": "alpha123", "User2": "beta456", "User3": "gamma789"}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        entered_passcode = request.form["passcode"]
        
        # Validate passcode
        if entered_passcode in PASSCODES.values():
            session["authenticated"] = True  # Store user session
            return redirect("/chat")  # Redirect to chatroom
        else:
            return render_template("login.html", error="❌ Invalid Passcode!")
    
    return render_template("login.html")

@app.route("/chat")
def chat():
    if session.get("authenticated"):
        return render_template("chat.html")
    return redirect("/")  # Send unauthenticated users back to login

@socketio.on("message")
def handle_message(msg):
    send(msg, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, debug=True)