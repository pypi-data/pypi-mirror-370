import sys

# import cx_Oracle
# import mysql.connector
# import oracledb as oracledb
# import pyodbc
# import os

from src.database.utils import DatabaseConfig
import src
from src.imports import import_package
import platform
import requests
import zipfile
import os


# import firebirdsql


class Connection:
    def __init__(self, db_config: DatabaseConfig):
        self.db_type = db_config.db_type.lower()
        self.db_config = db_config
        if self.db_type == 'mysql':
            self.conn = get_mysql_connection(db_config.db_host, db_config.db_name, db_config.db_user, db_config.db_pwd,
                                             db_config.port)
        elif self.db_type == 'oracle':
            self.conn = get_oracle_client_connection(db_config.db_client, db_config.db_user, db_config.db_pwd,
                                                     db_config.db_host)
        elif self.db_type == 'sql':
            self.conn = get_sql_server_connection(db_config.db_client, db_config.db_host, db_config.db_name,
                                                  db_config.db_user, db_config.db_pwd)
        elif self.db_type == 'firebird':
            self.conn = get_firebird_connection(db_config.db_user, db_config.db_pwd, db_config.db_client,
                                                db_config.db_host)

    def get_conect(self):
        # if self.db_type == 'oracle':
        #     return get_oracle_connection(self.db_config.db_host, self.db_config.db_user, self.db_config.db_pwd)
        # else:
        return self.conn


def get_mysql_connection(db_host: str, db_name: str, db_user: str, db_pwd: str, db_port: str = '3306'):
    # import mysql.connector
    package = import_package('mysql.connector')
    if db_host.__contains__(':'):
        data = db_host.split(':')
        db_host = data[0]
        db_port = data[1]
    elif db_port is None or db_port == '':
        db_port = '3306'

    return package.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_pwd,
        port=db_port)


# def get_oraclethin_connection(db_dsn: str, db_user: str, db_pwd: str):
#    return oracledb.connect(user=db_user, password=db_pwd,
#                             host=db_host, port=1521, service_name=db_name) "dbhost.example.com/orclpdb"

#    return oracledb.connect(user=db_user, password=db_pwd,
#                              dsn=db_dsn)


def get_oracle_client_connection(db_client: str, db_user: str, db_pwd: str, db_host: str):
    # import cx_Oracle
    package = import_package('cx_Oracle')
    if src.is_connected_oracle_client is False:

        _caminho = sys.path
        caminho = ''
        # Verifica a arquitetura do sistema
        arquitetura = platform.architecture()[0]  # Retorna '64bit' ou '32bit'

        # Exibe o resultado
        if src.print_payloads:
            print(f"A arquitetura do sistema operacional é: {arquitetura}")

        # Procura o caminho que contém 'site-packages'
        caminho_site_packages = None
        for caminho in _caminho:
            if 'site-packages' in caminho:
                caminho_site_packages = caminho
                if src.print_payloads:
                    print(f'MOSTRA O CAMINHO: {caminho_site_packages}')
                break  # Sai do loop após encontrar o caminho

        # Verifica se o caminho foi encontrado
        if caminho_site_packages is None:
            raise Exception("Caminho contendo 'site-packages' não encontrado!")

        # Define caminho_oracle antes dos blocos if/else
        caminho_oracle = None

        # Escolhe "oracle2" ou "oracle64" com base na arquitetura
        if arquitetura == '64bit':

            caminho_64 = rf'{caminho_site_packages}\src\database\oracle64'
            # Verifica se o diretório já existe
            if not os.path.exists(caminho_64):
                if src.print_payloads:
                    print(f"Realizando Donwload do Driver 64bit")
                # Cria o diretório
                os.makedirs(caminho_64)
                # Faz o download do arquivo
                url = "http://static.openk.com.br/instantclient-basic-windows.x64-21.6.0.0.0dbru.zip"
                response = requests.get(url)
                zip_path = os.path.join(caminho_64, "oracle64.zip")
                with open(zip_path, 'wb') as file:
                    file.write(response.content)
                # Descompacta o arquivo
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(caminho_64)
                # Remove o arquivo zip após descompactar
                os.remove(zip_path)
                if src.print_payloads:
                    print(f"Donwload DRIVER ORACLE 64BITs Realizado com Sucesso !")
            caminho_oracle = rf'{caminho_site_packages}\src\database\oracle64\instantclient_21_6'
        else:
            caminho_oracle = rf'{caminho_site_packages}\src\database\oracle2\instantclient_21_6'

        # Exibe o caminho final (se necessário)
        if src.print_payloads:
            print(f"Caminho Final Oracle: {caminho_oracle}")

        caminho = caminho_oracle
        package.init_oracle_client(lib_dir=caminho)
        src.is_connected_oracle_client = True

    # return cx_Oracle.connect(user='system',
    #                        password='oracle',
    #                       dsn='192.168.4.62:49161/XE')
    return package.connect(user=db_user, password=db_pwd, dsn=db_host)


# def get_oracle_connection(db_host: str, db_user: str, db_pwd):
#    conn_str = db_user + '/' + db_pwd + '@' + db_host
#    return cx_Oracle.connect(conn_str)


# def get_oracle_client_connection(db_client: str, db_user: str, db_pwd: str, db_host: str):
#    if src.is_connected_oracle_client is False:
#        cx_Oracle.init_oracle_client(lib_dir=rf'{db_client}')
#        src.is_connected_oracle_client = True

#    return cx_Oracle.connect(user=db_user,
#                             password=db_pwd,
#                             dsn=db_host)


def get_sql_server_connection(db_driver: str, db_host: str, db_name: str, db_user: str, db_pwd: str):
    # import pyodbc
    package = import_package('pyodbc')
    return package.connect(f'Driver={{{db_driver}}};Server={db_host.replace(":", ",")};'
                           f'Database={db_name};UID={db_user};PWD={db_pwd}')


def get_firebird_connection(db_user: str, db_pwd: str, port: str, db_host: str):
    # import firebirdsql
    package = import_package('firebirdsql')
    db_port = '3050'
    if db_host.__contains__(':'):
        data = db_host.split(':')
        db_host = data[0]
        db_port = data[1]
    return package.Connection(user=db_user, password=db_pwd, database=port, host=db_host, port=db_port)


def output_type_handler(cursor, name, default_type, size, precision, scale):
    # import cx_Oracle
    package = import_package('cx_Oracle')
    if default_type == package.DB_TYPE_CLOB:
        return cursor.var(package.DB_TYPE_LONG, arraysize=cursor.arraysize)
    if default_type == package.DB_TYPE_BLOB:
        return cursor.var(package.DB_TYPE_LONG_RAW, arraysize=cursor.arraysize)
