import socketio
import json

# standard Python
sio = socketio.Client()
NAME = 'H'

@sio.event
def connect():
    print("I'm connected! as H")
    sio.emit('signin', {'username':name, 'neighbors': neighbors})

@sio.event
def connect_error():
    print("The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")

# @sio.on('ready')
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
	data = {
		'from': [NAME],
		'to': nid,
		'message': msg
	}
	sio.emit("send_msg", data) 
	print('message sent\n\n\n')

@sio.on('flood')
def flood(data):
	if data['to'] == NAME:
		print('\n You recieved a message!\n',\
		'\n-----------------','\nfrom: ', data['from'][0],
        '\n-----------------','\nmessage: ', data['message'])
		aknowledge = data
		aknowledge['hops'] = data['from']
		sio.emit('flood_aknowledge', aknowledge)
	else:
		print('\nRecived message: ', data)
		if (len(data['from']) + 1 != 9) & (NAME not in data['from']):
			message = data
			message['from'].append(NAME)
			sio.emit('send_msg', message)
			print('\nSent message: ', message)

@sio.on('flood_aknowledge')
def flood_aknowledge(data):
	if data['from'][0] == NAME:
		print(f"\n Your message to {data['to']} was succesfully delivered.")
		print('\n-----------------','\nHops: ', data['from'])
	else:
		print('\nRecived FLOOD AKNOWLEDGE: ', data)
		sio.emit('flood_aknowledge', data)



with open('nodes.json') as f:
  nodes = json.load(f)

for n in nodes:
	if n['node_id'] == NAME:
		name = n['node_id']
		neighbors = n['neighbors']

sio.connect('http://localhost:5000')