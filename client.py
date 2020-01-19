import socket
import _thread
from myparser import parse_addr_str
import time
import getpass
import signal
import os
import sys

TIMEOUT_CONN = 2

class TimeOutException(Exception):
    pass

def alarm_handler(signum, frame):
    print("ALARM signal received")
    raise TimeOutException()

def myconnect(s):

    connected = False
    while not connected:
        host = input('\n[connect] host ip: ')
        if len(host) <= 6 or host[0] == 'd' or host[0] == 'D':
            host = '140.112.30.44'
            print('***default host: 140.112.30.44***')
        port = input('[connect] port:    ')
    
        try:
            port = int(port)
        except:
            print('\n*** port <{}> is invalid! ***\n*** port must be an integer in [1024, 65535] ***\n\nTry another IP:port'.format(port))
            continue

        if port <= 1023 or port >= 65536:
            print('\n*** port <{}> is invalid! ***\n*** port must be an integer in [1024, 65535] ***\n\nTry another IP:port'.format(port))
            continue
    
        print('connecting to ({}:{})'.format(host, port))

        s.close()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            signal.signal(signal.SIGALRM, alarm_handler)
            signal.alarm(TIMEOUT_CONN)
            s.connect((host, port))
            connected = True
            signal.alarm(0)
        except TimeOutException:
            print('\n*** Timeout when connecting to ({}:{}) ***\n\nTry another IP:port'.format(host, port))
            signal.alarm(0)
        except:
            print('\n*** Fail to connect to ({}:{}) ***\n\nTry another IP:port'.format(host, port))
            signal.alarm(0)
    
    return s


def waiting_for_msg(server_addr_str, my_addr_str):
    server_addr = parse_addr_str(server_addr_str)
    msg_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = server_addr[0]
    port = server_addr[1]
    msg_socket.connect((host, port))

    msg_socket.send(my_addr_str.encode('ascii'))

    while True:
        msg_recv = msg_socket.recv(1024)
        if msg_recv.decode('ascii') == 'logout':
            print('***SERVER TERMINATES msg***')
            break

        print(msg_recv.decode('ascii'))

    msg_socket.close()


def waiting_for_fin(server_addr_str, my_addr_str):
    server_addr = parse_addr_str(server_addr_str)
    fin_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = server_addr[0]
    port = server_addr[1]
    fin_socket.connect((host, port))

    fin_socket.send(my_addr_str.encode('ascii'))

    while True:
        fin = fin_socket.recv(1024).decode('ascii')
        fin_recv = fin.split(' ', 1)
        if fin_recv[0] == 'logout':
            print('***SERVER TERMINATES fin***')
            break 
        
        print(fin)

        if fin_recv[0] == 'recv':
            path = os.path.abspath('.') + '/new_' + fin_recv[1]
            file = open(path,'wb')
            file_exist = False
            while True:
                data = fin_socket.recv(1024)
                if data == 'END'.encode('ascii'):
                    break
                file.write(bytes(data))
                file_exist = True

            file.close()
            if file_exist == False:
                os.remove(path)
        pass
    
    fin_socket.close()


def waiting_for_fout(server_addr_str, my_addr_str, fout_socket):
    server_addr = parse_addr_str(server_addr_str)
    #fout_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = server_addr[0]
    port = server_addr[1]
    fout_socket.connect((host, port))

    fout_socket.send(my_addr_str.encode('ascii'))

    while True:
        fout_recv = fout_socket.recv(1024)
        fout = fout_recv.decode('ascii')
        if fout_recv.decode('ascii') == 'logout':
            print('***SERVER TERMINATES fout***') 
            break

        print(fout_recv.decode('ascii'))
        pass
    
    fout_socket.close()


# main()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s = myconnect(s)

msg = s.recv(1024)
print(msg.decode('ascii'))

req = ''

passwd = False
login = False
Login_SUCCESS = 'Login Success!'

fout_socket = None

SERVER_TERMINATE_MSG = '___SERVER_TERMINATES___'

while req != 'exit' or login == True:
    if passwd == True:
        req = getpass.getpass('')
        passwd = False
    else:
        req = input()
    s.send(req.encode('ascii'))

    if(len(req) == 0): continue
	
    msg_r = s.recv(1024)
    msg_rd = msg_r.decode('ascii')
    if msg_rd[0:len(SERVER_TERMINATE_MSG)] == SERVER_TERMINATE_MSG:
        print('***ERROR: {}***'.format(SERVER_TERMINATE_MSG))
        if not login:
            #s.send('exit(not yet logged in)'.encode('ascii'))
            req = 'exit'
            continue
        else:
            try:
                s.send('logout'.encode('ascii'))
            except:
                exit()
            break
    else:
        print(msg_rd)


    if msg_rd == 'password:     ':
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
        msg = s.recv(1024).decode('ascii')
        
        print('[from sendfile]', msg)
        if msg.split(' ',1)[0] == 'send':
            path = os.path.abspath('.') + '/' + req.split(' ')[2]
            if not os.path.exists(path):
                fout_socket.send('END'.encode('ascii'))
                print('Error: You do not have ' + req.split(' ')[2])
                continue
            file = open(path,'rb')
            while True:
                data = file.read(1024)
                if len(data) == 0:
                    break
                fout_socket.send(data)
            time.sleep(1)
            fout_socket.send('END'.encode('ascii'))
            file.close()

    elif req.split(' ')[0] == 'query' and login == True:
        msg = s.recv(65535).decode('ascii')
        print('[from query]\n', msg)
       
    elif req.split(' ')[0] == 'logout' and login == True:
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

        fout_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        _thread.start_new_thread(waiting_for_fout, (s3addr, myaddr, fout_socket))

    # socket 4 for RECEIVING files (client-side)
        msg = s.recv(1024)
        s4addr = msg.decode('ascii')

        s.send('s4 addr received'.encode('ascii'))

        _thread.start_new_thread(waiting_for_fin, (s4addr, myaddr))

    # receiving offline message
        msg = s.recv(65536)
        print(msg.decode('ascii'))

s.close()
