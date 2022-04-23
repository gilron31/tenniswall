import socket
from enum import Enum
import struct
import sys

class ClientStates(Enum):
	STARTUP_UNCONNECTED = 1
	ERROR = 2
	IDLE = 3
	RECORDING = 4


class TennisClient(object):
	CLIENT_TIMEOUT_S = 10

	def __init__(self, my_ip, my_port, server_ip, server_port):
		self.my_ip = my_ip
		self.my_port = my_port
		self.server_port = server_port
		self.server_ip = server_ip
		self.state = ClientStates.STARTUP_UNCONNECTED
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def start(self):
		self.socket.bind((self.my_ip, self.my_port))
		print(f"Trying to connect to server {(self.server_ip, self.server_port)}")
		self.socket.connect((self.server_ip, self.server_port))
		self.socket.settimeout(self.CLIENT_TIMEOUT_S)
		self.state = ClientStates.IDLE
		self.run()

	def __str__(self):
		return f"====TennisClient====\n{'{'} my_ip: {self.my_ip}, my_port: {self.my_port}, server_ip: \
		 {self.server_ip}, server_port: {self.server_port}, state: {self.state}, socket: {self.socket}{'}'}\n================"

	def run(self):
		while True:
			print(self)
			if self.state == ClientStates.IDLE:	
				self.idle()
			elif self.state == ClientStates.ERROR:
				print("ERROR!")
			elif self.state == ClientStates.RECORDING:
				self.acquire_new_client()
			else:
				pass

	def idle(self):
		try:
			data = self.socket.recv(4)
			assert len(data) == 4
			duration = struct.unpack('i', data)
			print(f"recieved duration: {duration}")
		except Exception as e:
			print("Timeout")


def main():
	if(len(sys.argv) != 5):
		print("Usage: client_app.py <my_ip> <my_port> <server_ip> <server_port>")
		return
	tc = TennisClient(sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]))
	tc.start()

if __name__ == '__main__':
	main()