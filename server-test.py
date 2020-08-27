import socketio
import eventlet

# create a Socket.IO server
sio = socketio.Server()

# wrap with a WSGI application
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print('connect ', sid)

@sio.event
def disconnect(sid):
    session = sio.get_session(sid)
    print('disconnect ', session['username'], sid)

@sio.on('signin')
def signin(sid,data):
    sio.save_session(sid, {"username": data['username']})
    session = sio.get_session(sid)
    print(f"username: {session['username']}")
    sio.emit("ready")

@sio.on('send_msg')
def signin(sid,msg):
    session = sio.get_session(sid)
    print('message from ', session['username'], msg)
    sio.emit("ready")


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)