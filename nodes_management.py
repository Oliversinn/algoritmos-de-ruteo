import socketio
import eventlet

# create a Socket.IO server
sio = socketio.Server()

# wrap with a WSGI application
app = socketio.WSGIApp(sio)

#Variable para ver los nodos
nodes = []

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
def signin(sid,data):
    sio.save_session(sid, {"username": data['username'], "neighbors": data['neighbors']})
    session = sio.get_session(sid)
    nodes.append({'id':sid, 'username': data['username'], "neighbors": data['neighbors']})
    print(f"username: {session['username']}")
    sio.emit("ready")

@sio.on('send_msg')
def signin(sid,msg):
    session = sio.get_session(sid)
    print('message from ', session['username'], msg)
    for n in nodes:
    	print(n)
    sio.emit("ready")


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)