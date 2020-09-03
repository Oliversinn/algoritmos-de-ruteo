import socketio
import json
import questionary
import time

menu_on = True # solo para hacer pruebas
# standard Python
sio = socketio.Client()
NAME = 'D'

@sio.event
def connect():
    print("I'm connected! as " + NAME)
    sio.emit('signin', {'username':name, 'neighbors': neighbors})

@sio.event
def connect_error():
    print("\nThe connection failed!")

@sio.event
def disconnect():
    print("\nI'm disconnected!")

@sio.on('ready')
def ready():
	global menu_on
	while(menu_on):
		time.sleep(1)
		print("\n------------ MENU PRINCIPAL DEL NODO ------------")
		#Pedimos el nodo al cual mandar el mensaje
		nodo_destino = questionary.select(
			"Escoja a que nodo desea enviar el mensaje",
			choices=['A','B','C','E','F','G','H','I','Salir']
		).ask()
		
		if nodo_destino == 'Salir':
			menu_on = False
		else:
			print(nodo_destino)

			msg = input("escibr el mensaje que deseas mandar: ")

			#Pedimos algoritmo a utilizar
			algoritmo = questionary.select(
				"Por favor escoja el algoritmo que desea utilizar para dirigir el tráfico entre nodo",
				choices=['Flooding', 'Distance vector routing', 'Link state routing']
			).ask()

			print(algoritmo)

			if algoritmo =='Flooding':
				data = {
					'from': [NAME],
					'to': nodo_destino,
					'message': msg
				}
				sio.emit("send_msg", data) 
				print('message sent\n\n\n')
			elif algoritmo == 'Distance vector routing':
				sio.emit('calc_distance', {"nei":neighbors, "name":NAME})
				print("compartiendo tablas con los vecinos, espere")
				time.sleep(5)
				print(neighbors)
			else:
				print("not yet implemented")
	
	print("Hasta luego!")
	sio.disconnect()


@sio.on('flood')
def flood(data):
	if data['to'] == NAME:
		print('\n SOMEONE SEND YOU A MESSAGE!\n',
		'\n-----------------','\nfrom: ', data['from'][0],
        '\n-----------------','\nmessage: ', data['message'])
		aknowledge = data
		aknowledge['hops'] = data['from']
		sio.emit('flood_aknowledge', aknowledge)
	else:
		print('\nRecived message: \n')
		print('From: ' + str(data['from'][0]))
		print('Message passed through: ' + str(data['from'][1:]))
		print("This is the message: " + data['message'])

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

@sio.on('update_table')
def update_table(v_table):
	global neighbors
	#Encontramos la distancia de este nodo hacia el vecino que le mando el mensaje
	for n in neighbors:
		if n['name'] == v_table['id']:
			distance_to_emitter = n['weight']

	for n in neighbors:
		for v in v_table['nei']:
			if n['name'] == v['name']:
				current_estimation = min(n['weight'], distance_to_emitter + v['weight'])
				if current_estimation != n['weight']:
					n['weight'] = current_estimation
					n['next_hop'].append(v['name'])
			else:
				neighbors.append(v)
	sio.emit('calc_distance', {"nei":neighbors, "name":NAME})

@sio.on('done_calc')
def done_calc():
	global neighbors
	
	print("done calculating")
	print(neighbors)

with open('nodes.json') as f:
  nodes = json.load(f)

for n in nodes:
	if n['node_id'] == NAME:
		name = n['node_id']
		neighbors = n['neighbors']

sio.connect('http://localhost:5000')