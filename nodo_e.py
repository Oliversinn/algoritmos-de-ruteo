import socketio
import json

# standard Python
sio = socketio.Client()
NAME = 'E'

@sio.event
def connect():
    print("I'm connected!")
    sio.emit('signin', {'username':name, 'neighbors': neighbors})

@sio.event
def connect_error():
    print("The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")

@sio.on('ready')
def ready():
	msg = input("que mensaje: ")
	if msg == "exit":
		sio.disconnect()
	sio.emit("send_msg", msg)

with open('nodes.json') as f:
  nodes = json.load(f)

for n in nodes:
	if n['node_id'] == NAME:
		name = n['node_id']
		neighbors = n['neighbors']
sio.connect('http://localhost:5000')
sio.wait()
