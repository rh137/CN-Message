import socket
import _thread
from myparser import parse_addr_str
import time
import getpass
import signal

TIMEOUT_CONN = 2

class TimeOutException(Exception):
    pass

def alarm_handler(signum, frame):
    print("ALARM signal received")
    raise TimeOutException()

def myconnect(socket, arg):
    socket.connect(arg)

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


def waiting_for_fin(server_addr_str, my_addr_str):
    server_addr = parse_addr_str(server_addr_str)
    fin_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = server_addr[0]
    port = server_addr[1]
    fin_socket.connect((host, port))

    fin_socket.send(my_addr_str.encode('ascii'))

    while True:
        pass
        # TODO: handling waiting file input
        

#********** unnecessary thread **********
def waiting_for_fout(server_addr_str, my_addr_str):

    server_addr = parse_addr_str(server_addr_str)
    fout_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    host = server_addr[0]
    port = server_addr[1]
    fout_socket.connect((host, port))

    fout_socket.send(my_addr_str.encode('ascii'))

    while True:
        pass
        # TODO: handling waiting file output




s = None #socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

connected = False
while not connected:
    host = input('host ip: ')
    port = input('port:    ')
    
    print('connecting to ({},{})'.format(host, port))

    s.close()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        port = int(port)
    except:
        print('invalid port')
        continue
    try:
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(TIMEOUT_CONN)
        myconnect(s, (host,port))
        connected = True
        signal.alarm(0)
    except:
        print('fail to connect to {}:{}\nTry another IP:port'.format(host, port))
        signal.alarm(0)

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

	
    # login success => connect 3 other sockets	
    if msg_r.decode('ascii') == Login_SUCCESS and login == False:
        login = True
        s.send('welcome msg received'.encode('ascii'))

        # create a new thread connecting to server msg socket
        msg = s.recv(1024)
        myaddr = msg.decode('ascii')

        s.send('my addr received'.encode('ascii'))

    # socket 2 for receiving message (client-side)
        msg = s.recv(1024)
        svaddr = msg.decode('ascii')
		
        s.send('sv addr received'.encode('ascii'))

        _thread.start_new_thread(waiting_for_msg, (svaddr, myaddr))

    # socket 3 for  SENDING  files (client-side)
        msg = s.recv(1024)
        s3addr = msg.decode('ascii')

        s.send('s3 addr received'.encode('ascii'))

        _thread.start_new_thread(waiting_for_fout, (s3addr, myaddr))

    # socket 4 for RECEIVING files (client-side)
        msg = s.recv(1024)
        s4addr = msg.decode('ascii')

        s.send('s4 addr received'.encode('ascii'))

        _thread.start_new_thread(waiting_for_fin, (s4addr, myaddr))

    # receiving offline message
        msg = s.recv(65536)
        print(msg.decode('ascii'))

s.close()

