import socket 
from enum import Enum
import struct
import sys
import select
from threading import Thread


SERVER_IDLE_MESSAGE = """\nServer is now idle.
Options: 
D - display paired clients
R - send recording request to clients
Q - Close socket and quit
"""

class ServerStates(Enum):
	STARTUP = 1
	ERROR = 2
	IDLE = 3
	WAITING_FOR_CLIENTS_RESPONSE = 4
	SENDING_INSTRUCTIONS_TO_CLIENTS = 5
	QUIT = 6

class TennisServer(object):
	SERVER_TIMEOUT_S = 10

	"""docstring for tennis_server"""
	def __init__(self, my_ip, my_port):
		self.my_ip = my_ip
		self.my_port = my_port
		self.clients = []
		self.state = ServerStates.STARTUP
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setblocking(False)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.inputs = [self.socket]
		self.outputs = []

	def start(self):
		self.socket.bind((self.my_ip, self.my_port))
		self.socket.listen(1000)
		self.socket.settimeout(self.SERVER_TIMEOUT_S)
		self.state = ServerStates.IDLE
		self.run()

	def __str__(self):
		return f"================\nTennisServer{'{'} my_ip: {self.my_ip}, my_port: {self.my_port}, clients: \
		 {self.clients}, state: {self.state}, socket: {self.socket}{'}'}\n================"

	def manage_readable_socket(self, socket):
		"""
		Will manage a new readable socket detected by the main select
		:param socket: new socket instance
		:return: None
		"""
		if socket is self.socket:
			# the server socket is readable when there is a new connection
			self.acquire_new_client()
		else:
			self.manage_sound_packet(socket)

	def manage_sound_packet(self, socket):
		"""
		Will parse and extract sound packet from read ready socket
		:param socket: socket to read sound from
		:return: None
		"""
		raise NotImplementedError()

	def manage_writable_socket(self, socket):
		"""
		Will manage a writable socket detected by the main select
		:param socket: writable socket
		:return: None
		"""
		pass

	def manage_exceptional_socket(self, socket):
		"""
		Will manage an exceptional socket detected by the main select
		:param socket: new exceptional socket
		:return: None
		"""
		# New exceptional socket indicates a disconnected client from the server
		print("Removing client connection:", socket)
		self.inputs.remove(socket)
		if socket in self.outputs:
			self.outputs.remove(socket)
		client_to_remove = None
		for client in self.clients:
			if client[0] == socket:
				client_to_remove = client
				break
		self.clients.remove(client_to_remove)
		socket.close()

	def handle_communication(self):
		"""
		Will handle the server side communication from incoming and outgoing messages using select
		:note: This method supposed to run on its own thread.
		:return: None
		"""
		while self.inputs:
			readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs)
			print(f"Select results:(readable:{len(readable)}, writable:{len(writable)}, exceptional:{len(exceptional)})")

			for readable_socket in readable:
				self.manage_readable_socket(readable_socket)

			for writable_socket in writable:
				self.manage_writable_socket(writable_socket)

			for exceptional_socket in exceptional:
				self.manage_exceptional_socket(exceptional_socket)

	def run(self):
		print(self)
		communication_thread = Thread(target=self.handle_communication)
		communication_thread.start()
		while True:
			if self.state == ServerStates.IDLE:
				self.idle()
			elif self.state == ServerStates.ERROR:
				print("ERROR!")
			elif self.state == ServerStates.WAITING_FOR_CLIENTS_RESPONSE:
				pass
			elif self.state == ServerStates.SENDING_INSTRUCTIONS_TO_CLIENTS:
				self.send_instructions_to_clients()
			elif self.state == ServerStates.QUIT:
				break
			else:
				pass
		
	
	def idle(self):
		user_response = input(SERVER_IDLE_MESSAGE).upper()
		if user_response == 'D':
			print(f"Paired Clients are: {self.clients}")
		elif user_response == 'R':
			self.state = ServerStates.SENDING_INSTRUCTIONS_TO_CLIENTS
		elif user_response == 'Q':
			print("Closing socket")
			self.socket.close()
			self.state = ServerStates.QUIT
		else:
			print(f"Invalid option chosen! - {user_response}")

	def acquire_new_client(self):
		conn, addr = self.socket.accept()
		self.clients.append((conn, addr))
		self.inputs.append(conn)
		print(f"Successfully connected to addr {addr}")

	def send_instructions_to_clients(self):

		try:
			duration = int(input("How long do you want to record (s)?"))
		except Exception as e:
			print("Invalid recording time")
			return
		for conn, addr in self.clients:
			print(f"Sending duration {duration} to {addr}")
			conn.sendall(struct.pack('i', duration))
		self.state = ServerStates.IDLE


def main():
	if(len(sys.argv) != 3):
		print("Usage: server_app.py <my_ip> <my_port> ")
		return
	ts = TennisServer(sys.argv[1], int(sys.argv[2]))
	ts.start()


if __name__ == '__main__':
	main()