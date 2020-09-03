import socketio
import eventlet
import json


# create a Socket.IO server
sio = socketio.Server()

# wrap with a WSGI application
app = socketio.WSGIApp(sio)

#Variable para ver los nodos
nodes = [] #

#Variable para contabilizar cuantas veces se esparce un mensaje
cont = 0
nodes_use = []
destino = 'N'
cont = 0

# llama al json con nodos
# with open('nodes.json') as f:
#   nodes = json.load(f)

@sio.event
def connect(sid, environ):
    print('connect ', sid)

@sio.event
def disconnect(sid):
    for n in nodes:
        if n['id'] == sid:
            nodes.remove(n)
    session = sio.get_session(sid)
    print('disconnect ', session['username'], sid)

@sio.on('signin')
def signin(sid, data):
    sio.save_session(sid, {"username": data['username'], "neighbors": data['neighbors']})
    session = sio.get_session(sid)
    newUser = True
    # Esto por si se desconecta e intenta volverse a conectar un nodo
    if nodes:
        for node in nodes:
            # Si ya existe el nombre del nodo solo actualiza el sid
            if node['username'] == data['username']: 
                newUser = False
                node['id'] = sid
                break
            # Si realmente es un nuevo usuario guarda toda la info
        if newUser:
            nodes.append({'id':sid, 'username': data['username'], "neighbors": data['neighbors']})
    # si nodes está vacia guarda toda la indo
    else:
        nodes.append({'id':sid, 'username': data['username'], "neighbors": data['neighbors']})

    print(f"username: {session['username']}")
    print(nodes)
    sio.emit("ready", to=sid)

@sio.on('send_msg')
def send_msg(sid, data):
    session = sio.get_session(sid)
    # Message log
    print('\nMessage at node', session['username'],
        '\n-----------------','\nfrom: ', data['from'][0],
        '\n-----------------','\nto: ', data['to'],
        '\n-----------------','\nmessage: ', data['message'])
    
    for neighbor in session['neighbors']:
        for node in nodes:
            if (neighbor['name'] == node['username']) & (node['username'] != data['from'][-1]):
                sio.emit('flood',data, to=node['id'])
                print(f"Sent message to {session['username']}'s neighbor {node['username']}")


@sio.on('distance_vector')
def distance_vector(sid, data):
    session = sio.get_session(sid)
    global cont
    cont += 1
    print("hola " + str(cont))
    for neighbor in session['neighbors']:
        for node in nodes:
            if (neighbor['name'] == node['username']) & (node['username'] != data['from'][-1]):
                new_data = {
                    'from': data['from'],
                    'to': data['to'],
                    'message': data['message'],
                    'neighbors_nei': session['neighbors']
                }
                sio.emit('shortest_path', new_data, to=node['id'])
                print(data['from'])
                print(data['from'][-1])
                print(f"Sent message to {session['username']}'s neighbor {node['username']}")

@sio.on('deliver')
def deliver(sid, data):

    for noti in data['path']['next_hop']:
        for n in nodes:
            if noti == n['username']:
                sio.emit('throug_you', to=n['id'])
            elif n['username'] == data['nododest']:
                sio.emit('vector_message', data['msg'],  to=n['id'])


@sio.on('link_flood')
def link_flood(sid,data):
    session = sio.get_session(sid)
    # Message log
    print('\nLink flood at node', session['username'],
        '\n-----------------','\nfrom: ', data['from'][0])
    for neighbor in session['neighbors']:
        for node in nodes:
            if (neighbor['name'] == node['username']) & (node['username'] not in data['from']):
                sio.emit('link_flood',data, to=node['id'])

@sio.on('link_flood_aknowledge')
def link_flood_aknowledge(sid, data):
    session = sio.get_session(sid)
    # Message log
    print('\nLink flood Aknowledge at node', session['username'],
        '\n-----------------','\nFrom: ', data['from'][-1],
        '\n-----------------','\nto: ', data['from'][0],
        '\n-----------------','\nhops: ', data['hops'])
    aknowledge = data
    neighbor = aknowledge['hops'].pop()
    for node in nodes:
        if (node['username'] == neighbor):
            sio.emit('link_flood_aknowledge',aknowledge, to=node['id'])
            print(f"\nSent LINK FLOOD AKNOWLEDGE from {session['username']} to {node['username']}.\n")
            break
    
@sio.on('link_message')
def link_message(sid,data):
    session = sio.get_session(sid)
    # Message log
    print('\nLink message at node', session['username'],
        '\n-----------------','\nFrom: ', data['from'][0],
        '\n-----------------','\nto: ', data['hops'][-1],
        '\n-----------------','\nhops: ', data['hops'])
    link_message = data
    neighbor = link_message['hops'].pop(0)
    for node in nodes:
        if node['username'] == neighbor:
            sio.emit('link_message',link_message, to=node['id'])
            print(f"\nSent LINK MESSAGE from {session['username']} to {node['username']}.\n")
            break

@sio.on('link_message_aknowledge')
def link_message_aknowledge(sid, data):
    session = sio.get_session(sid)
    # Message log
    print('\nAknowledge at node', session['username'],
        '\n-----------------','\nFrom: ', data['from'][-1],
        '\n-----------------','\nto: ', data['from'][0],
        '\n-----------------','\nhops: ', data['hops'])
    aknowledge = data
    neighbor = aknowledge['hops'].pop()
    for node in nodes:
        if node['username'] == neighbor:
            sio.emit('link_message_aknowledge',aknowledge, to=node['id'])
            print(f"\nSent LINK MESSAGE AKNOWLEDGE from {session['username']} to {node['username']}.\n")
            break
    

@sio.on('flood_aknowledge')
def flood_aknowledge(sid, data):
    session = sio.get_session(sid)
    # Message log
    print('\nAknowledge at node', session['username'],
        '\n-----------------','\nFrom: ', data['to'],
        '\n-----------------','\nto: ', data['from'][0],
        '\n-----------------','\nhops: ', data['hops'])
    aknowledge = data
    neighbor = aknowledge['hops'].pop()
    for node in nodes:
        if node['username'] == neighbor:
            sio.emit('flood_aknowledge',aknowledge, to=node['id'])
            print(f"\nSent FLOOD AKNOWLEDGE from {session['username']} to {node['username']}.\n")
            break

@sio.on('calc_distance')
def calc_distance(sid, data):
    global nodes_use
    global cont
    global destino
    nodes_use.append(data['name'])
    if cont == 0:
        destino = data['dest']
    cont += 1
    for v in data['nei']:
        for n in nodes:
            if v['name'] == n['username']:
                new_data = {
                    'nei': data['nei'],
                    'id': data['name'],
                    'dest': destino
                }
                print(new_data)
                sio.emit('update_table', new_data, to=n['id'])

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
