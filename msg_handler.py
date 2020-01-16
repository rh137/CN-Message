import time
import os

def send( source , destination , message):

    #determine if destination exists
    #If not, send to source "destination + 'does not exist.\n'"

    #otherwise
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

    #determine if destination is offline
    #if not, send packet to destination

    #otherwise
    #buffile = open(desdir + "\\" + buffer + '.txt','a')
    #buffile.write(packet)
    #buffile.close()



def query( source , destination ):

    path = os.path.abspath('.') + '\data' + "\\" + source + "\\" + destination + '.txt'

    if not os.path.exists(path):
        msg = 'You never chat with ' + destination + '.\n'

        #send to source

    else:
        srcfile = open(path)
        for srcpacket in srcfile.readlines():
            srcpacket = srcpacket.strip('\n')

            #send to source

        srcfile.close()


def receive( source ):

    path = os.path.abspath('.') + '\data' + "\\" + source + "\\" + 'buffer.txt'

    if not os.path.exists(path):
        msg = 'There is no message when you are offline.\n'
        #send to source

    else:
        srcfile = open(path)
        for srcpacket in srcfile.readlines():
            srcpacket = srcpacket.strip('\n')

            #send to source


        srcfile.close()
        os.remove(path)
