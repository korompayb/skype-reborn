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
MESSAGES_FILE = "data/conversations.json"
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

        with open(USERS_FILE, "r+") as f:
            users = json.load(f)

            for user in users:
                if user["username"] == username and user["password"] == password:
                    user["status"] = "online"  # Státusz módosítása
                    session["username"] = username
                    
                    # Frissített adatok visszaírása a JSON-fájlba
                    f.seek(0)
                    json.dump(users, f, indent=4)
                    f.truncate()

                    return redirect("/chat")  # Sikeres bejelentkezés

        return "Invalid username or password", 401  # Ha nem találja a felhasználót

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

    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    # Megkeressük a bejelentkezett felhasználót
    user = next((u for u in users if u["username"] == session["username"]), None)

    if not user:
        return redirect("/")

    return render_template("chat.html", username=user["username"], user=user, status=user["status"])


@app.route("/get_users")
def get_users():
    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    return jsonify([
        {"username": user["username"], "status": user["status"], "profile_pic": user.get("profile_pic", "/default.png")}
        for user in users if user["username"] != session.get("username")
    ])


@app.route("/get_private_messages/<other_user>")
def get_private_messages(other_user):
    with open(MESSAGES_FILE, "r") as f:
        messages = json.load(f)

    chat_id = sorted([session["username"], other_user])  # Egységes chat ID
    chat_id = "_".join(chat_id)

    return jsonify(messages.get(chat_id, []))  # Ha nincs beszélgetés, üres lista


@app.route("/send_private", methods=["POST"])
def send_private():
    data = request.get_json()
    receiver = data["receiver"]
    message = data["message"]

    with open(MESSAGES_FILE, "r") as f:
        messages = json.load(f)

    chat_id = sorted([session["username"], receiver])
    chat_id = "_".join(chat_id)

    if chat_id not in messages:
        messages[chat_id] = []

    messages[chat_id].append({"sender": session["username"], "message": message})

    with open(MESSAGES_FILE, "w") as f:
        json.dump(messages, f)

    return jsonify({"status": "success"})

@app.route("/update_status", methods=["POST"])
def update_status():
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    new_status = data.get("status")

    if not new_status:
        return jsonify({"error": "Invalid status"}), 400

    with open(USERS_FILE, "r+") as f:
        users = json.load(f)

        for user in users:
            if user["username"] == session["username"]:
                user["status"] = new_status
                break

        f.seek(0)
        json.dump(users, f, indent=4)
        f.truncate()

    return jsonify({"message": "Status updated!", "status": new_status})


@app.route("/logout")
def logout():
    username = session.get("username")
    if username:
        with open(USERS_FILE, "r+") as f:
            users = json.load(f)
            for user in users:
                if user["username"] == username:
                    user["status"] = "offline"
                    break
            f.seek(0)
            json.dump(users, f, indent=4)
            f.truncate()
        session.pop("username", None)
    return redirect("/")

""" if __name__ == "__main__":
    app.run( debug=True,port=5000, host='0.0.0.0', threaded=True) """

if __name__ == "__main__":
    app.run(debug=True , port=5000)