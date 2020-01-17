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

MAX_CONN = 100

class Server:
    
    host_ip = None
    port    = None
    port2   = None
    port3   = None
    port4   = None
    cli_list = []
    cli_list_msg  = []
    cli_list_fin  = []
    cli_list_fout = []
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
        print('( s2 )', cli.recv(1024).decode('ascii'))

        cli.send(str((self.host_ip, self.port3)).encode('ascii'))
        print('( s3 )', cli.recv(1024).decode('ascii'))

        cli.send(str((self.host_ip, self.port4)).encode('ascii'))
        print('( s4 )', cli.recv(1024).decode('ascii'))

        msg_send = receive(account_name)
        cli.send(msg_send.encode('ascii'))
            
        while True:

            msg_recv = cli.recv(1024).decode('ascii')
            print(addr, msg_recv)
            
            msg_send = str(addr) + '[logged in] msg recv: ' + msg_recv
            cli.send(msg_send.encode('ascii'))
            
            msg = msg_recv.split(' ',2)

            if msg[0] == 'send':
                if len(msg) == 3:
                    print('sending!!!')
                    msg_send = send(account_name,msg[1],msg[2],cli,self.push_req(msg[0], msg[1]))
                    cli.send(msg_send.encode('ascii'))
                else:
                    print('FORMAT ERROR send')
                    cli.send('FORMAT ERROR send\nusage: send <dest> <msg>'.encode('ascii'))

            elif msg[0] == 'sendfile':
                if len(msg) == 3:
                    print('sendfile!!!')
                    msg_send = 'successfully send file to {}'.format(msg[1])
                    cli.send(msg_send.encode('ascii'))
                else:
                    print('FORMAT ERROR sendfile')
                    cli.send('FORMAT ERROR sendfile\nusage: sendfile <dest> <filename>'.encode('ascii'))

            elif msg[0] == 'query':
                if len(msg) == 2:
                    print('query!!!')
                    msg_send = query(account_name,msg[1])
                    cli.send(msg_send.encode('ascii'))
                else:
                    print('FORMAT ERROR query')
                    cli.send('FORMAT ERROR query\nusage: query <dest>'.encode('ascii'))

            elif msg[0] == 'exit':
                print('exit!!!')
                #logout

            else:
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
                print(cli.recv(1024).decode('ascii'))

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
                print(cli.recv(1024).decode('ascii'))

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
        socket.listen(MAX_CONN)

        _thread.start_new_thread(self.request_to_UIH_handler, ())
        print('after queue handler thread')

        while True:
            c, addr = socket.accept()
            print('[req socket] Got connection from', addr)
            
            rst = check_integrity(c, addr)
            if rst == 'BAD':
                continue
            
            msg = '[req socket] Successfully connected to ' + self.host_ip + ':' + str(_port) + '\n'
            c.send(msg.encode('ascii'))
    
            _thread.start_new_thread(self.new_client, (c, addr))

        return

#####################################################################   
    def listening_msg(self, socket, _port):
        socket.listen(MAX_CONN)

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


            # update online table
            result = self.push_req('update_online_table', (cli_addr, c, 'msg',))
            
            if   result == 'SUCCESS':
                print('[msg(4) online table] update success')
            elif result == 'ERRORoffline':
                print('[msg(4) online table] ERROR updating online table(the one to be updated is offline')
                return
            elif result == 'ERROR func':
                print('[msg(4) online table] ERROR wrong func type')
                return
            else:
                print('[msg(4) online table] unexpected error')
                return


            msg = '[msg socket] Successfully connected to ' + self.host_ip + ':' + str(_port) + '\n'
            c.send(msg.encode('ascii'))

        # exchange msg

        return

