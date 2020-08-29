import socketio
import eventlet
import json


# create a Socket.IO server
sio = socketio.Server()

# wrap with a WSGI application
app = socketio.WSGIApp(sio)

#Variable para ver los nodos
nodes = [] #

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
    sio.emit("ready")

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
    sio.emit('ready',to=sid)
    
                
    # for n in nodes:
    #     if sid == n['node_id']:
    #         neighbors = n['neighbors']
    #         for vecino in neighbors:
    #             sio.emit('ready', vecino)
    #             print('Por FLOODING', n['node_id'], 'se envia a los vecinos: ', neighbors)
    


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)