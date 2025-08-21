import logging
import threading
from typing import List

from src.jobs.utils import executa_comando_sql

import src.database.connection as database
from src.api.entities.plano_pagamento_cliente import PlanoPagamentoCliente
from src.database import queries
from src.database.queries import IntegrationType
from src.database.utils import DatabaseConfig
import src.database.utils as utils
# from src.entities.product import Product
# from src.entities.photos_sku import PhotosSku
import src.api.okvendas as api_okvendas
from src.jobs.system_jobs import OnlineLogger
from src.database.entities.client_payment_plan import ClientPaymentPlan
from threading import Lock
import src
from src.log_types import LogType

lock = Lock()
logger = logging.getLogger()
send_log = OnlineLogger.send_log


def job_client_payment_plan(job_config_dict: dict):
    with lock:
        """
        Job para inserir os planos de pagamentos dos clientes no banco semáforo
        Args:
            job_config_dict: Configuração do job
        """
        logger.info(f'==== THREAD INICIADA -job: ' + job_config_dict.get('job_name'))
        # LOG de Inicialização do Método - Para acompanhamento de execução
        send_log(
            job_config_dict.get('job_name'),
            job_config_dict.get('enviar_logs'),
            True,
            f'Plano Pagamento Cliente - Iniciado',
            LogType.EXEC,
            'PLANO_PAGAMENTO_CLIENTE')

        db_config = utils.get_database_config(job_config_dict)
        if db_config.sql is None:
            send_log(
                job_config_dict.get('job_name'),
                job_config_dict.get('enviar_logs'),
                False,
                f'Comando sql para inserir os planos de pagamentos dos clientes no semaforo nao encontrado',
                LogType.WARNING,
                'PLANO_PAGAMENTO_CLIENTE')
            return

        try:
            if job_config_dict['executar_query_semaforo'] == 'S':
                executa_comando_sql(db_config, job_config_dict)
            db_client_payment_plan = query_list_client_payment_plan(job_config_dict, db_config)
            db_client_payment_plan.sort(key=lambda x: int(x.code_client))

            logger.info(f'==== Consultou os Planos de Pagamentos')

            # if not insert_update_semaphore_client_payment_plan(job_config_dict, db_config, db_client_payment_plan):
            #    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
            #             f'Nao foi possivel inserir os planos de pagamentos dos clientes no banco semaforo',
            #             LogType.ERROR, 'envia_plano_pagamento_cliente_job ', 'PLANO_PAGAMENTO_CLIENTE')
            #    return

            split_client_payment_plan = dict.fromkeys(set([d.code_client for d in db_client_payment_plan]), [])
            logger.info(f'==== Split Pagamentos ' + str(split_client_payment_plan.__len__()))
            for cpp in db_client_payment_plan:
                if cpp.code_client in list(split_client_payment_plan.keys()):
                    if split_client_payment_plan[cpp.code_client] is not None and len(
                            split_client_payment_plan[cpp.code_client]) <= 0:
                        split_client_payment_plan[cpp.code_client] = [cpp.payment_methods]
                    elif len(split_client_payment_plan[cpp.code_client]) > 0:
                        split_client_payment_plan[cpp.code_client].append(cpp.payment_methods)
                    else:
                        split_client_payment_plan[cpp.code_client] = []

            api_payment_plan_list = [PlanoPagamentoCliente(
                codigo_cliente=k,
                formas_pagamento=v) for k, v in split_client_payment_plan.items()]

            send_log(
                job_config_dict.get('job_name'),
                job_config_dict.get('enviar_logs'),
                False,
                f'Enviando os planos de pagamentos dos clientes via api okvendas',
                LogType.INFO,
                'PLANO_PAGAMENTO_CLIENTE')

            for api_client_payment_plan in api_payment_plan_list:
                try:
                    response_list, status_code, lista = api_okvendas.post_client_payment_plan(api_client_payment_plan)
                    message_response = format_response(lista)
                    if not response_list or status_code == 400:
                        send_log(
                            job_config_dict.get('job_name'),
                            job_config_dict.get('enviar_logs'),
                            True,
                            f'Erro ao processar a forma de pagamento do seguinte cliente '
                            f'{api_client_payment_plan.codigo_cliente} {message_response}',
                            LogType.WARNING,
                            'PLANO_PAGAMENTO_CLIENTE')

                    if status_code == 207:
                        send_log(
                            job_config_dict.get('job_name'),
                            job_config_dict.get('enviar_logs'),
                            True,
                            f'Inserção/Atualização parcial das formas de pagamento do seguinte cliente '
                            f'{api_client_payment_plan.codigo_cliente} {message_response}',
                            LogType.WARNING,
                            'PLANO_PAGAMENTO_CLIENTE')

                    if protocol_semaphore_client_payment_plan(job_config_dict, db_config,
                                                              api_client_payment_plan.codigo_cliente):
                        send_log(
                            job_config_dict.get('job_name'),
                            job_config_dict.get('enviar_logs'),
                            False,
                            f'Plano de Pagamento do cliente {api_client_payment_plan.codigo_cliente} '
                            f'protocolado no banco semaforo',
                            LogType.INFO,
                            'PLANO_PAGAMENTO_CLIENTE')
                    else:
                        send_log(
                            job_config_dict.get('job_name'),
                            job_config_dict.get('enviar_logs'),
                            False,
                            f'Falha ao protocolar o plano de pagamento do cliente '
                            f'{api_client_payment_plan.codigo_cliente} ',
                            LogType.WARNING,
                            'PLANO_PAGAMENTO_CLIENTE')

                except Exception as e:
                    send_log(
                        job_config_dict.get('job_name'),
                        job_config_dict.get('enviar_logs'),
                        True,
                        f'Falha ao enviar a forma de pagamento do cliente {api_client_payment_plan.codigo_cliente}'
                        f': {str(e)}',
                        LogType.ERROR,
                        'PLANO_PAGAMENTO_CLIENTE')

        except Exception as ex:
            send_log(
                job_config_dict.get('job_name'),
                job_config_dict.get('enviar_logs'),
                True,
                f'Erro {str(ex)}',
                LogType.ERROR,
                'PLANO_PAGAMENTO_CLIENTE')


