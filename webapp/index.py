from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def update_clients(data):
    # Emit the 'my event' event with the data to all connected clients
    socketio.emit('my event', data)

@app.route('/')
def index():
    # Update the clients with some data
    update_clients({'data': 'Hello, clients!'})
    return 'Hello, World!'

if __name__ == '__main__':
    socketio.run(app)
