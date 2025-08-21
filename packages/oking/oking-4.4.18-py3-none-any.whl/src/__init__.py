# Utilizar o padrão x.x.x.xxxx para caso precise subir versão de testes para o respositorio test-pypi
# Utilizar o padrão x.x.x para subir em produção
__version__ = '4.4.18'

import logging
import os
from datetime import datetime
from typing import Tuple
import requests

import src
from src.api import oking
import src.api.okinghub as api_okinghub
import sys
from src.entities.log import Log
from src.interface_grafica import exibir_janela_shortname
from src.jobs.utils import setup_logger
from src.layout import layout_shortname, layout_token
from src.imports import install_package_database
import re

global is_connected_oracle_client, client_data, start_time, shortname_interface, token_interface, conexao, \
    token_param, token_total, createDatabase, nome_token, job_console
nome_token = ''
createDatabase = False
shortname_interface = ''
token_interface = ''
token_total = ''
client_not_exists = True
exibir_interface_grafica = True
token_param = ''
job_console = ''
conexao = False
print_payloads: bool = False
jobs_qtd = 0

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s][%(asctime)s] %(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S')
logger = logging.getLogger()


# -- Ver Primeira linha deste arquivo
version = __version__  # <-- Nova forma de obter a versão


def print_version():
    print(version)
    exit()


def get_token_from_params(args: list) -> Tuple[str, bool]:
    global usrMaster, pwdMaster, exibir_interface_grafica

    if len(args) >= 2:
        if args.__contains__('-p') or args.__contains__('--payload'):
            global print_payloads
            print_payloads = True

        # Modo de Console
        if args.__contains__('--console'):
            exibir_interface_grafica = False
            global job_console, token_param
            if len(args) >= 3:
                token_element = ("".join([i for i in args if '-t=' in i]))
                job_element = ("".join([i for i in args if '-j=' in i]))
                if token_element:
                    token_param = args[args.index(token_element)].replace("-t=", "")
                if job_element:
                    job_console = args[args.index(job_element)].replace("-j=", "")

        if args.__contains__('--a'):
            setup_logger(src.job_console)

        # Modo de Criação de Banco de Dados
        if args.__contains__('--database'):
            exibir_interface_grafica = False
            src.createDatabase = True
            # Se [database] então precisa da Usuário e Senha [MASTER]
            if len(args) < 5:
                logger.error('======================= MODO DATABASE ========================')
                logger.error('=== Necessita dos parâmetros de Usuário e Senha master     ===')
                logger.error(' uso: oking [token] [--database] [usuarioMaster] [senhaMaster]')
                logger.error(' ')
                logger.error('--------------------------------------------------------------')
                exit(1)
            # Seta Usuário e Senha Master
            usrMaster = args[3]
            pwdMaster = args[4]

        if args[1] == '--version':
            print_version()

        if len(args) >= 3 and args[2] == '--dev':
            return args[1], True

        return '', False

    elif len(args) >= 1:
        return '', False

    else:
        logger.error('Informe o token da integracao como parametro')
        exit(1)


token_oking, is_dev = get_token_from_params(sys.argv)

start_time = datetime.now().isoformat()
logger.info('Iniciando oking __init__')
logger.info(f'Ambiente: {"Dev" if is_dev else "Prod"}')

try:
    if exibir_interface_grafica:
        exibir_janela_shortname()
    else:
        if os.path.isfile('shortname.txt'):
            shortname_file = open("shortname.txt", "r")
            shortname_interface = shortname_file.read()
            shortname_file.close()

        else:
            while True:
                shortname_interface = input('Digite o Shortname: ')
                try:
                    res = requests.get(f'https://{shortname_interface}.oking.openk.com.br/api/consulta/ping')
                    if not res.ok:
                        logger.warning(f'Ocorreu uma falha no test Ping: {res.text}')
                        continue
                    with open('shortname.txt', 'w') as f:
                        f.write(shortname_interface)
                        f.close()
                        break
                except:
                    print('Shortname inválido!')
                    continue

        if token_param:
            token_interface = token_param

        elif os.path.isfile('token.txt'):
            token_file = open("token.txt", "r")
            token_total = token_file.readline()
            value = 0
            if token_total.__contains__('#'):
                value = token_total.index('#') + 1
            token_interface = token_total[value:].replace("\n", "")
            token_file.close()

        else:
            nome_token = input('Informe o nome que deseja para essa integração (a sua escolha): ')
            while True:
                token_interface = input('Informe o Token: ')
                token_total = nome_token + '#' + token_interface + "\n"
                try:
                    client_data = oking.get(f'https://{shortname_interface}.oking.openk.com.br/api/consulta/oking_hub'
                                            f'/filtros?token={token_interface}', None)
                    client_not_exists = False
                    with open('token.txt', 'w') as f:
                        f.write(token_total)
                        f.close()
                        break
                except:
                    print('Token inválido!')
                    continue

    # if shortname_interface is None or token_interface is None:
    #     exit()

    if not is_dev:
        # Consultar dados da integracao do cliente (modulos, tempo de execucao, dados api okvendas)
        if client_not_exists:
            client_data = oking.get(f'https://{shortname_interface}.oking.openk.com.br/api/consulta/oking_hub'
                                    f'/filtros?token={token_interface}', None)
        if (createDatabase):
            client_data['user'] = usrMaster
            client_data['password'] = pwdMaster
        api_okinghub.post_log(
            Log(
                f'Oking inicializando {client_data["integracao_nome"]} - Versão {src.version}',
                'INICIALIZACAO',
                'OKING_INICIALIZACAO',
                f'{client_data.get("integracao_id")}',
                'X',
                F'{client_data.get("seller_id")}'
            )
        )
    else:
        # Consultar dados da integracao do cliente em ambiente node-red local
        client_data = oking.get(f'http://127.0.0.1:1880/api/consulta/integracao_oking/filtros', None)
        api_okinghub.post_log(Log(f'Oking inicializando cliente id {client_data["integracao_nome"]} - '
                                  f'Versão {src.version}',
                                  '',
                                  'OKING_INICIALIZACAO',
                                  {client_data["integracao_id"]},
                                  'X',
                                  {client_data["seller_id"]}))
    install_package_database(client_data['db_type'])
    if client_data is not None:
        # assert client_data['integracao_id'] is not None, 'Id da integracao nao informado (Api Oking)'
        # assert client_data['db_type'] is not None, 'Tipo do banco de dados nao informado (Api Oking)'
        # assert client_data['host'] is not None, 'Host do banco de dados nao informado (Api Oking)'
        # assert client_data['database'] is not None, 'Nome do banco de dados nao informado (Api Oking)'
        # assert client_data['user'] is not None, 'Usuario do banco de dados nao informado (Api Oking)'
        # assert client_data['password'] is not None, 'Senha do banco de dados nao informado (Api Oking)'
        if client_data['operacao'].lower().__contains__('mplace'):
            assert client_data[
                       'url_api_principal'] is not None, 'Url Principal da api okvendas nao informado (Api Oking)'
            assert client_data[
                       'url_api_secundaria'] is not None, 'Url Secundária da api okvendas nao informado (Api Oking)'
            assert client_data['token_api_integracao'] is not None, 'Token da api Parceiro nao informado '
        assert client_data['token_oking'] is not None, 'Token da Api Oking nao informado '

        is_connected_oracle_client = False
    else:
        logger.warning(f'Cliente nao configurado no painel oking para o token: {token_interface}')

except Exception as e:
    logger.error(f'Erro: {str(e)}')
    exit()
