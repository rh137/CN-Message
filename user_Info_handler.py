# user Info handler
# singleton

import sqlite3 as sql
from AES import encrypt

class userInfoHandler:

    conn = None
    c = None
    uid = 0
    online_table = []


    def __init__(self):
    
        self.conn = sql.connect('UserInfo.db')
        self.c = self.conn.cursor()

        self.uid = 0

        try:
            self.c.execute('CREATE TABLE Users(uid INTEGER, account_name, password)')
        except:
            print('table already exists but it\'s OK')
            self.c.execute('SELECT MAX (U.uid) FROM Users U')
            tmp = self.c.fetchall()
            print(tmp)
            if tmp[0][0] != None:
                self.uid = int(tmp[0][0]) + 1
            print(self.uid)

        self.c.execute('SELECT * FROM Users')
        tmp = self.c.fetchall()
        for t in tmp:
            self.online_table.append((t[0], t[1], False, None, None, None, None))
       
        for i in self.online_table:
            print(i)



    def _search(self, account_name):
        self.c.execute('SELECT * FROM Users WHERE account_name = ?', (account_name,))
        tmp = self.c.fetchall()
        count = 0
        for t in tmp:
            print(t)
            count = count + 1
        return count, tmp



    def register(self, account_name: str, password: str) -> str:
        exist, foo = self._search(account_name)
    
        if(exist == 0):
            encrypted_password = encrypt(password)
           
            tmp = (self.uid, account_name, encrypted_password)
            self.c.execute('INSERT INTO Users VALUES(?, ?, ?)', tmp)
            self.conn.commit()
            
            self.online_table.append((self.uid, account_name, False, None, None, None, None))

            self.uid = self.uid+1
       
            for i in self.online_table:
                print(i)

            return 'SUCCESS'

        else:
            #print('requested account name already exists!')
            return 'FAILED'



    def login(self, account_name: str, password: str, addr):
        exist, info = self._search(account_name)
        
        if(exist == 0):
            return 'INVALID_ACCOUNT'
        else:
            print('[UIH.login()]', info)
            if len(info) != 1:
                return 'ERROR duplicated account name'
            else:
                userInfo = info[0];
                encrypted_password = encrypt(password)
                
                if encrypted_password == userInfo[2]:
                    print('[UIH.login()]', 'for loop')
                    for i, user in enumerate(self.online_table):
                        if user[1] == account_name:
                            if user[2] == False:
                                user_tmp = list(user)
                                user_tmp[2] = True
                                user_tmp[3] = addr
                                self.online_table[i] = tuple(user_tmp)
                                return 'SUCCESS'
                            else:
                                return 'REENTRY'
                else:
                    return 'WRONG_PW'

    def msgsocket(self , account_name):
        for i, user in enumerate(self.online_table):
            if user[1] == account_name:
                if user[2] == True:
                    return ('ONLINE',user[4])
                else:
                    return ('OFFLINE',None)
        return ('INVALID_ACCOUNT',None)

    def filesocket(self , in_name , out_name):
        status = 'INVALID'
        for i, user in enumerate(self.online_table):
            if user[1] == in_name:
                if user[2] == True:
                    status = 'ONLINE'
                    finsocket = user[5]
                else:
                    status = 'OFFLINE'
                    finsocket = None
            elif user[1] == out_name:
                    foutsocket = user[6]
        return (status,finsocket,foutsocket)

    def logout(self , account_name):
        for i, user in enumerate(self.online_table):
            if user[1] == account_name:
                sck = (user[4] , user[5] , user[6])
                user_tmp = list(user)
                user_tmp[2] = False
                user_tmp[3] = None
                user_tmp[4] = None
                user_tmp[5] = None
                user_tmp[6] = None
                self.online_table[i] = tuple(user_tmp)
                return sck

    def update_online_table(self, dest_s_addr, dest_s2_cli, func):
        #print('type of dest_s_addr: ', type(dest_s_addr))
        #print('type of dest_s2_cli:', type(dest_s2_cli))
        
        which = -1
        if   func == 'msg':
            which = 4
        elif func == 'fin':
            which = 5
        elif func == 'fout':
            which = 6

        if which == -1:
            return 'ERROR func'

        for i, user in enumerate(self.online_table):
            #print('type of user[addr]:', type(user[3]))
            if user[3] == dest_s_addr:
                if user[2] == False:
                    return 'ERRORoffline'
                else:
                    user_tmp = list(user)
                    user_tmp[which] = dest_s2_cli
                    self.online_table[i] = tuple(user_tmp)
                    return 'SUCCESS' 




#if __name__ == '__main__':
#    main()
