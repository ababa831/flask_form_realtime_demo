# coding: utf-8
from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key"  # Add an arbitrary string
# If you input None, MonkeyPatchWarning might be occured.
socketio = SocketIO(app, async_mode="eventlet")


class SiteInfo:
    title = "Page title"


# Rendering a simple html page and getting or posting values
@app.route("/", methods=["GET", "POST"])  # Do not forget method"s"
def get_form():
    # Recieved single type="text" (form) data
    try:
        value_single = request.form["single"]
    except KeyError:
        value_single = None
    # Recieved type="checkbox" name="list" data
    try:
        value_list = request.form.getlist("list")
    except KeyError:
        value_list = []

    return render_template(
        "index.html",
        title=SiteInfo.title,
        value_list=value_list,
        value_single=value_single)


# Realtime communication with websocket
# Always sending information from server in background
def background(comment):
    num = 0
    while True:
        socketio.sleep(1)
        num += 1
        content = "<span>{}{}</span>".format(num, comment)
        socketio.emit("my_count", {"data": content}, namespace="/demo")


# GET inputed data from forms
@app.route("/websocket", methods=["GET", "POST"])
def websocket():
    socketio.start_background_task(
        target=background, comment=" second elapsed...")
    return render_template(
        "socket.html", async_mode=socketio.async_mode, title=SiteInfo.title)


# Settings of socketIO
@socketio.on("receive_content", namespace="/demo")
def send_content(sent_data):
    content = "<li>{}</li>".format(sent_data["data"])
    emit("my_content", {"data": content}, broadcast=False)


if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)