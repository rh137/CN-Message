import socket

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

while req != 'exit':
	req = input()
	s.send(req.encode('ascii'))
	
	if   req == 'reg' or req == 'login':
		msg = s.recv(1024)
		print(msg.decode('ascii'))
	#elif req == '':	

	msg = s.recv(1024)
	print(msg.decode('ascii'))

s.close()