def format_response(response):
    message = ''
    lista = response.get('Response')
    if lista is None:
        if response.get('Message') is not None:
            message = response.get('Message')
        return message

    for item in lista:
        if item['Identifiers'] is None or len(item['Identifiers']) <= 0:
            continue

        message = message + f'{item["Message"]} '

    return message


def query_list_client_payment_plan(job_config_dict: dict, db_config: DatabaseConfig) -> List[ClientPaymentPlan]:
    """
        Consultar no banco semáforo os planos de pagamentos dos clientes

        Args:
            job_config_dict: Configuração do job
            db_config: Configuração do banco de dados

        Returns:
        Lista dos planos de pagamentos dos clientes
        """
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        if src.print_payloads:
            print(db_config.sql)

        cursor.execute(db_config.sql)
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        results = list(dict(zip(columns, row)) for row in rows)
        cursor.close()
        conn.close()
        if len(results) > 0:
            lists = [ClientPaymentPlan(**p) for p in results]
            return lists

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                 f' Erro ao consultar os planos de pagamentos dos clientes no banco semaforo: {str(ex)}', LogType.ERROR,
                 'PLANO_PAGAMENTO_CLIENTE')

    return []


def insert_update_semaphore_client_payment_plan(job_config_dict: dict, db_config: DatabaseConfig,
                                                lists: List[ClientPaymentPlan]) -> bool:
    """
    Insere os planos de pagamentos dos clientes no banco semáforo
    Args:
        job_config_dict: Configuração do job
        db_config: Configuracao do banco de dados
        lists: Lista dos planos de pagamentos dos clientes

    Returns:
        Boleano indicando se foram inseridos 1 ou mais registros
    """
    params = [(li.code_client, " ", IntegrationType.PLANO_PAGAMENTO_CLIENTE.value, None, 'SUCESSO') for li in lists]

    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        retorno = False
        for p in params:
            cursor.execute(queries.get_insert_update_semaphore_command(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, list(p)))
            retorno = (cursor.rowcount > 0) if retorno == False else retorno

        cursor.close()
        conn.commit()
        conn.close()
        return retorno

    except Exception as ex:
        send_log(
            job_config_dict.get('job_name'),
            job_config_dict.get('enviar_logs'),
            True,
            f' Erro ao consultar os planos de pagamentos dos clientes no banco semaforo: {str(ex)}',
            LogType.ERROR,
            'PLANO_PAGAMENTO_CLIENTE')

    return False


def protocol_semaphore_client_payment_plan(job_config_dict: dict, db_config: DatabaseConfig, identifier: str) -> bool:
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        if identifier is not None:
            cursor.execute(queries.get_protocol_semaphore_id_command(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, ['SUCESSO', identifier]))
        count = cursor.rowcount
        cursor.close()
        conn.commit()
        conn.close()
        return count > 0

    except Exception as ex:
        send_log(
            job_config_dict.get('job_name'),
            job_config_dict.get('enviar_logs'),
            True,
            f' Erro ao protocolar os planos de pagamentos no banco semaforo: {str(ex)}',
            LogType.ERROR,
            'PLANO_PAGAMENTO_CLIENTE')
