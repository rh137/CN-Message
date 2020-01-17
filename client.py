import socket
import _thread
from myparser import parse_addr_str

def waiting_for_msg(server_addr_str, my_addr_str):
	server_addr = parse_addr_str(server_addr_str)
	msg_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	host = server_addr[0]
	port = server_addr[1]
	msg_socket.connect((host, port))

	msg_socket.send(my_addr_str.encode('ascii'))

	while True:
		msg_recv = msg_socket.recv(1024)
		print(msg_recv.decode('ascii'))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = input('host ip: ')
port = input('port:    ')

#host = int(host)
port = int(port)

s.connect((host,port))

msg = s.recv(1024)

#print(msg)
print(msg.decode('ascii'))

req = ''

login = False
Login_SUCCESS = 'Login Success!'

while req != 'exit' or login:
	req = input()
	s.send(req.encode('ascii'))
	
	if   req == 'reg' or req == 'login':
		msg = s.recv(1024)
		print(msg.decode('ascii'))
	#elif req == '':	

	msg = s.recv(1024)
	print(msg.decode('ascii'))
	
	if msg.decode('ascii') == Login_SUCCESS:
		# TODO: create a new thread connecting to server msg socket
		login = True
		s.send('welcome msg received'.encode('ascii'))

		msg = s.recv(1024)
		myaddr = msg.decode('ascii')
		print('identity:', myaddr)
		print('type:     ({}, {})'.format(type(myaddr[0]), type(myaddr[1])))

		s.send('my addr received'.encode('ascii'))

		msg = s.recv(1024)
		svaddr = msg.decode('ascii')
		print('dest:    ', svaddr)
		#print('type:    ', type(svaddr))
		print('type:     ({}, {})'.format(type(svaddr[0]), type(svaddr[1])))
		
		s.send('sv addr received'.encode('ascii'))

		_thread.start_new_thread(waiting_for_msg, (svaddr, myaddr))
		

s.close()
