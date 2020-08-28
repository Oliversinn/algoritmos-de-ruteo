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
with open('nodes.json') as f:
  nodes = json.load(f)

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
    nodes.append({'id':sid, 'username': data['username'], "neighbors": data['neighbors']})
    print(f"username: {session['username']}")
    sio.emit("ready")

@sio.on('send_msg')
def send_msg(sid, msg, nid):
    session = sio.get_session(sid)
    print('\nMessage from', session['username'], '\n-----------------','\n', msg, '\n-----------------','\nto: ', nid)
    for n in nodes:
        if sid == n['node_id']:
            neighbors = n['neighbors']
            for vecino in neighbors:
                sio.emit('ready', vecino)
                print('Por FLOODING', n['node_id'], 'se envia a los vecinos: ', neighbors)
    


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)