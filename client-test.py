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

@sio.on('ready')
def ready():
	try:
		msg = input("que mensaje: ")
		sio.emit("send_msg", msg)
	except KeyboardInterrupt:
		sio.disconnect()

sio.connect('http://localhost:5000')
sio.wait()
