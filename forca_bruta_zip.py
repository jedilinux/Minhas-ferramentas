# -*- coding: utf-8 -*-
# @Author: Diego Rodrigues Pereira
# @Date:   2023-04-03 17:13:20
import zipfile
import threading
import argparse
import time
import hashlib
from tqdm import tqdm
import concurrent.futures

MAX_ATTEMPTS = 10
FOUND = False

def extractFile(zFile, password):
    global FOUND
    try:
        hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        zFile.extractall(pwd=password.encode('utf-8'))
        FOUND = True
        print("Senha encontrada:", password)
        return password
    except:
        return None

def main():
    global FOUND
    parser = argparse.ArgumentParser(description='Força bruta em arquivos zip e 7z.')
    parser.add_argument('-f', dest='zname', type=str, help='especifique o arquivo zip ou 7z')
    parser.add_argument('-d', dest='dname', type=str, help='especifique o arquivo dicionário')
    parser.add_argument('--max-attempts', dest='max_attempts', type=int, help='especifique o número máximo de tentativas de senha (padrão: 10)')
    parser.add_argument('-H', dest='help', action='store_true', help='obtenha ajuda')
    args = parser.parse_args()

    if args.help:
        parser.print_help()
        exit(0)

    if not args.zname or not args.dname:
        print(parser.usage)
        exit(0)

    zname = args.zname
    dname = args.dname
    max_attempts = args.max_attempts or MAX_ATTEMPTS

    zFile = zipfile.ZipFile(zname)
    dFile = open(dname, 'r')

    passwords = dFile.readlines()
    num_passwords = len(passwords)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i, password in enumerate(passwords):
            password = password.strip('\n')
            executor.submit(extractFile, zFile, password)
            if FOUND or (i+1) == num_passwords:
                break

            if (i+1) % 100 == 0:
                progress = (i+1) / num_passwords * 100
                print(f"Progresso: {int(progress)}%")

            if (i+1) % max_attempts == 0:
                time.sleep(10)

    if not FOUND:
        print("Senha não encontrada.")

if __name__ == '__main__':
    main()
