import sys
sys.path.append("/home/student/06/b06902137")

import socket
import _thread
import queue
import time

import user_Info_handler
from integrity_checker import check_integrity


class Server:
    
    host_ip = None
    cli_list = []
    dbq = None 
    result_list = []
    global_req_ID = 0
    req_ID_lock = _thread.allocate_lock()

   
    def get_result(self, ID):           # multi thread
        result = None
        while result == None:
            for rst in self.result_list:
                if rst[0] == ID:
                    result = rst[1]
                    self.result_list.remove(rst)
                    break
                else:
                    continue
            time.sleep(0.05)
        return result
    
    def push_req(self, req_msg, argument):    # multi thread
        self.req_ID_lock.acquire()
        tid = _thread.get_ident()
        print('lock acquired by thread ', tid)
        try:
            req_ID = self.global_req_ID
            self.global_req_ID = self.global_req_ID + 1
        except:
            print('ERROR lock WTF')
        self.req_ID_lock.release()
        print('lock released by thread ', tid)
    
        req = (req_ID, req_msg, argument)
        self.dbq.put(req)
        
        result = self.get_result(req_ID)
        return result



    def logged_in_client(self, cli, addr):      # multi thread
        while True:
            msg_recv = cli.recv(1024)
            msg_recv = msg_recv.decode('ascii')
            print(addr, msg_recv)
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
                    self.logged_in_client(cli, addr)
                
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


    def request_to_UIH_handler(self):            # singleton

        uih = user_Info_handler.userInfoHandler()

        self.dbq = queue.Queue()
        print('dbq initialized')
        print('type = ', type(self.dbq))

        while True:
            req = self.dbq.get()
            print('[req_handler] get ', req)
            if   req[1] == 'reg':
                ID = req[0]
                account_name = req[2][0]
                password     = req[2][1]
                result = uih.register(account_name, password)
                self.result_list.append((ID, result))

            elif req[1] == 'login':
                ID = req[0]
                account_name = req[2][0]
                password     = req[2][1]
                addr         = req[2][2]
                result = uih.login(account_name, password, addr)
                self.result_list.append((ID, result))

              
            elif req[1] == 'req3':
                pass
            else:
                pass




    def listening(self, socket, _port):         # singleton
        socket.listen(100)

        _thread.start_new_thread(self.request_to_UIH_handler, ())
        print('after queue handler thread')

        while True:
            c, addr = socket.accept()
            print('Got connection from', addr)
            
            rst = check_integrity(c, addr)
            if rst == 'BAD':
                continue
            
            msg = 'Successfully connected to ' + self.host_ip + ':' + str(_port) + '\n'
            #msg = msg + 'What\'s your request?'
            c.send(msg.encode('ascii'))
    
            _thread.start_new_thread(self.new_client, (c, addr))

        return

    def listening_msg(self, socket, _port):
        socket.listen(100)

        while True:
            c, addr = socket.accept()
            print('Got connection from', addr)

            rst = check_integrity(c, addr)
            if rst == 'BAD':
                continue
 
            msg = 'Successfully connected to ' + self.host_ip + ':' + str(_port) + '\n'
            c.send(msg.encode('ascii'))

            # exchange msg
            # update (dest_s_addr, dest_s2_cli) table

        return



    def run(self):              # singleton
                                # conceptually, main()

        port = input('port: ')
        port = int(port)
        port2 = input('port2: ')
        port2 = int(port2)


        host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(host_name)
        print("host ip: ", self.host_ip)
        print("port:    ", port)
        print("port2:   ", port2)


        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', port))

        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.bind(('', port2))

        _thread.start_new_thread(self.listening,(s, port))
        _thread.start_new_thread(self.listening_msg,(s2, port2))

        while True:
            req = input('->')
            if   req == 'exit':
                for cli in self.cli_list:
                    cli.close()
                break
            elif req == 'show':
                pass

        s.close()
        s2.close()


#main()
server = Server()
server.run()
