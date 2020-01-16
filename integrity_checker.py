# integrity checker

#block_list = ['82.149.194.134', '111.249.16.197']
block_list = ['82.149.194.134',]

def check_integrity(c, addr):
    if addr[0] in block_list:
        print('{}{}{}'.format('*' * 19, ' MALICIOUS-INTENTED CONNECTION ', '*' * 50))
        count = 0
        while c.fileno() != -1:
            print('try to close', count)
            count = count + 1
            try:
                c.close()
            except:
                print('\tFAIL TO CLOSE!!')
        print('connection from {} is closed'.format(addr))
        print('*' * 100)
        return 'BAD'
    else:
        return 'GOOD'


