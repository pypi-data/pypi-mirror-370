import logging
from typing import List

import PySimpleGUI as sg
from src.jobs.utils import executa_comando_sql

import src
import src.database.connection as database
from src.api.entities.entregue import Entregue, EntregueOkvendas
from src.database import utils, queries
from src.database.utils import DatabaseConfig
from src.entities.order_queue import queue_status
from src.jobs.system_jobs import OnlineLogger
from src.api import api_mplace as api_mplace
from src.api import okinghub as api_oking
import src.api.okvendas as api_okvendas
from threading import Lock
from src.log_types import LogType

logger = logging.getLogger()
send_log = OnlineLogger.send_log
lock = Lock()


def job_delivered(job_config: dict):
    with lock:
        try:
            db_config = utils.get_database_config(job_config)
            # Exibe mensagem monstrando que a Thread foi Iniciada
            logger.info(f'==== THREAD INICIADA -job: ' + job_config.get('job_name'))
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Entregue - Iniciado',
                LogType.EXEC,
                'ENTREGUE')
            if db_config is None:
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Comando sql para entregar pedidos encaminhados nao encontrado',
                    LogType.WARNING,
                    'ENTREGA')
                return
            if job_config['executar_query_semaforo'] == 'S':
                executa_comando_sql(db_config, job_config)

            if src.client_data['operacao'].lower().__contains__('mplace'):
                queue = api_mplace.get_order_queue_mplace(src.client_data, queue_status.get('shipped'))
                for q_order in queue:
                    deliveries = query_entrega_erp(job_config, db_config, q_order.pedido_oking_id)
                    qtd = deliveries.__len__()
                    if qtd > 0:
                        for deliver in deliveries:
                            try:
                                encaminha_deliver = api_mplace.post_deliver_mplace(deliver)
                                if encaminha_deliver is None:
                                    send_log(
                                        job_config.get('job_name'),
                                        job_config.get('enviar_logs'),
                                        job_config.get('enviar_logs_debug'),
                                        f'Pedido {deliver.id} entregue com sucesso para api mplace',
                                        LogType.INFO,
                                        'PEDIDO')
                                    update_entrega(db_config, deliver.id)
                                    continue
                                else:
                                    send_log(
                                        job_config.get('job_name'),
                                        job_config.get('enviar_logs'),
                                        job_config.get('enviar_logs_debug'),
                                        f'Falha entregar o pedido {deliver.id} para api mplace: {encaminha_deliver}',
                                        LogType.ERROR,
                                        'PEDIDO')
                                    sg.popup(encaminha_deliver)
                            except Exception as e:
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'Falha ao entregar o pedido {deliver.id}: {str(e)}',
                                    LogType.ERROR,
                                    'PEDIDO')
            elif src.client_data['operacao'].lower().__contains__('okvendas'):
                queue = api_okvendas.get_order_queue_okvendas(queue_status.get('shipped'))
                for q_order in queue:
                    deliveries = query_entrega_erp(job_config, db_config, q_order.pedido_oking_id)
                    qtd = deliveries.__len__()
                    if qtd > 0:
                        for deliver in deliveries:
                            try:
                                encaminha_deliver = api_okvendas.post_deliver_okvendas(deliver)
                                if encaminha_deliver is None:
                                    send_log(
                                        job_config.get('job_name'),
                                        job_config.get('enviar_logs'),
                                        job_config.get('enviar_logs_debug'),
                                        f'Pedido {deliver.id} entregue com sucesso para api okvendas',
                                        LogType.INFO,
                                        'PEDIDO')
                                    update_entrega(db_config, deliver.id)
                                    continue
                                else:
                                    send_log(
                                        job_config.get('job_name'),
                                        job_config.get('enviar_logs'),
                                        job_config.get('enviar_logs_debug'),
                                        f'Falha entregar o pedido {deliver.id} para api okvendas: {encaminha_deliver}',
                                        LogType.ERROR,
                                        'PEDIDO')
                                    sg.popup(encaminha_deliver)
                            except Exception as e:
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'Falha ao entregar o pedido {deliver.id}: {str(e)}',
                                    LogType.ERROR,
                                    'PEDIDO')
            else:
                queue = api_oking.get_order_queue(src.client_data, queue_status.get('shipped'))
                for q_order in queue:
                    deliveries = query_entrega_erp(job_config, db_config, q_order.pedido_oking_id)
                    qtd = deliveries.__len__()
                    if qtd > 0:
                        for deliver in deliveries:
                            try:
                                encaminha_deliver = api_oking.post_delivered_okinghub(deliver)
                                if encaminha_deliver is None:
                                    send_log(
                                        job_config.get('job_name'),
                                        job_config.get('enviar_logs'),
                                        job_config.get('enviar_logs_debug'),
                                        f'Pedido {deliver.id} entregue com sucesso para api okinghub',
                                        LogType.INFO,
                                        'PEDIDO')
                                    update_entrega(db_config, deliver.id)
                                    continue
                                else:
                                    send_log(
                                        job_config.get('job_name'),
                                        job_config.get('enviar_logs'),
                                        job_config.get('enviar_logs_debug'),
                                        f'Falha entregar o pedido {deliver.id} para api okinghub: {encaminha_deliver}',
                                        LogType.ERROR,
                                        'PEDIDO')
                                    sg.popup(encaminha_deliver)
                            except Exception as e:
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'Falha ao entregar o pedido {deliver.id}: {str(e)}',
                                    LogType.ERROR,
                                    'PEDIDO')
        except Exception as e:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Falha na execução do job: {str(e)}',
                LogType.ERROR,
                'PEDIDO')


def query_entrega_erp(job_config: dict, db_config: DatabaseConfig, pedido_oking_id=''):
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    delivery = []
    try:
        if db_config.is_oracle():
            conn.outputtypehandler = database.output_type_handler

        newsql = db_config.sql.lower()
        if src.client_data['operacao'].lower().__contains__('mplace') \
                or src.client_data['operacao'].lower().__contains__('okvendas'):
            newsql = newsql.replace("@pedido_oking_id", f'{pedido_oking_id}').replace('#v', ',')
        if src.print_payloads:
            print(newsql)
        cursor.execute(newsql.lower().replace(';', ''))
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        cursor.close()
        conn.close()
        if len(results) > 0:
            if src.client_data['operacao'].lower().__contains__('okvendas'):
                delivery = [EntregueOkvendas(**p) for p in results]
            else:
                delivery = [Entregue(**p) for p in results]

    except Exception as ex:
        logger.error(f' ')
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Erro ao consultar pedidos enviados no banco: {str(ex)}',
            LogType.ERROR,
            'PEDIDO')

    return delivery


def update_entrega(db_config: DatabaseConfig, pedido_oking_id: str):
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        cursor.execute(queries.update_entrega_command(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type, [
                           pedido_oking_id]))
        cursor.close()
        conn.commit()
        conn.close()
    except Exception as ex:
        print(f'Erro {ex} ao atualizar a tabela do pedido {pedido_oking_id}')
