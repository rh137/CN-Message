import sys
sys.path.append("/home/student/06/b06902137")

import socket
import _thread
import queue
import time

#import user_Info_handler
from integrity_checker import check_integrity
from myparser import parse_addr_str
from msg_handler import send, query, receive

class Server:
    
    host_ip = None
    port    = None
    port2   = None
    port3   = None
    cli_list = []
    cli_list_msg = []
    dbq = None 
    result_list = []
    global_req_ID = 0
    req_ID_lock = _thread.allocate_lock()


    from uih_interface import get_result
    from uih_interface import push_req
    from uih_interface import request_to_UIH_handler

#####################################################################   
    def logged_in_client(self, cli, addr , account_name):      # multi thread
        
        print('(wlcm)', cli.recv(1024).decode('ascii'))
    
        cli.send(str(addr).encode('ascii'))
        print('(addr)', cli.recv(1024).decode('ascii'))
        cli.send(str((self.host_ip, self.port2)).encode('ascii'))
        print('(self)', cli.recv(1024).decode('ascii'))
            
        while True:

            msg_recv = cli.recv(1024).decode('ascii')
            print(addr, msg_recv)
            
            msg_send = str(addr) + '[logged in] msg recv: ' + msg_recv
            cli.send(msg_send.encode('ascii'))
            
            msg = msg_recv.split(' ',2)

            if msg[0] == 'send' and len(msg) == 3:
                print('sending!!!')
                send(account_name,msg[1],msg[2],cli,self.push_req(msg_recv, msg[1]))
                pass
            elif msg[0] == 'sendfile' and len(msg) == 3:
                print('sendfile!!!')
                pass
            elif msg[0] == 'query' and len(msg) == 2:
                print('query!!!')
                query(account_name,msg[1],cli)
                pass
            elif msg[0] == 'exit' and len(msg) == 1:
                print('exit!!!')
                #logout
                pass
            else:
                msg_send = 'Invalid instruction.\nsend : send + [account name] + [message]\nsend file : sendfile + [account name] + [file relative path]\nquery : query + [account name]\nexit : exit\n'
                print(msg_send)
                cli.send(msg_send.encode('ascii'))
                pass

        return

#####################################################################   
    def new_client(self, cli, addr):        # multi thread
        self.cli_list.append(cli)
    
        while True:

            msg_recv = cli.recv(1024)
            msg_recv = msg_recv.decode('ascii')
            print(addr, msg_recv)
        
            msg_send = str(addr) + 'msg recv: ' + msg_recv
            cli.send(msg_send.encode('ascii'))
        
       

            if   msg_recv == 'reg':

                msg_send = 'account name: '
                cli.send(msg_send.encode('ascii'))
                account_name = cli.recv(1024).decode('ascii')
                msg_send = 'password:     '
                cli.send(msg_send.encode('ascii'))
                password = cli.recv(1024).decode('ascii')

                result = self.push_req(msg_recv, (account_name, password)) 

                if   result == 'SUCCESS':
                    msg_send = 'Registration Success!'
                    cli.send(msg_send.encode('ascii'))
                    print('Register Success! ^_^')
                
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

                result = self.push_req(msg_recv, (account_name, password, addr))

                if   result == 'SUCCESS':
                    msg_send = 'Login Success!'
                    cli.send(msg_send.encode('ascii'))
                    print('Login Success')
                    self.logged_in_client(cli, addr,account_name)
                
                elif result == 'INVALID_ACCOUNT':
                    msg_send = 'Login Failed! Your account name doesn\'t exist!'
                    cli.send(msg_send.encode('ascii'))
                    print('Login Fail invalid account')

                elif result == 'WRONG_PW':
                    msg_send = 'Login Failed! Your password is wrong!'
                    cli.send(msg_send.encode('ascii'))
                    print('Login Fail wrong password')
                
                elif result == 'REENTRY':
                    msg_send = 'Login Failed! This account has already been logged in!'
                    cli.send(msg_send.encode('ascii'))
                    print('Login Fail reentry')

                else:
                    print('ERROR Login')
                    return



            elif msg_recv == 'exit':
                break

        self.cli_list.remove(cli)
        cli.close()

        return




#####################################################################   
    def listening(self, socket, _port):         # singleton
        socket.listen(100)

        _thread.start_new_thread(self.request_to_UIH_handler, ())
        print('after queue handler thread')

        while True:
            c, addr = socket.accept()
            print('[req socket] Got connection from', addr)
            
            rst = check_integrity(c, addr)
            if rst == 'BAD':
                continue
            
            msg = '[req socket] Successfully connected to ' + self.host_ip + ':' + str(_port) + '\n'
            #msg = msg + 'What\'s your request?'
            c.send(msg.encode('ascii'))
    
            _thread.start_new_thread(self.new_client, (c, addr))

        return

#####################################################################   
    def listening_msg(self, socket, _port):
        socket.listen(100)

        while True:
            c, addr = socket.accept()
            self.cli_list_msg.append(c)
            
            print('[msg socket] Got connection from', addr)

            cli_addr_str = c.recv(1024).decode('ascii')
            print('[msg socket] who is this?', cli_addr_str)
            cli_addr = parse_addr_str(cli_addr_str)

            rst = check_integrity(c, addr)
            if rst == 'BAD':
                continue


            # update (dest_s_addr, dest_s2_cli) table
            result = self.push_req('update_online_table', (cli_addr, c,))
            
            if   result == 'SUCCESS':
                print('[online table] update success')
            elif result == 'ERRORoffline':
                print('[online table] ERROR updating online table(the one to be updated is offline')
                return
            else:
                print('[online table] unexpected error')

 
            msg = '[msg socket] Successfully connected to ' + self.host_ip + ':' + str(_port) + '\n'
            c.send(msg.encode('ascii'))

        # exchange msg

        return


#####################################################################   
    def run(self):              # singleton
                                # conceptually, main()

        self.port  = input('port:  ')
        self.port  = int(self.port)
        #port2 = input('port2: ')
        #port2 = int(port2)
        #port3 = input('port3: ')
        #port3 = int(port3)
        self.port2 = (self.port + 1) % 65536
        if self.port2 < 10000: self.port2 += 10000
        self.port3 = (self.port + 2) % 65536
        if self.port3 < 10000: self.port3 += 10000

        host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(host_name)
        print("host ip: ", self.host_ip)
        print("port:    ", self.port)
        print("port2:   ", self.port2)
        print("port3:   ", self.port3)


        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('', self.port))

        self.s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s2.bind(('', self.port2))

        self.s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s3.bind(('', self.port3))

        _thread.start_new_thread(self.listening,(self.s, self.port))
        _thread.start_new_thread(self.listening_msg,(self.s2, self.port2))
        # TODO: start new thread for file transfer socket
        #   issue: need 2 sockets for file in/out?

        while True:
            req = input('->')
            if   req == 'exit':
                for cli in self.cli_list:
                    cli.close()
                break
            elif req == 'ot':
                pass
            elif req == 'status':
                pass

        self.s.close()
        self.s2.close()
        self.s3.close()

server = Server()
server.run()
