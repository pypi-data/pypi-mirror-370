import logging
import string
from time import sleep
from typing import List
import time
from src.jobs.utils import executa_comando_sql

import src
import src.database.connection as database
from src.api.api_mplace import logger
from src.api.entities.encaminha import Encaminha, EncaminhaOkinghub, EncaminhaOkvendas
from src.database import utils, queries
from src.database.utils import DatabaseConfig
from src.entities.order_queue import queue_status
from src.api import api_mplace as api_Mplace
import src.api.okinghub as api_Okinghub
import src.api.okvendas as api_okVendas
import PySimpleGUI as sg
from threading import Lock
from src.jobs.system_jobs import OnlineLogger
from src.log_types import LogType

lock = Lock()
logger = logging.getLogger()
send_log = OnlineLogger.send_log


def job_sent(job_config: dict):
    with lock:
        try:
            db_config = utils.get_database_config(job_config)
            # Exibe mensagem monstrando que a Thread foi Iniciada
            logger.info(f'==== THREAD INICIADA -job: ' + job_config.get('job_name'))

            # LOG de Inicialização do Método - Para acompanhamento de execução
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Encaminhar Entrega - Iniciado',
                LogType.EXEC,
                'ENCAMINHAR')

            if db_config.sql is None:
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Comando sql para ENCAMINHAR pedidos nao encontrado',
                    LogType.WARNING,
                    'ENCAMINHAR')
                return
            if job_config['executar_query_semaforo'] == 'S':
                executa_comando_sql(db_config, job_config)

            if src.client_data['operacao'].lower().__contains__('mplace'):
                queue = api_Mplace.get_order_queue_mplace(src.client_data, queue_status.get('invoiced'))
                for q_order in queue:
                    sents = query_encaminha_erp(job_config, db_config, q_order.pedido_oking_id)
                    qtd = sents.__len__()
                    if qtd > 0:
                        for sent in sents:
                            try:
                                encaminha_sent = api_Mplace.post_sent_mplace(sent, q_order.pedido_oking_id)
                                if encaminha_sent is None:
                                    update_encaminha(db_config, sent.id)
                                    send_log(
                                        job_config.get('job_name'),
                                        job_config.get('enviar_logs'),
                                        job_config.get('enviar_logs_debug'),
                                        f'Pedido {sent.id} encaminhado com sucesso para MPLACE',
                                        LogType.INFO,
                                        'ENCAMINHAR')
                                    continue
                                else:
                                    send_log(
                                        job_config.get('job_name'),
                                        job_config.get('enviar_logs'),
                                        job_config.get('enviar_logs_debug'),
                                        f'Falha ao encaminhar o pedido {sent.id} para MPLACE:{encaminha_sent}',
                                        LogType.ERROR,
                                        'ENCAMINHAR')
                                    sg.popup(encaminha_sent)
                            except Exception as e:
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'Falha encaminhar pedido {sent.id}: {str(e)}',
                                    LogType.ERROR,
                                    'ENCAMINHAR')
            elif src.client_data['operacao'].lower().__contains__('okvendas'):
                queue = api_okVendas.get_order_queue_okvendas(queue_status.get('invoiced'))
                for q_order in queue:
                    sents = query_encaminha_erp(job_config, db_config, q_order.pedido_oking_id)
                    qtd = sents.__len__()
                    if qtd > 0:
                        for sent in sents:
                            try:
                                encaminha_sent = api_okVendas.post_sent_okvendas(sent)
                                if encaminha_sent is None:
                                    update_encaminha(db_config, sent.id)
                                    send_log(
                                        job_config.get('job_name'),
                                        job_config.get('enviar_logs'),
                                        job_config.get('enviar_logs_debug'),
                                        f'Pedido {sent.id} encaminhado com sucesso para OKVENDAS',
                                        LogType.INFO,
                                        'ENCAMINHAR')
                                    continue
                                else:
                                    send_log(
                                        job_config.get('job_name'),
                                        job_config.get('enviar_logs'),
                                        job_config.get('enviar_logs_debug'),
                                        f'Falha ao encaminhar o pedido {sent.id} para OKVENDAS:{encaminha_sent}',
                                        LogType.ERROR,
                                        'ENCAMINHAR')
                                    sg.popup(encaminha_sent)
                            except Exception as e:
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'Falha encaminhar pedido {sent.id}: {str(e)}',
                                    LogType.ERROR,
                                    'ENCAMINHAR')
            else:
                sents = query_encaminha_erp(job_config, db_config)
                for sent in sents:
                    try:
                        invoice_sent = api_Okinghub.post_sent_okinghub(sent)
                        if invoice_sent is None:
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'Pedido {sent.pedido_oking_id} encaminhado com sucesso para api OkingHub',
                                LogType.INFO,
                                'ENCAMINHAR')
                            continue
                        else:
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'Falha ao encaminhar pedido {sent.pedido_oking_id} para api OkingHub: {invoice_sent}',
                                LogType.ERROR,
                                'ENCAMINHAR')
                    except Exception as e:
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Falha encaminhar o pedido {sent.pedido_oking_id}: {str(e)}',
                            LogType.ERROR,
                            'ENCAMINHAR')

        except Exception as e:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Falha na execução do job: {str(e)}',
                LogType.ERROR,
                'ENCAMINHAR')


def query_encaminha_erp(job_config: dict, db_config: DatabaseConfig, pedido_oking_id=''):
    """
    Consulta os pedidos FATURADOS no banco de dados
    Args:
        job_config: Configuração do job
        db_config: Configuracao do banco de dados
        pedido_oking_id: id do pedido
    Returns:
        Lista de pedidos "FATURADO" para enviar
    """
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    sent = []
    try:
        if db_config.is_oracle():
            conn.outputtypehandler = database.output_type_handler

        newsql = db_config.sql
        if src.client_data['operacao'].lower().__contains__('mplace') or src.client_data['operacao'].lower().__contains__('okvendas'):
            newsql = newsql.replace("@pedido_oking_id", f'{pedido_oking_id}').replace('#v', ',')

        if src.print_payloads:
            print(newsql)

        cursor.execute(newsql.replace(';', ''))
        rows = cursor.fetchall()
        # Garante nomes de colunas em minúsculo para corresponder à classe
        columns = [col[0].lower() for col in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        cursor.close()
        conn.close()

        if len(results) > 0:
            if src.client_data['operacao'].lower().__contains__('okinghub'):
                sent = [EncaminhaOkinghub(**p) for p in results]
            elif src.client_data['operacao'].lower().__contains__('okvendas'):
                sent = [EncaminhaOkvendas(**p) for p in results]
            else:
                sent = [Encaminha(**p) for p in results]

    except Exception as ex:
        logger.error(f'Erro ao consultar pedidos faturados no banco: {str(ex)}')
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Erro ao consultar pedidos faturados no banco: {str(ex)}',
            LogType.ERROR,
            'ENCAMINHAR')

    return sent


def update_encaminha(db_config: DatabaseConfig, pedido_oking_id: str):
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        cursor.execute(queries.update_encaminha_command(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type, [
                           pedido_oking_id]))
        cursor.close()
        conn.commit()
        conn.close()
    except Exception as ex:
        print(f'Erro {ex} ao atualizar a tabela do pedido {pedido_oking_id}')
