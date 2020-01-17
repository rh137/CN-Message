def send( source , destination , message , cli , result):

    if result[0] == 'INVALID_ACCOUNT':
        msg = destination + ' does not exist.\n'
        cli.send(msg.encode('ascii'))
    else:
        packet = '[' + time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())  + ']' + source + ':' + message + '\n'

        dir = os.path.abspath('.') + '\data'
        srcdir = dir + "\\" + source
        desdir = dir + "\\" + destination

        if not os.path.exists(dir):
            os.mkdir(dir)

        if not os.path.exists(srcdir):
            os.mkdir(srcdir)

        if not os.path.exists(desdir):
            os.mkdir(desdir)

        srcfile = open(srcdir + "\\" + destination + '.txt','a')
        desfile = open(desdir + "\\" + source + '.txt','a')

        srcfile.write(packet)
        desfile.write(packet)

        srcfile.close()
        desfile.close()

        if result[0] == 'ONLINE':
            result[1].send(packet.encode('ascii'))
        elif result[0] == 'OFFLINE':
            buffile = open(desdir + "\\" + buffer + '.txt','a')
            buffile.write(packet)
            buffile.close()


def query( source , destination , cli ):

    path = os.path.abspath('.') + '\data' + "\\" + source + "\\" + destination + '.txt'

    if not os.path.exists(path):
        msg = 'You never chat with ' + destination + '.\n'
        cli.send(msg.encode('ascii'))

    else:
        srcfile = open(path)
        for srcpacket in srcfile.readlines():
            srcpacket = srcpacket.strip('\n')
            cli.send(srcpacket.encode('ascii'))
        srcfile.close()


def receive( source , cli ):

    path = os.path.abspath('.') + '\data' + "\\" + source + "\\" + 'buffer.txt'

    if not os.path.exists(path):
        msg = 'There is no message when you are offline.\n'
        cli.send(msg.encode('ascii'))

    else:
        srcfile = open(path)
        for srcpacket in srcfile.readlines():
            srcpacket = srcpacket.strip('\n')
            cli.send(srcpacket.encode('ascii'))
        srcfile.close()
        os.remove(path)
