import socketio
import json

# standard Python
sio = socketio.Client()
NAME = 'A'

@sio.event
def connect():
    print("I'm connected! as A.")
    sio.emit('signin', {'username':name, 'neighbors': neighbors})

@sio.event
def connect_error():
    print("\nThe connection failed!")

@sio.event
def disconnect():
    print("\nI'm disconnected!")

@sio.on('ready')
def ready():
	nid = str(input("A que nodo: ")) #nid = nodo destino
	msg = str(input("Qué mensaje: "))
	'''
	if nid != "A" or "B" or "C" or "D" or "E" or "F" or "G" or "H" or "I":
		print("nodo no existe")
		sio.disconnect()
	'''
	if msg == "exit":
		sio.disconnect()
	sio.emit("send_msg", data=(msg, nid)) 

@sio.on('flood')
def flood():
	return


with open('nodes.json') as f:
  nodes = json.load(f)

for n in nodes:
	if n['node_id'] == NAME:
		name = n['node_id']
		neighbors = n['neighbors']
sio.connect('http://localhost:5000')
sio.wait()
