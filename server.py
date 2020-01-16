import socket
import _thread
import user_Info_handler

cli_list = []
#uih = user_Info_handler.userInfoHandler()

def logged_in_client(cli, addr):
    while True:
        msg_recv = cli.recv(1024)
        msg_recv = msg_recv.decode('ascii')
        print(addr, msg_recv)
        #need sync
        msg_send = str(addr) + 'msg recv: ' + msg_recv
        cli.send(msg_send.encode('ascii'))
        # need strtok
        if   msg_recv == 'send':
            pass
        elif msg_recv == 'sendfile':
            pass
        elif msg_recv == 'query':
            pass
        elif msg_recv == 'exit':
            #logout
            pass
    return

def new_client(cli, addr):
    cli_list.append(cli)

    uih = user_Info_handler.userInfoHandler()
    
    while True:
        msg_recv = cli.recv(1024)
        msg_recv = msg_recv.decode('ascii')
        print(addr, msg_recv)
        # need sync server-client side
        msg_send = str(addr) + 'msg recv: ' + msg_recv
        cli.send(msg_send.encode('ascii'))
        
        if   msg_recv == 'reg':
            # call user_manager -> register() 
            
            msg_send = 'account name: '
            cli.send(msg_send.encode('ascii'))
            account_name = cli.recv(1024).decode('ascii')

            msg_send = 'password:     '
            cli.send(msg_send.encode('ascii'))
            password = cli.recv(1024).decode('ascii')

            # NEED TO ENCRYPT password !!!

            result = uih.register(account_name, password)
            
            if   result == 'SUCCESS':
                msg_send = 'Registration Success!'
                cli.send(msg_send.encode('ascii'))
                print('Register Success! ^_^')
                #update online table!!
                uih.conn.commit()
                
            elif result == 'FAILED':
                msg_send = 'Registration Failed! Please try another account name!'
                cli.send(msg_send.encode('ascii'))
                print('Register Fail QQ')
            else:
                print('ERROR Register')
                return

        elif msg_recv == 'login':
            msg_send = 'account name: '
            cli.send(msg_send.encode('ascii'))
            account_name = cli.recv(1024).decode('ascii')

            msg_send = 'password:     '
            cli.send(msg_send.encode('ascii'))
            password = cli.recv(1024).decode('ascii')

            # call user_manager -> login()
            result = uih.login(account_name, password)

            if   result == 'SUCCESS':
                msg_send = 'Login Success!'
                cli.send(msg_send.encode('ascii'))
                print('Login Success')
                #update online table!!
                logged_in_client(cli, addr)
            elif result == 'INVALID_ACCOUNT':
                msg_send = 'Login Failed! Your account name doesn\'t exist!'
                cli.send(msg_send.encode('ascii'))
                print('Login Fail invalid account')

            elif result == 'WRONG_PW':
                msg_send = 'Login Failed! Your password is wrong!'
                cli.send(msg_send.encode('ascii'))
                print('Login Fail wrong password')

            else:
                print('ERROR Login')
                return


        elif msg_recv == 'exit':
            break

    cli_list.remove(cli)
    cli.close()

    return


def listening(socket, _port):
    socket.listen(100)

    while True:
        c, addr = socket.accept()
        print('Got connection from', addr)
 
        msg = 'Successfully connected to ' + host_ip + ':' + str(_port) + '\n'
        #msg = msg + 'What\'s your request?'
        c.send(msg.encode('ascii'))
    
        _thread.start_new_thread(new_client, (c, addr))

    return

def listening_msg(socket, _port):
    socket.listen(100)

    while True:
        c, addr = socket.accept()
        print('Got connection from', addr)
 
        msg = 'Successfully connected to ' + host_ip + ':' + str(_port) + '\n'
        c.send(msg.encode('ascii'))

        # exchange msg
        # update (dest_s_addr, dest_s2_cli) table

    return




# main()

port = input('port: ')
port = int(port)
port2 = input('port2: ')
port2 = int(port2)


host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print("host ip: ", host_ip)
print("port:    ", port)
print("port2:   ", port2)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', port))

s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2.bind(('', port2))

_thread.start_new_thread(listening,(s, port))
_thread.start_new_thread(listening_msg,(s2, port2))

while True:
    req = input('->')
    if req == 'exit':
        for cli in cli_list:
            cli.close()
        break

s.close()
s2.close()
