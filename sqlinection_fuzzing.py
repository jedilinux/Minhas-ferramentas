# @Autor: Diego Rodrigues Pereira
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import argparse
import sqlparse
import threading
from multiprocessing.pool import ThreadPool as Pool


def colorize(color, text):
    colors = {
        'red': '\033[1;31m',
        'green': '\033[1;32m',
        'blue': '\033[1;34m',
        'reset': '\033[1;m'
    }
    return f'{colors[color]}{text}{colors["reset"]}'


def parse_cli_args():
    parser = argparse.ArgumentParser(
        description='Fuzzing no banco de dados MariaDB, MSSQL, \
            MySQL, PostgreSQL and Oracle database')
    parser.add_argument(
        '-t',
        '--type',
        dest='type',
        default='mysql',
        help='Database type: mysql, mssql',
        choices=[
            "mysql",
            "mariadb",
            "mssql",
            "pgsql",
            "oracle"])
    parser.add_argument('-q', '--query',
                        dest='query',
                        help='Query to fuzz',
                        required=True)
    parser.add_argument('-p', '--payload',
                        dest='payload',
                        help='Payload to use',
                        required=True)
    parser.add_argument('-c', '--chars',
                        dest='chars',
                        help='Characters to fuzz',
                        required=True)
    parser.add_argument('-u', '--user',
                        dest='user',
                        help='Database user')
    parser.add_argument('--password',
                        dest='password',
                        help='Database password',
                        default='')
    parser.add_argument('-d', '--db',
                        dest='db',
                        help='Database name',
                        required=True)
    parser.add_argument('-o', '--out',
                        dest='out',
                        help='Filename pattern (default: log)',
                        default="log")
    parser.add_argument('--log-all',
                        dest='log_all',
                        action='store_true')
    parser.add_argument('--check',
                        dest='check',
                        help='Check value',
                        default=False)
    return parser.parse_args()


def db_connect(args):
    if args.type in ["mysql", "mariadb"]:
        import mysql.connector
        try:
            connection = mysql.connector.connect(
                user=args.user,
                password=args.password,
                database=args.db)
        except mysql.connector.Error as err:
            print(colorize("red", f"[ERROR] {err}"))
            return None
    elif args.type == "mssql":
        import pymssql
        try:
            connection = pymssql.connect(server="localhost", database=args.db)
        except pymssql.Error as err:
            print(colorize("red", f"[ERROR] {err}"))
            return None
    elif args.type == "pgsql":
        import psycopg2
        try:
            connection = psycopg2.connect(
                f"dbname='{args.db}' user='{args.user}' password='{args.password}'")
        except psycopg2.Error as err:
            print(colorize("red", f"[ERROR] {err}"))
            return None
    elif args.type == "oracle":
        import cx_Oracle
        try:
            connection = cx_Oracle.connect(
                args.user, args.password, cx_Oracle.makedsn(
                    '127.0.0.1', 1521, args.db), mode=cx_Oracle.SYSDBA)
        except cx_Oracle.Error as err:
            print(colorize("red", f"[ERROR] {err}"))
            return None

    return connection


def get_next(string, args):
    if len(string) <= 0:
        string.append(args.chars[0])
    else:
        string[0] = args.chars[(args.chars.index(string[0]) + 1) % len(args.chars)]
        if args.chars.index(string[0]) == 0:
            return list(string[0]) + get_next(string[1:], args)
    return string


def log_msg(filename, msg):
    with threading.Lock():
        with open(filename, "a") as f:
            f.write(f"{msg}\n")


def process_one(opts):
    cursor = opts[0]
    payload = opts[1]
    args = opts[2]
    fingerprints_file = f"{args.type}_fp.txt"
    if os.path.isfile(fingerprints_file):
        fingerprints = open(fingerprints_file, "r").read()
    else:
        fingerprints = list()

    try:
        if args.type in ["mysql", "mariadb"]:
            for item in cursor.execute(args.query.format(payload), multi=True):
                rows = item.fetchall()
        else:
            cursor.execute(args.query.format(payload))
            rows = cursor.fetchall()
    except Exception as err:
        print(colorize("red", f"[ERROR] {err}"))
        return

    sqli = pylibinjection.detect_sqli(payload)
    msg = f"Fingerprint: {sqli['fingerprint']} Query: {args.query.format(payload)} Result: {rows}"
    if len(rows) > 0:
        if sqli["sqli"]:
            print(colorize("red", f"[BLOCKED] {msg}"))
            if args.log_all:
                log_msg(f"{args.type}_bad.txt", f"[{args.type.upper()}] {msg}")
        else:
            if sqli["fingerprint"] in fingerprints:
                print(colorize("blue", f"[PASS][DUP] {msg}"))
                log_msg(f"{args.type}_bad.txt", f"[DUPE][{args.type.upper()}] {msg}")
            else:
                print(colorize("green", f"[PASS][NEW] {msg}"))
                log_msg(f"{args.type}_good.txt", f"[{args.type.upper()}] {msg}")
                log_msg(fingerprints_file, sqli["fingerprint"])
                fingerprints.append(sqli["fingerprint"])


def fuzz(args):
    cnx = db_connect(args)
    if not cnx:
        sys.exit()
    cursor = cnx.cursor()
    sequence = list()
    if args.log_all:
        with open(f"{args.type}_all.txt", "w") as file_log:
            pass
    if args.check:
        payload = args.payload.format(args.check)
        process_one([cursor, payload, args])
        sys.exit()
    else:
        while True:
            sequence = get_next(sequence, args)
            item = ''.join(reversed(sequence))
            if len(item) == 5:
                cnx.close()
                sys.exit()
            payload = args.payload.format(item)
            try:
                process_one([cursor, payload, args])
            except Exception as err:
                if args.type == "pgsql":
                    cnx.rollback()
                if args.log_all:
                    log_msg(f"{args.type}_all.txt", f"[{args.type.upper()}] Query: {args.query.format(payload)}")
                continue


if __name__ == "__main__":
    args = parse_cli_args()
    fuzz(args)
