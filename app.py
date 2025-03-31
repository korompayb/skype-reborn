from flask import Flask, render_template, request, redirect, session, jsonify
import json
import os
from flask_session import Session

app = Flask(__name__)
app.secret_key = "ajkdhkslf333"

# Flask-Session configuration
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_FILE_DIR"] = "./flask_session"
os.makedirs(app.config["SESSION_FILE_DIR"], exist_ok=True)

Session(app)

# JSON files
MESSAGES_FILE = "data/messages.json"
CONVERSATIONS_FILE = "data/conversations.json"
USERS_FILE = "data/users.json"

# Initialize files
os.makedirs("data", exist_ok=True)
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump([], f)  # Initialize as an empty list

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with open(USERS_FILE, "r") as f:
            users = json.load(f)

        # Check if the user exists and the password matches
        for user in users:
            if user["username"] == username and user["password"] == password:
                session["username"] = username
                return redirect("/chat")

        return "Invalid username or password", 401  # Unauthorized

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with open(USERS_FILE, "r+") as f:
            users = json.load(f)

            # Check if the username already exists
            if any(user["username"] == username for user in users):
                return "Username already exists", 400  # Bad Request

            # Add new user
            users.append({"username": username, "password": password})
            f.seek(0)
            json.dump(users, f, indent=4)
            f.truncate()

        return redirect("/")

    return render_template("register.html")

@app.route("/chat")
def chat():
    if "username" not in session:
        return redirect("/")
    return render_template("chat.html", username=session["username"])

@app.route("/get_users")
def get_users():
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
    return jsonify([user["username"] for user in users])  # Return only usernames

@app.route("/private_chat/<other_user>")
def private_chat(other_user):
    if "username" not in session:
        return redirect("/")
    
    username = session["username"]
    chat_id = "_".join(sorted([username, other_user]))
    return render_template("private_chat.html", username=username, other_user=other_user, chat_id=chat_id)

@app.route("/send_private", methods=["POST"])
def send_private():
    data = request.get_json()
    sender = session["username"]
    receiver = data["receiver"]
    message = data["message"]

    chat_id = "_".join(sorted([sender, receiver]))

    with open(CONVERSATIONS_FILE, "r+") as f:
        conversations = json.load(f)
        if chat_id not in conversations:
            conversations[chat_id] = []
        conversations[chat_id].append({"sender": sender, "message": message})
        f.seek(0)
        json.dump(conversations, f, indent=4)

    return jsonify({"status": "Message Sent"})

@app.route("/get_private_messages/<chat_id>")
def get_private_messages(chat_id):
    with open(CONVERSATIONS_FILE, "r") as f:
        conversations = json.load(f)
    return jsonify(conversations.get(chat_id, []))

@app.route("/logout")
def logout():
    if "username" in session:
        session.pop("username", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(port=5000, host='0.0.0.0', threaded=True)