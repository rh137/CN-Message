# user Info handler
import sqlite3 as sql

class userInfoHandler:

    conn = None
    c = None
    uid = 0

    def __init__(self):
    
        self.conn = sql.connect('UserInfo.db')
        self.c = self.conn.cursor()

        self.uid = 0

        try:
            self.c.execute('CREATE TABLE Users(uid, account_name, password)')
        except:
            print('table already exists but it\'s OK')
            self.c.execute('SELECT MAX (U.uid) FROM Users U')
            tmp = self.c.fetchall()
            print(tmp)
            if tmp[0][0] != None:
                self.uid = int(tmp[0][0]) + 1
            print(self.uid)


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
            tmp = (str(self.uid), account_name, password)
            self.c.execute('INSERT INTO Users VALUES(?, ?, ?)', tmp)
            self.uid = self.uid+1
            return 'SUCCESS'

        else:
            #print('requested account name already exists!')
            return 'FAILED'


    def login(self, account_name: str, password: str):
        exist, info = self._search(account_name)
        
        if(exist == 0):
            return 'INVALID_ACCOUNT'
        else:
            print(info)
            if len(info) > 1:
                return 'ERROR'
            else:
                userInfo = info[0];
                # NEED ENCRYPT!!
                if password == userInfo[2]:
                    return 'SUCCESS'
                else:
                    return 'WRONG_PW'



    def logout(self):
        pass


#if __name__ == '__main__':
#    main()
