import socket 
from enum import Enum
import struct

SERVER_IDLE_MESSAGE = "\nServer is now idle.\nOptions: \nL - listen to new clients\nD - display paired clients\nR - send recording request to clients\n"

class ServerStates(Enum):
	STARTUP = 1
	ERROR = 2
	IDLE = 3
	WAITING_FOR_CLIENTS_RESPONSE = 4
	WAITING_FOR_CLIENTS_BRINGUP = 5
	SENDING_INSTRUCTIONS_TO_CLIENTS = 6

class TennisServer(object):
	"""docstring for tennis_server"""
	def __init__(self, my_ip, my_port):
		self.my_ip = my_ip
		self.my_port = my_port
		self.clients = []
		self.state = ServerStates.STARTUP
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print(self)

	def start(self):
		self.socket.bind((self.my_ip, self.my_port))
		self.state = ServerStates.IDLE
		self.run()

	def __str__(self):
		return f"================\nTennisServer{'{'} my_ip: {self.my_ip}, my_port: {self.my_port}, clients: \
		 {self.clients}, state: {self.state}, socket: {self.socket}{'}'}\n================"

	def run(self):
		while True:
			print(self)
			if self.state == ServerStates.IDLE:	
				self.idle()
			elif self.state == ServerStates.ERROR:
				pass
			elif self.state == ServerStates.WAITING_FOR_CLIENTS_BRINGUP:
				self.acquire_new_client()
			elif self.state == ServerStates.WAITING_FOR_CLIENTS_RESPONSE:
				pass
			elif self.state == ServerStates.SENDING_INSTRUCTIONS_TO_CLIENTS:
				self.send_instructions_to_clients()
			else:
				pass
	
	def idle(self):
		user_response = input(SERVER_IDLE_MESSAGE)
		if user_response == 'L':
			self.state = ServerStates.WAITING_FOR_CLIENTS_BRINGUP
			pass
		elif user_response == 'D':
			print(f"Paired Clients are: {self.clients}")
		elif user_response == 'R':
			self.state = ServerStates.SENDING_INSTRUCTIONS_TO_CLIENTS
			print(f"Soon will implement requesting recordings from clients...")
		else:
			print("Invalid option chosen!")

	def acquire_new_client(self):
		print("Listening to new client")
		self.socket.listen()
		conn, addr = self.socket.accept()
		self.clients.append((conn, addr))
		print(f"Successfully connected to addr {addr}")
		self.state = ServerStates.IDLE


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
