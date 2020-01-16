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
            self.online_table.append((t[0], t[1], False, None))
       
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
            
            self.online_table.append((self.uid, account_name, False, None))

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



    def logout(self):
        pass


#if __name__ == '__main__':
#    main()
