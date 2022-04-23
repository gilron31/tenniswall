import sys
import server_app





def main():
	# s = server_app.TennisServer('192.168.68.116', 4000)
	s = server_app.TennisServer('', 4000)
	s.start()


if __name__ == '__main__':
	main()