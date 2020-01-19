import time
import os

def send( source , destination , message , cli , result):

    if result[0] == 'INVALID_ACCOUNT':
        msg = destination + ' does not exist.\n'
        return msg
        #cli.send(msg.encode('ascii'))

    else:
        packet = '[' + time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())  + '] ' + source + ': ' + message

        dir = os.path.abspath('.') + '/data'
        srcdir = dir + "/" + source
        desdir = dir + "/" + destination

        if not os.path.exists(dir):
            os.mkdir(dir)

        if not os.path.exists(srcdir):
            os.mkdir(srcdir)

        if not os.path.exists(desdir):
            os.mkdir(desdir)

        srcfile = open(srcdir + "/" + destination + '.txt','a')
        desfile = open(desdir + "/" + source + '.txt','a')

        srcfile.write(packet)
        desfile.write(packet)

        srcfile.close()
        desfile.close()


        s = 'online user'
        if result[0] == 'ONLINE':
            result[1].send(packet.encode('ascii'))
        elif result[0] == 'OFFLINE':
            s = 'offline user'
            buffile = open(desdir + "/" + 'buffer' + '.txt','a')
            buffile.write(packet+'\n')
            buffile.close()

        return 'successfully send to {} {}'.format(s, destination)

def query( source , destination ):

    path = os.path.abspath('.') + '/data' + "/" + source + "/" + destination + '.txt'

    if not os.path.exists(path):
        msg = 'You never chat with ' + destination + ' or the account doesn\'t exist.\n'
        return msg

    else:
        srcfile = open(path)
        data = srcfile.read()
        srcfile.close()
        return data


def receive( source ):

    path = os.path.abspath('.') + '/data' + "/" + source + "/" + 'buffer.txt'

    if not os.path.exists(path):
        msg = 'There is no message when you are offline.\n'
        return msg

    else:
        srcfile = open(path)
        data = srcfile.read()
        srcfile.close()
        os.remove(path)
        return data
