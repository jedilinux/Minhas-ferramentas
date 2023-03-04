import zipfile
import threading
import optparse
import time
import hashlib
from tqdm import tqdm
import concurrent.futures
import py7zr

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
    parser = optparse.OptionParser('Uso: %prog -f <arquivo_zip> -d <arquivo_dicionário> -t <tipo_de_arquivo> [--max-attempts <tentativas_máximas>]')
    parser.add_option('-f', dest='zname', type='string', help='especifique o arquivo zip/7z')
    parser.add_option('-d', dest='dname', type='string', help='especifique o arquivo dicionário')
    parser.add_option('-t', dest='filetype', type='string', help='especifique o tipo de arquivo, zip ou 7z')
    parser.add_option('--max-attempts', dest='max_attempts', type='int', help='especifique o número máximo de tentativas de senha (padrão: 10)')
    parser.add_option('-h', dest='help', action='store_true', help='obtenha ajuda')
    options, args = parser.parse_args()
    if options.help:
        parser.print_help()
        exit(0)

    if not options.zname or not options.dname or not options.filetype:
        print(parser.usage)
        exit(0)

    zname = options.zname
    dname = options.dname
    filetype = options.filetype.lower()
    max_attempts = options.max_attempts or MAX_ATTEMPTS

    if filetype == 'zip':
        zFile = zipfile.ZipFile(zname)
    elif filetype == '7z':
        zFile = py7zr.SevenZipFile(zname, mode='r')
    else:
        print("Tipo de arquivo não suportado.")
        exit(0)

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
