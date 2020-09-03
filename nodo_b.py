import socketio
import json
import questionary
import time

# standard Python
sio = socketio.Client()
NAME = 'B'
wait_tables = True
menu_on = True # solo para hacer pruebas
with open('nodes.json') as f:
  nodes = json.load(f)

for n in nodes:
	if n['node_id'] == NAME:
		name = n['node_id']
		neighbors = n['neighbors']

link_database = []
route_table = {
	'node_id':NAME,
	'neighbors': neighbors
}


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
	global link_database
	global neighbors
	while(menu_on):
		time.sleep(1)
		print("\n------------ MENU PRINCIPAL DEL NODO ------------")
		#Pedimos el nodo al cual mandar el mensaje
		nodo_destino = questionary.select(
			"Escoja a que nodo desea enviar el mensaje",
			choices=['B','C','D','E','F','G','H','I','Salir']
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
				data = {
					'nei': neighbors,
					'name': NAME
				}
				sio.emit('calc_distance', data)
				print("compartiendo tablas con los vecinos, espere")
				time.sleep(5)
				print(neighbors)
			elif algoritmo == 'Link state routing':
				link_database = [route_table]
				sio.emit('link_flood',{'from':[NAME]})
				while len(link_database) != 9:
					continue
				print('\nGot all routing tables\n')
				path = best_path(link_database,NAME,nodo_destino)
				print(f"\nBest path: {path[0]} \nWeight: {path[1]}")
				link_message = {
					'from': [NAME],
					'hops':path[0][1:],
					'message': msg
				}
				sio.emit('link_message',link_message)

			else:
				print("not yet implemented")
	
	print("Hasta luego!")
	sio.disconnect()

@sio.on('link_flood')
def link_flood(data):
	acknowledge = data
	acknowledge['hops'] = data['from']
	acknowledge['from'].append(NAME)
	acknowledge['table'] = {
		'node_id': NAME,
		'neighbors': neighbors
	}
	sio.emit('link_flood_aknowledge', acknowledge)
	flood = data
	flood['from'].append(NAME)
	sio.emit('link_flood',flood)
	
@sio.on('link_flood_aknowledge')
def link_flood_aknowledge(data):
	global link_database
	if data['from'][0] == NAME:
		if data['from'][-1] not in [tabla['node_id'] for tabla in link_database]:
			print(f'\n Recieved ROUTING TABLE from {data["from"][-1]}')
			link_database.append(data['table'])
	else:
		
		sio.emit('link_flood_aknowledge', data)

@sio.on('link_message')
def link_message(data):
	if len(data['hops']) == 0:
		print('\n SOMEONE SEND YOU A MESSAGE!\n',
		'\n-----------------','\nfrom: ', data['from'],
        '\n-----------------','\nmessage: ', data['message'])
		aknowledge = data
		aknowledge['from'].append(NAME)
		aknowledge['hops'] = data['from']
		sio.emit('link_message_aknowledge', aknowledge)
	else:
		print('\nRecived LINK MESSAGE: \n')
		print('From: ' + str(data['from'][0]))
		print('to: ' + str(data['hops'][-1]))
		message = data
		message['from'].append(NAME)
		sio.emit('link_message',message)
		print('\nSent LINK MESSAGE')

@sio.on("link_message_aknowledge")
def flood_aknowledge(data):
	if data['from'][0] == NAME:
		print(f"\n Your message to {data['from'][-1]} was succesfully delivered.")
		print('\n-----------------','\nHops: ', data['from'])
	else:
		
		sio.emit('link_message_aknowledge', data)


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



sio.connect('http://localhost:5000')


def get_all_path(graph, src, dest, path = []):
	path = path + [src]
	if src[0] == dest: 
		return [path]
	paths = []
	new_path_list = []
	for node in nodes:
		if node['node_id'] == src[0]:
			for neighbor in node['neighbors']:
				visitados = [tupla[0] for tupla in path]
				if neighbor['name'] not in visitados:
					new_path_list = get_all_path(graph, (neighbor['name'],neighbor['weight']),dest,path)
				for new_path in new_path_list:
					paths.append(new_path)
			return paths

def best_path(graph, src, dest):
	best_weight = float('inf')
	best = []
	print(f"\nCalculating best path betwen {src} and {dest}")
	for path in get_all_path(graph,src,dest):
		weight = 0
		for hop in path[1:]:
			weight += hop[1]
		if weight < best_weight:
			best_weight = weight
			best = [hop[0] for hop in path]
	return best, best_weight