import eventlet
eventlet.monkey_patch()

from uuid import uuid4
from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, join_room, leave_room, emit
import sqlite3, os

app = Flask(__name__)
app.secret_key = os.urandom(32)
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

DB = "chat.db"
GLOBAL_PORT = "8789"

def db():
    return sqlite3.connect(DB)

def init_db():
    con = db()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rooms(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            port TEXT UNIQUE
        )
    """)
    cur.execute("DELETE FROM rooms WHERE port != ?", (GLOBAL_PORT,))
    cur.execute("INSERT OR IGNORE INTO rooms(name,port) VALUES(?,?)", ("Global Chat", GLOBAL_PORT))
    con.commit()
    con.close()


init_db()

@app.before_request
def make_session_permanent():
    if "sid" not in session:
        session["sid"] = str(uuid4())

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        session["nick"] = request.form["nick"]
        return redirect("/main")
    if "nick" in session:
        return redirect("/main")
    return render_template("index.html")


@app.route("/main")
def main():
    if "nick" not in session:
        return redirect("/")
    con = db()
    cur = con.cursor()
    cur.execute("SELECT name,port FROM rooms")
    rooms = cur.fetchall()
    con.close()
    return render_template("main.html", rooms=rooms)


@app.route("/create_room", methods=["POST"])
def create_room():
    name = request.form["name"]
    port = request.form["port"]
    if port == GLOBAL_PORT:
        return "Forbidden port."
    con = db()
    cur = con.cursor()
    cur.execute("INSERT OR IGNORE INTO rooms(name,port) VALUES(?,?)",(name,port))
    con.commit()
    con.close()
    return redirect(f"/chat/{port}")


@app.route("/join_room")
def join_room_page():
    port = request.args.get("port")
    con = db()
    cur = con.cursor()
    cur.execute("SELECT id FROM rooms WHERE port=?",(port,))
    room = cur.fetchone()
    con.close()
    if not room:
        return "Room does not exist."
    return redirect(f"/chat/{port}")


@app.route("/chat/<port>")
def chat(port):
    if "nick" not in session:
        return redirect("/")
    return render_template("chat.html", port=port, nick=session["nick"])


@app.route("/leave")
def leave():
    return redirect("/main")


@socketio.on("join")
def on_join(data):
    join_room(data["room"])
    emit("msg", {"nick":"SYSTEM","msg":f'{data["nick"]} joined.'}, room=data["room"])


@socketio.on("send")
def on_send(data):
    emit("msg", data, room=data["room"])

@socketio.on("leave")
def on_leave(data):
    leave_room(data["room"])
    emit("msg",{"nick":"SYSTEM","msg":f'{data["nick"]} left.'},room=data["room"])


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8000)