#####################################################################
    def listening_fin(self, s_fin, port_fin):
        s_fin.listen(MAX_CONN)

        while True:
            c, addr = s_fin.accept()
            self.cli_list_fin.append(c)

            print('[fin socket] Got connection from', addr)

            cli_addr_str = c.recv(1024).decode('ascii')
            print('[fin socket] who is this?', cli_addr_str)
            cli_addr = parse_addr_str(cli_addr_str)

            rst = check_integrity(c, addr)
            if rst == 'BAD':
                continue

            #update online table
            result = self.push_req('update_online_table', (cli_addr, c, 'fin'))
            if   result == 'SUCCESS':
                print('[fin(5) online table] update success')
            elif result == 'ERRORoffline':
                print('[fin(5) online table] ERROR updating online table(the one to be updated is offline')
                return
            elif result == 'ERROR func':
                print('[fin(5) online table] ERROR wrong func type')
                return 
            else:
                print('[fin(5) online table] unexpected error')
                return

            msg = '[fin(5) socket(fout for client)] Successfully connected to ' + self.host_ip + ':' + str(port_fin) + '\n'
            c.send(msg.encode('ascii'))

        # for file from client to server

        return

#####################################################################
    def listening_fout(self, s_fout, port_fout):
        s_fout.listen(MAX_CONN)

        while True:
            c, addr = s_fout.accept()
            self.cli_list_fout.append(c)
            
            print('[fout socket] Got connection from', addr)

            cli_addr_str = c.recv(1024).decode('ascii')
            print('[fout socket] who is this?', cli_addr_str)
            cli_addr = parse_addr_str(cli_addr_str)

            rst = check_integrity(c, addr)
            if rst == 'BAD':
                continue

            #update online table
            result = self.push_req('update_online_table', (cli_addr, c, 'fout',))

            if   result == "SUCCESS":
                print('[fout(6) online table] update success')
            elif result == 'ERRORoffline':
                print('[fout(6) online table] ERROR updating online table(the one to be updated is offline')
                return
            elif resulf == 'ERROR func':
                print('[fout(6) online table] ERROR wrong func type')
                return
            else:
                print('[fout(6) online table] unexpected error')
                return


            msg = '[fout(6) socket(fin for client)] Successfully connected to ' + self.host_ip + ':' + str(port_fout) + '\n'
            c.send(msg.encode('ascii'))

        return

#####################################################################   
    def run(self):              # singleton
                                # conceptually, main()

        self.port  = input('port:  ')
        self.port  = int(self.port)

        self.port = self.port % 65536
        if self.port < 1024: self.port += 1024
        self.port2 = (self.port + 1) % 65536
        if self.port2 < 1024: self.port2 += 1024
        self.port3 = (self.port + 2) % 65536
        if self.port3 < 1024: self.port3 += 1024
        self.port4 = (self.port + 3) % 65536
        if self.port4 < 1024: self.port4 += 1024

        host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(host_name)
        print("host ip: ", self.host_ip)
        print("port:    ", self.port)
        print("port2:   ", self.port2)
        print("port3:   ", self.port3)
        print("port4:   ", self.port4)


    # recv request from/send respond to client socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('', self.port))

    # send msg to client socket
        self.s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s2.bind(('', self.port2))

    # file in socket
        self.s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s3.bind(('', self.port3))
    
    # file out socket
        self.s4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s4.bind(('', self.port4))

        _thread.start_new_thread(self.listening, (self.s, self.port))
        _thread.start_new_thread(self.listening_msg, (self.s2, self.port2))
        # TODO: start new thread for file transfer socket
        #   issue: need 2 sockets for file in/out?
        _thread.start_new_thread(self.listening_fin,  (self.s3, self.port3))
        _thread.start_new_thread(self.listening_fout, (self.s4, self.port4))


        while True:
            req = input('->')
            if   req == 'exit':
                for cli in self.cli_list:
                    cli.close()
                break

            elif req == 'ot':
                result = push_req('show_online_table', ())
            
            elif req == 'status':
                pass

        self.s.close()
        self.s2.close()
        self.s3.close()
        self.s4.close()

server = Server()
server.run()
