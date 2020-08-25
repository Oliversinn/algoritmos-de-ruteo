import socketio

# standard Python
sio = socketio.Client()

@sio.event
def connect():
    print("I'm connected!")
    sio.emit('signin', {'username':'oli'})

@sio.event
def connect_error():
    print("The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")

sio.connect('http://localhost:5000')
sio.wait()