from threading import Lock
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random

# Settings for flask
app = Flask(__name__)

# Settings for socket.io
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*",logging = True)

# Settings for threading
thread = None
thread_lock = Lock()

values = {
    'slider1': 25,
    'slider2': 0,
}

# Threading for websockets
def backgroundThread():
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        # Below value would be coming from the simulator (replace random)
        windDirection = random.randint(0,359)
        socketio.emit('winddirection', {'data': 'Wind direction is ', 'count': count, 'direction': windDirection })

# Flask routing
@app.route('/')
def index():
    return render_template('index.html',**values)

@app.route('/gauge')
def gauge():
    return render_template('radialgauge.html',**values)

@socketio.on('connect')
def connect():
    emit('after connect',  {'data':'Connected.'})
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(backgroundThread)

@socketio.on('Slider value changed')
def value_changed(message):
    values[message['who']] = message['data']
    emit('update value', message, broadcast=True)

# Notice how socketio.run takes care of app instantiation as well.
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')