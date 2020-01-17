import socket
import _thread
from myparser import parse_addr_str
import time
import getpass

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
        if msg_recv.decode('ascii') == 'logout':
            break

    msg_socket.close()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = input('host ip: ')
port = input('port:    ')

port = int(port)

s.connect((host,port))

msg = s.recv(1024)
print(msg.decode('ascii'))

req = ''

passwd = False
login = False
Login_SUCCESS = 'Login Success!'

while req != 'exit' or login == True:
    if passwd == True:
        req = getpass.getpass('')
        passwd = False
    else:
        req = input()
    s.send(req.encode('ascii'))
	
    msg_r = s.recv(1024)
    print(msg_r.decode('ascii'))

    if msg_r.decode('ascii') == 'password:     ':
            passwd = True

    # before login
    if  (req == 'reg' or req == 'login') and login == False:
        s.send('foo'.encode('ascii'))

        msg = s.recv(1024)
        print(msg.decode('ascii'))

        #time.sleep(0.05)
     
    # after login
    elif req.split(' ')[0] == 'send' and login == True:
        msg = s.recv(1024).decode('ascii')
        print('[from send]', msg)

    elif req.split(' ')[0] == 'sendfile' and login == True:
        # TODO: complete this block
        msg = s.recv(1024).decode('ascii')
        print('[from sendfile]', msg)

    elif req.split(' ')[0] == 'query' and login == True:
        msg = s.recv(1024).decode('ascii')
        print('[from query]\n', msg)
       
    elif req.split(' ')[0] == 'logout' and login == True:
        # TODO: logout
        msg = s.recv(1024).decode('ascii')
        print('[from logout]\n', msg)
        if msg == 'Bye Bye':
            login = False
            break
	
    if msg_r.decode('ascii') == Login_SUCCESS and login == False:
	# create a new thread connecting to server msg socket
        login = True
        s.send('welcome msg received'.encode('ascii'))

        msg = s.recv(1024)
        myaddr = msg.decode('ascii')
        #print('identity:', myaddr)
        #print('type:     ({}, {})'.format(type(myaddr[0]), type(myaddr[1])))

        s.send('my addr received'.encode('ascii'))

        msg = s.recv(1024)
        svaddr = msg.decode('ascii')
        #print('dest:    ', svaddr)
        #print('type:     ({}, {})'.format(type(svaddr[0]), type(svaddr[1])))
		
        s.send('sv addr received'.encode('ascii'))

        _thread.start_new_thread(waiting_for_msg, (svaddr, myaddr))

        msg = s.recv(65536)     # offline message
        print(msg.decode('ascii'))

s.close()

