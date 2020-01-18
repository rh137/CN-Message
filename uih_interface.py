import user_Info_handler
import queue
import _thread
import time

#####################################################################   
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
    
#####################################################################   
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


#####################################################################   
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

        elif req[1] == 'update_online_table':
            ID = req[0]
            dest_s_addr = req[2][0]
            dest_s_another_cli = req[2][1]
            func = req[2][2]
            result = uih.update_online_table(dest_s_addr, dest_s_another_cli, func)
            print(result)
            self.result_list.append((ID, result))
            pass

        elif req[1] == 'send':
            ID = req[0]
            account_name = req[2]
            result = uih.msgsocket(account_name)
            self.result_list.append((ID, result))                

        elif req[1] == 'show_online_table':
            try:
                for i in uih.online_table:
                    print(i)
                result = 'SUCCESS'
            except:
                result = 'FAIL'
            ID = req[0]
            self.result_list.append((ID, result))

        elif req[1] == 'sendfile':
            ID = req[0]
            in_name = req[2][0]
            out_name = req[2][1]
            result = uih.filesocket(in_name,out_name)
            self.result_list.append((ID, result))     

        elif req[1] == 'logout':
            ID = req[0]
            account_name = req[2]
            result = uih.logout(account_name)
            self.result_list.append((ID, result))                  
              
        else:
            pass
