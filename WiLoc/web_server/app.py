from config import r
from pony.orm import db_session

from flask import Flask, send_from_directory, url_for
from flask.ext.socketio import SocketIO, send, emit

app = Flask(__name__)
app.debug = True
socketio = SocketIO(app)

@app.route('/static/<path:filename>')
def send_foo(filename):
    return send_from_directory('static/', filename)

@app.route('/')
def hello_world():
    return send_from_directory('static/','index.html')

@socketio.on('connect')
def handle_message(message):
	print ("Connected!")

def push_socket_data():

	if app.already_listening:
		return
	app.already_listening = True
	def ack():
		print "Data was received."

	def new_data(msg):
		data = eval(msg['data'])
		print "Got some data to send. "+str(type(data))
		socketio.emit('draw_data',data)

	redis_queue = r.pubsub(ignore_subscribe_messages=True)
	redis_queue.subscribe(**{'positioning': new_data})
	redis_queue.run_in_thread(sleep_time=0.01)

	print "Listening for messages"


if __name__ == '__main__':
	app.already_listening = False
	push_socket_data()
	socketio.run(app)