import sys
from src.networking import server_app


def main():
	if(len(sys.argv) != 3):
		print("Usage: server_app.py <my_ip> <my_port> ")
		return
	ts = server_app.TennisServer(sys.argv[1], int(sys.argv[2]))
	ts.start()


if __name__ == '__main__':
	main()