import logging
import string
from datetime import datetime
from threading import Lock
from time import sleep
from typing import List

import PySimpleGUI as sg
from src.jobs.utils import executa_comando_sql

import src
import src.api.api_mplace as api_Mplace
import src.api.okinghub as api_okHUB
import src.api.okvendas as api_okVendas
import src.database.connection as database
import src.database.utils as utils
import re
from src.api.entities.pedido import Queue, Order, OrderMplace, OrderOkvendas
from src.database import queries
from src.database.queries import IntegrationType
from src.database.utils import DatabaseConfig
from src.entities.invoice import Invoice, InvoiceOkvendas, InvoiceMplace
from src.jobs.system_jobs import OnlineLogger
from src.log_types import LogType

logger = logging.getLogger()
send_log = OnlineLogger.send_log
lock = Lock()

default_limit = 50
queue_status = {
    'pending': 'PENDENTE',
    'AGUARDANDO_PAGAMENTO': 'AGUARDANDO_PAGAMENTO',
    'paid': 'PAGO',
    'APROVADO': 'APROVADO',
    'invoiced': 'FATURADO',
    'em_processamento': 'EM_PROCESSAMENTO',
    'canceled': 'CANCELADO',
    'shipped': 'ENCAMINHADO',
    'delivered': 'ENTREGUE',
    'paid_order': 'PEDIDO_PAGO',
    'order': 'PEDIDO'
}


def define_job_start(job_config: dict) -> None:
    global current_job
    current_job = job_config.get('job_name')
    try:
        # Inicia o job a partir dos pedidos AgPagamento
        if current_job == 'internaliza_pedidos_job' or current_job == 'internaliza_pedidos_b2b_job':
            with lock:
                # Exibe mensagem monstrando que a Thread foi Iniciada
                logger.info(f'==== THREAD INICIADA -job: ' + job_config.get('job_name'))
                job_orders(job_config, True)
        # Inicia o job a partir do pedidos pagos
        elif current_job == 'internaliza_pedidos_pagos_job' or current_job == 'internaliza_pedidos_pagos_b2b_job':
            with lock:
                # Exibe mensagem monstrando que a Thread foi Iniciada
                logger.info(f'==== THREAD INICIADA -job: ' + job_config.get('job_name'))
                job_orders(job_config)
    except Exception as e:
        raise e


def job_orders(job_config: dict, start_at_pending: bool = False) -> None:
    try:
        db_config = utils.get_database_config(job_config)
        logger.info(f'======= OPERACAO  {src.client_data["operacao"].lower()}  =======')

        if 'mplace' in src.client_data['operacao'].lower():
            logger.info(f'======= Operação MPLACE =======')
            if start_at_pending:
                process_order_queue_mplace(job_config, queue_status.get('AGUARDANDO_PAGAMENTO'), db_config, True)
            process_order_queue_mplace(job_config, queue_status.get('APROVADO'), db_config, True)
            # process_order_queue_mplace(job_config, queue_status.get('canceled'), db_config)

        elif 'okvendas' in src.client_data['operacao'].lower():
            logger.info(f'======= Operação OKVENDAS  =======')
            if start_at_pending:
                process_order_queue_okvendas(job_config, queue_status.get('order'), db_config, True)
            process_order_queue_okvendas(job_config, queue_status.get('paid_order'), db_config, True)
            process_order_queue_okvendas(job_config, queue_status.get('canceled'), db_config)
        # ======= Operação OKING HUB =======
        else:
            logger.info(f'======= Operação OKING HUB =======')
            if start_at_pending:
                process_order_queue(job_config, queue_status.get('pending'), db_config, True)
            process_order_queue(job_config, queue_status.get('APROVADO'), db_config, True)
            process_order_queue(job_config, queue_status.get('canceled'), db_config)

    except Exception as e:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Erro ao inicializar job: {str(e)}',
            LogType.ERROR,
            'PEDIDO')
        raise e


def job_envia_notafiscal(job_config: dict):
    with lock:
        db_config = utils.get_database_config(job_config)
        # Exibe mensagem monstrando que a Thread foi Iniciada
        logger.info(f'==== THREAD INICIADA -job: ' + job_config.get('job_name'))

        # LOG de Inicialização do Método - Para acompanhamento de execução
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Enviar Nota Fiscal - Iniciado',
            LogType.EXEC,
            'NOTAFISCAL')

        if db_config.sql is None:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Comando sql para baixar notas fiscais nao encontrado',
                LogType.WARNING,
                'ENVIA_NOTAFISCAL')
            return
        if job_config['executar_query_semaforo'] == 'S':
            executa_comando_sql(db_config, job_config)

        if src.client_data['operacao'].lower().__contains__('mplace'):  # Operação Mplace
            queue = api_Mplace.get_order_queue_mplace(src.client_data, queue_status.get('em_processamento'))

            for q_order in queue:
                invoices = query_invoices(job_config, db_config, q_order.pedido_oking_id)
                # Consultar no banco de dados o pedido
                qtd = invoices.__len__()
                # Consulta fila pedidos processamento
                if qtd > 0:
                    for invoice in invoices:
                        try:
                            invoice_sent = api_Mplace.post_invoices_mplace(q_order.pedido_oking_id, invoice)
                            if invoice_sent is None:
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'NF do pedido {invoice.pedido_oking_id} enviada com sucesso para api mplace',
                                    LogType.INFO,
                                    'PEDIDO')
                                versao = "pedido_oking_id" if job_config.get("old_version") == 'N' else "pedido_id"
                                db = database.Connection(db_config)
                                conn = db.get_conect()
                                cursor = conn.cursor()
                                cursor.execute(
                                    queries.get_update_data_sincronizacao_nf_command(db_config.db_type, versao),
                                    queries.get_command_parameter(db_config.db_type, [invoice.pedido_oking_id]))
                                cursor.close()
                                conn.commit()
                                conn.close()
                                continue
                            else:
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'Falha ao enviar NF do pedido {invoice.pedido_oking_id} '
                                    f'para api mplace: {invoice_sent}',
                                    LogType.ERROR,
                                    'NOTAFISCAL')
                                if src.exibir_interface_grafica:
                                    sg.popup(invoice_sent)
                        except Exception as e:
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'Falha ao enviar NF do pedido {invoice.pedido_oking_id}: {str(e)}',
                                LogType.ERROR,
                                'NOTAFISCAL')
                            raise e
                    else:
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Nenhum pedido encontrado',
                            LogType.ERROR,
                            'PEDIDO')
        elif src.client_data['operacao'].lower().__contains__('okvendas'):
            queue = api_okVendas.get_order_queue_okvendas(queue_status.get('paid_order'))
            for q_order in queue:
                invoices = query_invoices(job_config, db_config, q_order.pedido_oking_id)
                qtd = invoices.__len__()
                if qtd > 0:
                    for invoice in invoices:
                        try:
                            invoice_sent = api_okVendas.post_invoices(invoice)
                            if invoice_sent is None:
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'NF do pedido {invoice.id} enviada com sucesso para api okvendas',
                                    LogType.INFO,
                                    'PEDIDO')
                                versao = "pedido_oking_id" if job_config.get("old_version") == 'N' else "pedido_id"
                                db = database.Connection(db_config)
                                conn = db.get_conect()
                                cursor = conn.cursor()
                                cursor.execute(
                                    queries.get_update_data_sincronizacao_nf_command(db_config.db_type, versao),
                                    queries.get_command_parameter(db_config.db_type, [invoice.id]))
                                cursor.close()
                                conn.commit()
                                conn.close()
                                protocola_notafiscal = api_okVendas.put_protocol_order_okvendas([q_order.protocolo])
                                if protocola_notafiscal:
                                    send_log(
                                        job_config.get('job_name'),
                                        job_config.get('enviar_logs'),
                                        job_config.get('enviar_logs_debug'),
                                        f'Nota Fiscal protocolada via api OkVendas',
                                        LogType.INFO,
                                        'NOTAFISCAL')
                                else:
                                    send_log(
                                        job_config.get('job_name'),
                                        job_config.get('enviar_logs'),
                                        job_config.get('enviar_logs_debug'),
                                        f'Falha ao protocolar Nota Fiscal via api OkVendas',
                                        LogType.WARNING,
                                        'NOTAFISCAL')
                                continue
                            else:
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'Falha ao enviar NF do pedido {invoice.id} '
                                    f'para api okvendas: {invoice_sent.message}',
                                    LogType.ERROR,
                                    'NOTAFISCAL')
                        except Exception as e:
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'Falha ao enviar NF do pedido {invoice.id}: {str(e)}',
                                LogType.ERROR,
                                'NOTAFISCAL')


def job_envia_notafiscal_semfila(job_config: dict):
    with lock:
        db_config = utils.get_database_config(job_config)
        # Exibe mensagem monstrando que a Thread foi Iniciada
        logger.info(f'==== THREAD INICIADA -job: ' + job_config.get('job_name'))

        # LOG de Inicialização do Método - Para acompanhamento de execução
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Envia Nota Fiscal Sem Fila - Iniciado',
            LogType.EXEC,
            'NOTASEMFILA')

        if db_config.sql is None:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Comando sql para baixar notas fiscais nao encontrado',
                LogType.WARNING,
                'NOTASEMFILA')
            return
        if job_config['executar_query_semaforo'] == 'S':
            executa_comando_sql(db_config, job_config)
        if src.client_data['operacao'].lower().__contains__('okvendas'):
            invoices = query_invoices(job_config, db_config)
            qtd = invoices.__len__()
            if qtd > 0:
                for invoice in invoices:
                    try:
                        invoice_sent = api_okVendas.post_invoices(invoice)
                        if invoice_sent is None:
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'NF do pedido {invoice.id} enviada com sucesso para api okvendas',
                                LogType.INFO,
                                'PEDIDO')
                            versao = "pedido_oking_id" if job_config.get("old_version") == 'N' else "pedido_id"
                            protocola_notafiscal = update_sincronization_nf(db_config, invoice.id, versao)
                            if protocola_notafiscal:
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'Nota Fiscal protocolada via api OkVendas',
                                    LogType.INFO,
                                    'PEDIDO')
                            else:
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'Falha ao protocolar Nota Fiscal via api OkVendas',
                                    LogType.WARNING,
                                    'NOTASEMFILA')
                            continue
                        else:
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'Falha ao enviar NF do pedido {invoice.id} para api okvendas: {invoice_sent.message}',
                                LogType.ERROR,
                                'NOTASEMFILA')
                    except Exception as e:
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Falha ao enviar NF do pedido {invoice.id}: {str(e)}',
                            LogType.ERROR,
                            'NOTASEMFILA')

                        raise e
            else:  # Não Retornou nenhum Nota
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Nenhuma Nota Fiscail encontrada',
                    LogType.WARNING,
                    'NOTASEMFILA')
        else:  # Operação OKING
            invoices = query_invoices(job_config, db_config)
            for invoice in invoices:
                try:
                    invoice_sent = api_okHUB.post_faturar(invoice)
                    if invoice_sent is None:
                        versao = "pedido_oking_id" if job_config.get("old_version") == 'N' else "pedido_id"
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'NF do pedido {invoice.pedido_oking_id} enviada com sucesso para api Oking',
                            LogType.INFO,
                            'PEDIDO')
                        update_sincronization_nf(db_config, invoice.pedido_oking_id, versao)
                    else:
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Falha ao enviar NF do pedido {invoice.pedido_oking_id} para api Oking: {invoice_sent}',
                            LogType.ERROR,
                            'NOTAFISCAL')
                except Exception as e:
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f'Falha ao enviar NF do pedido {invoice.pedido_oking_id}: {str(e)}',
                        LogType.ERROR,
                        'NOTAFISCAL')
                    raise e


def update_sincronization_nf(db_config, id, versao):
    try:
        db = database.Connection(db_config)
        conn = db.get_conect()
        cursor = conn.cursor()
        cursor.execute(
            queries.get_update_data_sincronizacao_nf_command(db_config.db_type, versao),
            queries.get_command_parameter(db_config.db_type, [id]))

        if cursor.rowcount == 0:
            logger.warning(f'Nenhum registro foi alterado durante a sincronização da data da Nota Fiscal')
            return False

        cursor.close()
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.warning(f'Falha ao sincronizar a data, erro {str(e)}')
        return False


# region Order - OKINGHUB
def process_order_queue(job_config: dict, status: str, db_config: DatabaseConfig,
                        status_to_insert: bool = False) -> None:
    try:
        print()
        print()
        queue = []
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Consultando fila de pedidos no status {status}',
            LogType.INFO,
            'PEDIDO')

        # LOG de Inicialização do Método - Para acompanhamento de execução
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Pedido - Iniciado[{status}]',
            LogType.EXEC,
            'PEDIDO')
        if job_config['executar_query_semaforo'] == 'S':
            executa_comando_sql(db_config, job_config)
        queue = api_okHUB.get_order_queue(src.client_data, status)

        qty = 0
        for q_order in queue:
            try:
                sleep(0.5)
                qty = qty + 1
                print()
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Iniciando processamento ({qty} de {len(queue)}) Pedido OKING ID: {q_order.pedido_oking_id}',
                    LogType.INFO,
                    'PEDIDO')
                order = api_okHUB.get_order(src.client_data, q_order.pedido_oking_id)
                # Pedido integrado anteriormente
                if order.capa.numero_pedido_externo is not None and order.capa.numero_pedido_externo != '':

                    if check_order_existence(db_config, int(order.capa.pedido_oking_id)):
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Pedido ja integrado com o ERP, chamando procedure de atualizacao...',
                            LogType.INFO,
                            'PEDIDO')
                        if call_update_order_procedure(job_config, db_config, int(order.capa.pedido_oking_id),
                                                       order.capa.status):
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'Pedido atualizado com sucesso',
                                LogType.INFO,
                                'PEDIDO')
                            set_codigo_erp_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                                 order_erp_id=order.capa.numero_pedido_externo, client_erp_id='')
                    else:
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Pedido {order.capa.pedido_oking_id} nao existe no banco semaforo porem ja foi integrado '
                            f'previamente. Protocolando pedido...',
                            LogType.WARNING,
                            'PEDIDO')
                        protocol_non_existent_order(job_config, q_order)

                else:  # Pedido nao integrado anteriormente
                    # Pedido existente no banco semaforo
                    if check_non_integrated_order_existence(db_config,
                                                            int(order.capa.pedido_oking_id)):
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Pedido já existente no banco semáforo, porem nao integrado com erp. Chamando procedures',
                            LogType.INFO,
                            'PEDIDO')
                        # Chama a Procedure para Inserir o Pedido no ERP (cliente)
                        sp_success, client_erp_id, order_erp_id = call_order_procedures(job_config, db_config,
                                                                                        int(order.capa.pedido_oking_id))
                        log = query_get_log_integracao2(db_config, q_order.pedido_oking_id)
                        if log:
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'Log de integração do pedido - {q_order.pedido_oking_id}: {log}',
                                LogType.ERROR,
                                'PEDIDO')
                        if sp_success:
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'Chamadas das procedures executadas com sucesso, protocolando pedido...',
                                LogType.INFO,
                                'PEDIDO')
                            set_codigo_erp_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                                 order_erp_id=order_erp_id, client_erp_id=client_erp_id)

                    # Pedido nao existe no semaforo e esta em status de internalizacao (pending e paid)
                    elif status_to_insert:
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Inserindo novo pedido no banco semaforo',
                            LogType.INFO,
                            'PEDIDO')
                        inserted = insert_temp_order(job_config, order, db_config)
                        if inserted:
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'Pedido inserido com sucesso, chamando procedures...',
                                LogType.INFO,
                                'PEDIDO')
                            # Chama a Procedure para Inserir o Pedido no ERP (cliente)
                            sp_success, client_erp_id, order_erp_id = call_order_procedures(job_config, db_config,
                                                                                            int(order.capa
                                                                                                .pedido_oking_id))
                            # ======================================================================
                            # Verifica se conseguiu Inserir o Cliente caso contrário consulta o Log
                            if client_erp_id:
                                logcli = query_get_log_integracaoCliente(db_config, q_order.pedido_oking_id)

                                # ======================================================================
                            log = query_get_log_integracao2(db_config, q_order.pedido_oking_id)
                            if log:
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'Log de integração do pedido - {q_order.pedido_oking_id}: {log}',
                                    LogType.ERROR,
                                    'PEDIDO')
                            if sp_success:
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'Chamadas das procedures executadas com sucesso, protocolando pedido...',
                                    LogType.INFO,
                                    'PEDIDO')
                                set_codigo_erp_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                                     order_erp_id=order_erp_id, client_erp_id=client_erp_id)

                    else:  # Pedido nao existe no semaforo e nao esta em status de internalizacao (pending e paid)
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Pedido nao existente no banco semaforo e nao se encontra em status de internalizacao',
                            LogType.WARNING,
                            'PEDIDO')

            except Exception as e:
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Erro no processamento do pedido {q_order.pedido_oking_id}: {str(e)}',
                    LogType.ERROR,
                    q_order.pedido_oking_id)
    except Exception as e:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Erro ao inicializar job de processamento de pedidos do status {status}: {str(e)}',
            LogType.ERROR,
            'PEDIDO')
        raise


# endregion
def call_update_order_procedure(job_config: dict, db_config: DatabaseConfig, pedido_oking_id: int, status: str) -> bool:
    success = True
    db = database.Connection(db_config)
    conn = db.get_conect()
    try:
        if src.print_payloads:
            print(f"Pedido OKING: {pedido_oking_id} ")
            print(f"      Status: {status} ")

        cursor = conn.cursor()
        updated: bool = False
        if db_config.is_sql_server():
            cursor.execute('SET NOCOUNT ON;'
                           'DECLARE @pedido_erp_output INT;'
                           'exec openk_semaforo.sp_atualiza_pedido @pedido = ?,@status = ?, '
                           '@pedido_erp = @pedido_erp_output OUTPUT;'
                           'SELECT @pedido_erp_output as pedido_erp;', pedido_oking_id, status)
            row = cursor.fetchone()
            if row[0] > 0:
                updated = True
        elif db_config.is_oracle():
            order_updated = cursor.var(int)
            cursor.callproc('OPENK_SEMAFORO.SP_ATUALIZA_PEDIDO',
                            [pedido_oking_id, status, order_updated])
            updated = order_updated.getvalue()
        elif db_config.is_mysql():
            order_updated = 0
            args = (pedido_oking_id, status, order_updated)
            result_args = cursor.callproc('openk_semaforo.SP_ATUALIZA_PEDIDO', args)
            if result_args[2] > 0:
                updated = True
        elif db_config.is_firebird():
            args = (pedido_oking_id, status)
            cursor.callproc('SP_ATUALIZA_PEDIDO', args)
            result_args = cursor.fetchone()
            order_updated = result_args[0]
            if order_updated > 0:
                updated = True

        if updated is None or updated <= 0:
            success = False
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'P.2-Pedido [{pedido_oking_id}] - Nao foi possivel atualizar o pedido informado',
                LogType.WARNING,
                f'PEDIDO_{pedido_oking_id}_UPD')

        cursor.close()
        if success:
            conn.commit()
        else:
            conn.rollback()
        conn.close()
        return success
    except Exception as e:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Erro no método de chamada da procedure de atualização do pedido {pedido_oking_id}: {str(e)}',
            LogType.ERROR,
            str(pedido_oking_id))
        conn.rollback()
        conn.close()


def check_order_existence(db_config: DatabaseConfig, pedido_oking_id: int) -> bool:
    db = database.Connection(db_config)
    conn = db.get_conect()
    try:
        cursor = conn.cursor()
        cursor.execute(queries.get_query_order(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type, [pedido_oking_id]))
        existent_order = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return existent_order is not None and existent_order > 0
    except Exception as e:
        conn.close()
        return False


def set_codigo_erp_order(job_config: dict, db_config: DatabaseConfig, order: Order | OrderMplace | OrderOkvendas,
                         queue_order: Queue, order_erp_id: str = '', client_erp_id: str = '') -> None:
    db = database.Connection(db_config)
    try:
        conn = db.get_conect()
        cursor = conn.cursor()
        if order_erp_id != '':
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'P.1-ERP-Pedido [{order.id}] - Protocolando pedido com codigo_referencia {order_erp_id}',
                LogType.INFO,
                f'PED_{order.id}_P.1-ERP')

            if src.client_data['operacao'].lower().__contains__('mplace'):
                # colocar o pedido em processamento. [EM_PROCESSAMENTO]
                if queue_order.status.lower() != 'cancelado':
                    api_Mplace.post_order_processing_mplace(order.order_id)
                    updated_order_code = api_Mplace.put_order_erp_code_mplace(order.order_id, order_erp_id)
                else:
                    updated_order_code = True
            elif src.client_data['operacao'].lower().__contains__('okvendas'):
                updated_order_code = api_okVendas.put_order_erp_code(
                    int(order.id),
                    order_erp_id)
            else:
                dict_order = {
                    "numero_pedido_externo": order_erp_id,
                    "observacao": "Duplicado no ERP" if job_config.get(
                        'job_name') == 'duplicar_pedido_internalizado_job' else "Internalizado no ERP",
                    "token": src.client_data['token_oking'],
                    "protocolo": order.protocolo
                }
                if job_config.get('job_name') == 'duplicar_pedido_internalizado_job':
                    updated_order_code = api_okHUB.post_protocol_duplicated_order(dict_order)
                else:
                    updated_order_code = api_okHUB.post_order_erp_code(dict_order)
            if updated_order_code:
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'P.2-ERP-Pedido [{order.id}] - Codigo Erp do pedido atualizado via api',
                    LogType.INFO,
                    f'PED_{order.id}_P.2-ERP')
            else:
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'P.3-ERP-Pedido [{order.id}] - Falha ao atualizar o Codigo Erp do pedido via api',
                    LogType.WARNING,
                    f'PED_{order.id}_P.3-ERP')

        if client_erp_id != '' and client_erp_id is not None:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'P.4-ERP-Pedido [{order.id}] - Salvando codigo do erp do cliente no banco semaforo {client_erp_id}',
                LogType.INFO,
                f'PED_{order.id}_P.4-ERP')
            logger.info(f'======= Antes do get client protocol command {src.client_data["operacao"].lower()} =======')
            if src.client_data['operacao'].lower().__contains__('mplace'):
                logger.info(f'======= Get client protocol command =======')
                cursor.execute(queries.get_client_protocol_command(db_config.db_type),
                               queries.get_command_parameter(db_config.db_type,
                                                             [client_erp_id, order.order_id]))

            elif src.client_data['operacao'].lower().__contains__('okvendas'):
                cursor.execute(queries.get_client_protocol_command(db_config.db_type),
                               queries.get_command_parameter(db_config.db_type,
                                                             [client_erp_id, order.id]))
            else:
                cursor.execute(queries.get_client_protocol_command(db_config.db_type),
                               queries.get_command_parameter(db_config.db_type,
                                                             [client_erp_id, order.capa.pedido_oking_id]))

            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'P.5-ERP-Pedido [{order.id}] - Protocolando cliente via api com codigo_referencia {client_erp_id}',
                LogType.INFO,
                f'PED_{order.id}_P.5-ERP')

            if src.client_data['operacao'].lower().__contains__('okvendas'):
                updated_client_code = api_okVendas.put_client_erp_code(
                    {
                        'cpf_cnpj': order.usuario.cpf if order.usuario.cpf is not None and order.usuario.cpf != '' else order.usuario.cnpj,
                        'codigo_cliente': client_erp_id
                    })

                if updated_client_code:
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f'P.6-ERP-Pedido [{order.id}] - Codigo Erp do cliente atualizado via api okvendas',
                        LogType.INFO,
                        f'PED_{order.id}_P.6-ERP')
                else:
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f'P.7-ERP-Pedido [{order.id}] - Falha ao atualizar o Codigo Erp do cliente via api okvendas',
                        LogType.WARNING,
                        f'PED_{order.id}_P.7-ERP')

        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'P.8-ERP-Pedido [{order.id}] - Removendo pedido da fila pelo protocolo {queue_order.protocolo}',
            LogType.INFO,
            f'PED_{order.id}_P.8-ERP')

        if src.client_data['operacao'].lower().__contains__('mplace'):
            # protocoled_order = api_Mplace.put_protocol_orders_mplace(queue_order.protocolo)
            # não há necessidade de tirar ele da fila, pois o método anterior coloca em outra fila
            if queue_order.status.lower() == 'cancelado':
                protocoled_order = api_Mplace.put_protocol_orders_mplace(queue_order.protocolo)
            else:
                protocoled_order = True
        elif src.client_data['operacao'].lower().__contains__('okvendas'):
            protocoled_order = api_okVendas.put_protocol_order_okvendas([queue_order.protocolo])
        else:
            protocoled_order = api_okHUB.put_protocol_orders([queue_order.protocolo])

        if protocoled_order:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'P.9-ERP-Pedido [{order.id}] - Pedido protocolado via api',
                LogType.INFO,
                f'PED_{order.id}_P.9-ERP')
        else:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'P.10-ERP-Pedido [{order.id}] - Falha ao protocolar pedido via api',
                LogType.WARNING,
                f'PED_{order.id}_P.10-ERP')

        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'P.11-ERP-Pedido [{order.id}] - Protocolando pedido no banco semaforo',
            LogType.INFO,
            f'PED_{order.id}_P.11-ERP')

        if src.client_data['operacao'].lower().__contains__('mplace'):
            logger.info('======= Order protocol command Mplace =======')
            cursor.execute(queries.get_order_protocol_command(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [order_erp_id, order.order_id]))
        elif src.client_data['operacao'].lower().__contains__('okvendas'):
            cursor.execute(queries.get_order_protocol_command(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [order_erp_id, order.id]))
        else:
            cursor.execute(queries.get_order_protocol_command(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [order_erp_id, order.capa.pedido_oking_id]))

        cursor.close()
        conn.commit()
        conn.close()
    except Exception as e:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Erro ao protocolar pedidos: {str(e)}',
            LogType.ERROR,
            order_erp_id)


def protocol_non_existent_order(job_config: dict, queue_order: Queue) -> None:
    try:
        if src.client_data['operacao'].lower().__contains__('mplace'):
            protocoled_order = api_Mplace.put_protocol_orders_mplace(queue_order.protocolo)
            if protocoled_order:
                logger.info(
                    job_config.get('job_name') + f' | Pedido {queue_order.pedido_oking_id} protocolado via api Mplace')
            else:
                logger.warning(
                    job_config.get(
                        'job_name') + f' | Falha ao protocolar pedido {queue_order.pedido_oking_id} via api Mplace')
        elif src.client_data['operacao'].lower().__contains__('okvendas'):
            protocoled_order = api_okVendas.put_protocol_order_okvendas([queue_order.protocolo])
            if protocoled_order:
                logger.info(job_config.get(
                    'job_name') + f' | Pedido {queue_order.pedido_oking_id} protocolado via api Okvendas')
            else:
                logger.warning(
                    job_config.get(
                        'job_name') + f' | Falha ao protocolar pedido {queue_order.pedido_oking_id} via api Okvendas')
        else:
            protocoled_order = api_okHUB.put_protocol_orders([queue_order.protocolo])
            if protocoled_order:
                logger.info(job_config.get(
                    'job_name') + f' | Pedido {queue_order.pedido_oking_id} protocolado via api OkingHub')
            else:
                logger.warning(
                    job_config.get(
                        'job_name') + f' | Falha ao protocolar pedido {queue_order.pedido_oking_id} via api OkingHub')

    except Exception as ex:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Erro ao protocolar pedido {queue_order.pedido_oking_id}: {str(ex)}',
            LogType.ERROR,
            queue_order.pedido_oking_id)


def insert_temp_order(job_config: dict, order: Order, db_config: DatabaseConfig) -> bool:
    step = ''
    db = database.Connection(db_config)
    conn = db.get_conect()
    try:
        step = 'conexao'
        cursor = conn.cursor()

        existent_client = None

        client_cpf_cnpj = order.usuario.cpf_cnpj
        client_cpf_cnpj = client_cpf_cnpj.translate(str.maketrans('', '', string.punctuation))
        cursor.execute(queries.get_query_cliente_cpfcnpj(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type, [
                           client_cpf_cnpj]))

        # existent_client = None
        # if order.usuario.codigo_referencia_erp is not None and order.usuario.codigo_referencia_erp != '' \
        #         and order.usuario.codigo_referencia_erp != '0':  # Por padrao o erp_code vem = '0' da api okvendas
        #     cursor.execute(queries.get_query_client_erp(db_config.db_type),
        #                    queries.get_command_parameter(db_config.db_type, [order.usuario.codigo_referencia_erp]))
        #     existent_client = cursor.fetchone()

        if existent_client is None:
            # insere cliente

            step = 'P.1 -Insere NOVO cliente'
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'\tPedido {order.capa.pedido_oking_id}: Inserindo cliente',
                LogType.INFO,
                'PEDIDO')
            cursor.execute(queries.get_insert_client_command(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [
                               order.usuario.nome or order.usuario.razao_social,
                               order.usuario.razao_social or order.usuario.nome,
                               order.usuario.sexo,
                               order.usuario.email,
                               order.usuario.rg,
                               order.usuario.orgao,
                               order.usuario.data_nascimento_constituicao,
                               order.usuario.telefone_residencial,
                               order.usuario.telefone_celular,
                               order.usuario.inscricao_estadual,
                               order.usuario.inscricao_municipal,
                               order.usuario.codigo_representante,
                               order.usuario.endereco_cobranca.cep,
                               order.usuario.endereco_cobranca.tipo_logradouro,
                               order.usuario.endereco_cobranca.endereco,
                               order.usuario.endereco_cobranca.numero,
                               order.usuario.endereco_cobranca.complemento,
                               order.usuario.endereco_cobranca.bairro or " ",
                               order.usuario.endereco_cobranca.cidade,
                               order.usuario.endereco_cobranca.estado,
                               order.usuario.endereco_cobranca.referencia_entrega,
                               order.usuario.endereco_cobranca.codigo_ibge,
                               'IN'
                           ]))
        else:
            # update no cliente existente
            step = 'P.1 -Atualizando Cliente Existente'
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'\tPedido {order.capa.pedido_oking_id}: Atualizando cliente existente',
                LogType.INFO,
                'PEDIDO')
            cursor.execute(queries.get_update_client_sql(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [
                               order.usuario.nome or order.usuario.razao_social,
                               order.usuario.razao_social or order.usuario.nome,
                               order.usuario.sexo,
                               order.usuario.email,
                               order.usuario.rg,
                               order.usuario.orgao,
                               order.usuario.data_nascimento_constituicao,
                               order.usuario.telefone_residencial,
                               order.usuario.telefone_celular,
                               order.usuario.inscricao_estadual,
                               order.usuario.inscricao_municipal,
                               order.usuario.codigo_representante,
                               order.usuario.endereco_cobranca.cep,
                               order.usuario.endereco_cobranca.tipo_logradouro,
                               order.usuario.endereco_cobranca.endereco,
                               order.usuario.endereco_cobranca.numero,
                               order.usuario.endereco_cobranca.complemento,
                               order.usuario.endereco_cobranca.bairro or " ",
                               order.usuario.endereco_cobranca.cidade,
                               order.usuario.endereco_cobranca.estado,
                               order.usuario.endereco_cobranca.referencia_entrega,
                               order.usuario.endereco_cobranca.codigo_ibge
                           ]))

        step = 'P.2 - Antes de Executar a Querys'
        # if cursor.rowcount > 0:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Cliente inserido/atualizado para o pedido {order.capa.pedido_oking_id}',
            LogType.INFO,
            'PEDIDO')
        cursor.execute(queries.get_query_cliente_cpfcnpj(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type, [
                           order.usuario.cpf_cnpj.translate(str.maketrans('', '', string.punctuation))]))
        step = 'P.3 - Queries executada'
        (client_id,) = cursor.fetchone()
        if client_id is None or client_id <= 0:
            cursor.close()
            raise Exception('Nao foi possivel obter o cliente inserido do banco de dados')
        # else:
        #     cursor.close()
        #     raise Exception('O cliente nao foi inserido')

        # insere pedido
        step = 'P.4 - Inserindo Pedido'
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'\tPedido {order.capa.pedido_oking_id}: Inserindo cabecalho pedido',
            LogType.INFO,
            'PEDIDO')
        trata_data = ''
        if db_config.db_type.lower() == 'firebird':
            trata_data = None
        cursor.execute(queries.get_insert_order_command(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type, [
                           order.capa.pedido_oking_id,
                           order.capa.pedido_venda_id,
                           order.capa.pedido_canal,
                           str(datetime.strptime(order.capa.data_pedido.replace('T', ' '),
                                                 '%Y-%m-%d %H:%M:%S.%f'))
                           if order.capa.data_pedido is not None else trata_data,
                           order.capa.status,
                           client_id,
                           order.capa.valor,
                           order.capa.valor_desconto,
                           order.capa.valor_frete,
                           order.capa.valor_adicional_forma_pagamento,
                           str(datetime.strptime(order.registro_status.aprovado_em.replace('T', ' '),
                                                 '%Y-%m-%d %H:%M:%S'))
                           if order.registro_status.aprovado_em is not None else trata_data,
                           order.pagamento['tipo_pagamento'],
                           order.pagamento['bandeira'],
                           order.pagamento['parcelas'],
                           order.pagamento['condicao_pagamento_erp'],
                           order.pagamento['opcao_pagamento'],
                           order.entrega.codigo_rastreio,
                           str(datetime.strptime(order.entrega.data_previsao_entrega.replace('T', ' '),
                                                 '%Y-%m-%d %H:%M:%S'))
                           if order.entrega.data_previsao_entrega is not None else trata_data,
                           order.entrega.transportadora,
                           order.entrega.modo_envio,
                           order.adiconal['canal_id'],
                           job_config.get('db_seller'),
                           order.usuario.codigo_representante,
                           order.adiconal['cnpj_intermediador'],
                           order.endereco_entrega['cep'],
                           order.endereco_entrega['tipo_logradouro'],
                           order.endereco_entrega['endereco'],
                           order.endereco_entrega['numero'],
                           order.endereco_entrega['complemento'],
                           order.endereco_entrega['bairro'],
                           order.endereco_entrega['cidade'],
                           order.endereco_entrega['estado'],
                           order.endereco_entrega['referencia_entrega'],
                           order.endereco_entrega['codigo_ibge'],
                       ]))
        step = 'P.5 - Populou os dados do Pedido'
        if cursor.rowcount > 0:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Pedido {order.capa.pedido_oking_id} inserido',
                LogType.INFO,
                'PEDIDO')
            step = 'P.6 - Antes de Executar a query'
            cursor.execute(queries.get_query_order(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [order.capa.pedido_oking_id]))
            step = 'P.7 - Executou a Query'
            (order_id,) = cursor.fetchone()
            if order_id is None or order_id <= 0:
                cursor.close()
                raise Exception('Nao foi possivel obter o pedido inserido no banco de dados')
        else:
            cursor.close()
            raise Exception('O cliente nao foi inserido')

        # insere itens
        step = 'insere itens'
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'\tPedido {order.capa.pedido_oking_id} com id semaforo {order_id}: Inserindo itens do pedido',
            LogType.INFO,
            'PEDIDO')
        for i in order.item:
            if src.print_payloads:
                print("=====================================Item Pedido=====================================")
                print(i)
            if db_config.db_type.lower() == 'firebird':
                cursor.execute(queries.get_order_item_firebird(), [order_id, i['codigo_sku'], i['codigo_erp']])
                if cursor.fetchone() is None:
                    cursor.execute(queries.get_insert_order_items_command(db_config.db_type),
                                   queries.get_command_parameter(db_config.db_type, [
                                       order_id,
                                       i['codigo_sku'],
                                       i['codigo_erp'],
                                       i['quantidade'],
                                       i['ean'],
                                       i['valor'],
                                       i['desconto'],
                                       i['valor_frete']
                                   ]))
            else:
                cursor.execute(queries.get_insert_order_items_command(db_config.db_type),
                               queries.get_command_parameter(db_config.db_type, [
                                   order_id,
                                   i['codigo_sku'],
                                   i['codigo_erp'],
                                   i['quantidade'],
                                   i['ean'],
                                   i['valor'],
                                   i['desconto'],
                                   i['valor_frete']
                               ]))

        cursor.close()
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Passo {step} - Erro durante a inserção dos dados do pedido {order.capa.pedido_oking_id}: {str(e)}',
            LogType.ERROR,
            str(order.capa.pedido_oking_id))
        conn.rollback()
        conn.close()
        return False


def call_order_procedures(job_config: dict, db_config: DatabaseConfig, order_id: int) -> (bool, str, str):
    client_erp_id = ''
    order_erp_id = ''
    success = True
    db = database.Connection(db_config)
    conn = db.get_conect()
    passo = "Passo 1 - Conectado no banco"
    try:
        cursor = conn.cursor()
        # LOG DEBUG -
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'P.1-PROC-Pedido [{order_id}] - Executando procedure de cliente',
            LogType.INFO,  # Voltar para - LogType.DEBUG
            f'PED_{order_id}_P.1-PROC')

        passo = "Passo 2 - Executando procedure de cliente"
        if db_config.is_sql_server():
            cursor.execute('SET NOCOUNT ON;'
                           'DECLARE @cliente_erp_output VARCHAR(50); '
                           'EXEC openk_semaforo.sp_processa_cliente @pedido = ?, '
                           '@cliente_erp = @cliente_erp_output OUTPUT; '
                           'SELECT @cliente_erp_output AS cliente_erp;', order_id)
            # Recuperar o valor do parâmetro de saída
            passo = "Passo 3 - Recuperando valor da procedure"
            row = cursor.fetchone()
            client_erp_id = row.cliente_erp
        elif db_config.is_oracle():
            client_out_value = cursor.var(str)
            cursor.callproc('OPENK_SEMAFORO.SP_PROCESSA_CLIENTE', [order_id, client_out_value])
            passo = "Passo 3 - Recuperando valor da procedure"
            client_erp_id = client_out_value.getvalue()
        elif db_config.is_mysql():
            args = (order_id, 0)
            resultargs = cursor.callproc('openk_semaforo.SP_PROCESSA_CLIENTE', order_id)
            passo = "Passo 3 - Recuperando valor da procedure"
            client_erp_id = resultargs[1]
        elif db_config.is_firebird():
            cursor.execute('EXECUTE PROCEDURE SP_PROCESSA_CLIENTE ?', [order_id])
            passo = "Passo 3 - Recuperando valor da procedure"
            (client_erp_id,) = cursor.fetchone()

        passo = "Passo 4 - Verificando retorno da procedure"
        if client_erp_id is not None:
            # LOG DEBUG -
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'P.2-PROC-Pedido [{order_id}] - Procedure de Cliente Executada com sucesso'
                f' -- Cliente ERP retornado: [{client_erp_id}]',
                LogType.INFO,  # Voltar para - LogType.DEBUG
                f'PED_{order_id}_P.2-PROC')

            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'P.3-PROC-Pedido [{order_id}] - Executando procedure de pedido',
                LogType.INFO,
                f'PED_{order_id}_P.3-PROC')
            passo = "Passo 5 - Executando procedure de Pedido"
            if db_config.is_sql_server():
                order_id = int(order_id)
                client_erp_id = int(client_erp_id)

                cursor.execute('SET NOCOUNT ON;'
                               'DECLARE @pedido_erp_output INT; '
                               'EXEC openk_semaforo.sp_processa_pedido @pedido = ?, @cliente_erp = ?, '
                               '@pedido_erp = @pedido_erp_output OUTPUT; '
                               'SELECT @pedido_erp_output AS pedido_erp;',
                               order_id, client_erp_id)
                passo = "Passo 6 - Recuperando valor da procedure"
                row = cursor.fetchone()
                order_erp_id = row[0]
            elif db_config.is_oracle():
                order_out_value = cursor.var(str)
                cursor.callproc('OPENK_SEMAFORO.SP_PROCESSA_PEDIDO', [order_id, int(client_erp_id), order_out_value])
                passo = "Passo 6 - Recuperando valor da procedure"
                order_erp_id = order_out_value.getvalue()
                passo = f"Passo 6 - Valor retornado da procedure {order_erp_id}"
            elif db_config.is_mysql():
                args = (order_id, int(client_erp_id), 0)
                resultargs = cursor.callproc('openk_semaforo.SP_PROCESSA_PEDIDO', args)
                passo = "Passo 6 - Recuperando valor da procedure"
                order_erp_id = resultargs[2]
            elif db_config.is_firebird():
                args = (order_id, int(client_erp_id))
                query = 'EXECUTE PROCEDURE SP_PROCESSA_PEDIDO (?, ?)'
                cursor.execute(query, args)
                passo = "Passo 6 - Recuperando valor da procedure"
                (order_erp_id,) = cursor.fetchone()

            if order_erp_id is not None:
                # LOG DEBUG -
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'P.4-PROC-Pedido [{order_id}] - Procedure de PEDIDO Executada com sucesso'
                    f' -- PEDIDO ERP retornado: {order_erp_id}',
                    LogType.INFO,  # Voltar para - LogType.DEBUG
                    f'PED_{order_id}_P.4-PROC')
            else:
                success = False
                passo = "Passo 7 - Executando o select do log integração"
                log_integracao = query_get_log_integracao2(db_config, str(order_id))

                passo = "Passo 8 - Pegando o valor do log integração"
                # LOG DEBUG -
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'P.5-PROC-Pedido [{order_id}] - Nao foi possivel obter o id do pedido do ERP (retorno da procedure) '
                    f' -- LOG retornado: {log_integracao}',
                    LogType.WARNING,
                    f'PED_{order_id}_P.5-PROC')
                raise Exception(f'Pedido [{order_id}]: Nao foi possivel obter o id do pedido do ERP (retorno da '
                                f'procedure) - Erro {log_integracao}')
        else:
            # LOG DEBUG -
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'P.6-PROC-Pedido [{order_id}] - Nao foi possivel obter o id do cliente do ERP (retorno da procedure)',
                LogType.WARNING,
                f'PED_{order_id}_P.6-PROC')

        cursor.close()
        if success:
            conn.commit()
        else:
            conn.rollback()
        conn.close()
        return success, client_erp_id, order_erp_id
    except Exception as e:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'\tPedido [{order_id}]:Erro no {passo}, '
            f'ERRO: {str(e)}', LogType.ERROR,
            str(order_id))
        conn.rollback()
        conn.close()
        return False, client_erp_id, order_erp_id


def check_non_integrated_order_existence(db_config: DatabaseConfig, order_id: int) -> bool:
    db = database.Connection(db_config)
    conn = db.get_conect()
    try:
        cursor = conn.cursor()
        cursor.execute(queries.get_query_non_integrated_order(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type, [order_id]))
        existent_order = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return existent_order is not None and existent_order > 0
    except Exception as e:
        conn.close()
        return False


# region - MPLACE
def process_order_queue_mplace(job_config: dict, status: str, db_config: DatabaseConfig,
                               status_to_insert: bool = False) -> None:
    try:
        print()
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'== [INICIO] Consultando fila de pedidos no status {status}',
            LogType.INFO,
            'PEDIDO')

        # LOG de Inicialização do Método - Para acompanhamento de execução
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Pedido - Iniciado[{status}]',
            LogType.EXEC,
            'PEDIDO')
        if job_config['executar_query_semaforo'] == 'S':
            executa_comando_sql(db_config, job_config)
        queue = api_Mplace.get_order_queue_mplace(src.client_data, status)

        qty = 0
        for q_order in queue:
            try:
                sleep(0.5)
                qty = qty + 1
                print()
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Iniciando processamento ({qty} de {len(queue)}) pedido {q_order.pedido_oking_id}',
                    LogType.INFO,
                    'PEDIDO')
                order = api_Mplace.get_order_mplace(src.client_data, q_order.pedido_oking_id)

                if order.partner_order_code is not None and order.partner_order_code != '':  # Pedido integrado anteriormente

                    if check_order_existence(db_config, order.order_id):
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'\tPedido [{order.order_id}]: Pedido ja integrado com o ERP, chamando '
                            f'procedure de atualizacao...',
                            LogType.INFO,
                            'PEDIDO')
                        if call_update_order_procedure(job_config, db_config, order.order_id, order.status_code):
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'\tPedido [{order.order_id}]: Pedido atualizado com sucesso',
                                LogType.INFO,
                                'PEDIDO')
                            set_codigo_erp_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                                 order_erp_id=order.partner_order_code, client_erp_id='')
                    else:
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'\tPedido [{order.order_id}]: NÃO existe no banco semaforo porem ja foi integrado '
                            f'previamente. Protocolando pedido...',
                            LogType.WARNING,
                            'PEDIDO')
                        protocol_non_existent_order(job_config, q_order)

                else:  # Pedido nao integrado anteriormente

                    if check_order_existence(db_config, order.order_id):  # Pedido existente no banco semaforo
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'\tPedido [{order.order_id}]: Pedido já existente no banco semáforo, '
                            f'porem nao integrado com erp. Chamando procedures',
                            LogType.INFO,
                            'PEDIDO')
                        sp_success, client_erp_id, order_erp_id = call_order_procedures(job_config, db_config,
                                                                                        q_order.pedido_oking_id)
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'\t === PROCEDURE EXECUTADA === ',
                            LogType.INFO,
                            'PEDIDO')

                        log = query_get_log_integracao2(db_config, q_order.pedido_oking_id)

                        if log:
                            api_Mplace.send_log_mplace(order.site_order_code, log)
                        if sp_success:
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'\tPedido [{order.order_id}]: Chamadas das procedures executadas com sucesso,'
                                f' protocolando pedido...',
                                LogType.INFO,
                                'PEDIDO')
                            set_codigo_erp_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                                 order_erp_id=order_erp_id, client_erp_id=client_erp_id)

                    elif status_to_insert:  # Pedido nao existe no semaforo e esta em status de internalizacao
                        #                     (pending e paid)

                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Inserindo novo pedido no banco semaforo',
                            LogType.INFO,
                            'PEDIDO')
                        inserted = insert_temp_order_mplace(job_config, order, db_config)
                        if inserted:
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'\tPedido [{order.order_id}]: Pedido inserido com sucesso, chamando procedures...',
                                LogType.INFO,
                                'PEDIDO')
                            sp_success, client_erp_id, order_erp_id = call_order_procedures(job_config, db_config,
                                                                                            q_order.pedido_oking_id)
                            log = query_get_log_integracao2(db_config, q_order.pedido_oking_id)
                            if log:
                                api_Mplace.send_log_mplace(order.site_order_code, log)

                            if sp_success:
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'\tPedido [{order.order_id}]: Chamadas das procedures executadas com sucesso,'
                                    f' protocolando pedido...',
                                    LogType.INFO,
                                    'PEDIDO')
                                set_codigo_erp_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                                     order_erp_id=order_erp_id, client_erp_id=client_erp_id)

                    else:  # Pedido nao existe no semaforo e nao esta em status de internalizacao (pending e paid)
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'\tPedido [{order.order_id}]: Pedido nao existente no banco semaforo e nao se '
                            f'encontra em status de internalizacao',
                            LogType.WARNING,
                            'PEDIDO')
                        api_Mplace.put_protocol_orders_mplace(q_order.protocolo)

            except Exception as e:
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'\tPedido [{q_order.pedido_oking_id}]: Erro no processamento do pedido: {str(e)}',
                    LogType.ERROR,
                    q_order.pedido_oking_id)
                # raise e
    except Exception as e:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Erro ao inicializar job de processamento de pedidos do status {status}: {str(e)}',
            LogType.ERROR,
            'PEDIDO')
        raise e


def insert_temp_order_mplace(job_config: dict, order: OrderMplace, db_config: DatabaseConfig) -> bool:
    step = ''
    db = database.Connection(db_config)
    conn = db.get_conect()
    try:
        step = 'conexao'
        cursor = conn.cursor()

        existent_client = None

        cursor.execute(queries.get_query_cliente_cpfcnpj(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type, [
                           order.customer.document_number.translate(str.maketrans('', '', string.punctuation))]))
        existent_client = cursor.fetchone()

        if existent_client is None:
            # insere cliente
            step = 'P.1 -Inserindo Novo Cliente'
            logger.info(f'')
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'\tPedido [{order.order_id}]: Inserindo cliente',
                LogType.INFO,
                'PEDIDO')
            cursor.execute(queries.get_insert_client_command(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [
                               order.customer.name,  # nome
                               order.customer.name,  # razao_social
                               order.customer.type,  # tipo_pessoa
                               order.customer.document_number,  # cpf_cnpj
                               order.customer.gender,  # sexo
                               order.customer.email,  # email
                               order.customer.identity_number,  # rg
                               '',  # orgao
                               str(datetime.strptime(order.customer.born_at.split('.')[0].replace('T', ' '),
                                                     # data_nascimento_constituicao
                                                     '%Y-%m-%d %H:%M:%S')) if order.customer.born_at is not None \
                                                                              and order.customer.born_at != '0001-01-01T00:00:00' else None,
                               order.customer.phones.office,  # telefone_residencial
                               order.customer.phones.mobile,  # telefone_celular
                               order.customer.state_registration,  # inscricao_estadual
                               '',  # inscricao_municipal
                               '',  # codigo_referencia_erp
                               '',  # codigo_representante
                               order.customer.billing.postal_code,  # end_principal_cep
                               '',  # END_PRINCIPAL_TIPOLOGRADOURO
                               order.customer.billing.address,  # end_principal_logradouro
                               order.customer.billing.number,  # end_principal_numero
                               order.customer.billing.complement,  # end_principal_complemento
                               order.customer.billing.neighborhood or " ",  # end_principal_bairro
                               order.customer.billing.city,  # end_principal_cidade
                               order.customer.billing.state,  # end_principal_estado
                               order.customer.billing.reference,  # end_principal_referencia_ent
                               order.customer.billing.city_ibge_code,  # end_principal_codigo_ibge
                               'M',  # Marketplace
                               'IN'  # direcao
                           ]))
            step = 'P.2 -Populou os dados do Cliente'
            if cursor.rowcount > 0:
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'\tPedido [{order.order_id}]: Cliente inserido/atualizado',
                    LogType.INFO,
                    'PEDIDO')
                step = 'P.3 -Consultando o CLiente pelo CPF/CNPJ'
                cursor.execute(queries.get_query_cliente_cpfcnpj(db_config.db_type),
                               queries.get_command_parameter(db_config.db_type, [
                                   order.customer.document_number.translate(
                                       str.maketrans('', '', string.punctuation))]))
                step = 'P.4 -Query executada'
                (client_id,) = cursor.fetchone()

                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'\tPedido [{order.order_id}]: Cliente Encontrado:{client_id}',
                    LogType.INFO,
                    'PEDIDO')

                if client_id is None or client_id <= 0:
                    cursor.close()
                    raise Exception('Nao foi possivel obter o cliente inserido do banco de dados')
            else:
                cursor.close()
                raise Exception('O cliente nao foi inserido')
        else:
            # update no cliente existente
            client_id = existent_client[0]
            step = 'P.5 -Atualizando Cliente existente'
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'\tPedido [{order.order_id}]: Atualizando cliente existente',
                LogType.INFO,
                'PEDIDO')
            step = 'P.6 -Antes de excutar a Query'
            cursor.execute(queries.get_update_client_sql(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [
                               order.customer.name,  # 1. nome
                               order.customer.name,  # 2. razao_social
                               order.customer.gender,  # 3. sexo
                               order.customer.email,  # 4. email
                               order.customer.identity_number,  # 5. rg
                               '',  # 6. orgao
                               str(datetime.strptime(
                                   order.customer.born_at.split('.')[0].replace('T', ' '), '%Y-%m-%d %H:%M:%S'))
                               if order.customer.born_at is not None and order.customer.born_at != '0001-01-01T00:00:00'
                               else None, # 7. data_nascimento_constituicao
                               order.customer.phones.office,  # 8. telefone_residencial
                               order.customer.phones.mobile,  # 9. telefone_celular
                               order.customer.state_registration,  # 10. inscricao_estadual
                               '',  # 11. inscricao_municipal
                               '',  # 12. codigo_representante
                               order.customer.billing.postal_code,  # 13. end_principal_cep
                               '',  # 14. END_PRINCIPAL_TIPOLOGRADOURO
                               order.customer.billing.address,  # 15. end_principal_logradouro
                               order.customer.billing.number,  # 16. end_principal_numero
                               order.customer.billing.complement,  # 17. end_principal_complemento
                               order.customer.billing.neighborhood or " ",  # 18. end_principal_bairro
                               order.customer.billing.city,  # 19. end_principal_cidade
                               order.customer.billing.state,  # 20. end_principal_estado
                               order.customer.billing.reference,  # 21. end_principal_referencia_ent
                               order.customer.billing.city_ibge_code or " ",  # 11. end_principal_codigo_ibge
                               client_id # ID -> SEMAFORO.CLIENTE
                           ]))
            step = 'P.6 -Query executada'
            client_id = existent_client[0]

        # insere pedido
        step = 'P.7 -Antes de Executar a Query de Pedido'
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'\tPedido [{order.order_id}]: Inserindo cabecalho pedido',
            LogType.INFO,
            'PEDIDO')

        cursor.execute(queries.get_insert_b2b_order_command(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type, [
                           order.order_id,  # pedido_oking_id
                           order.order_id,  # pedido_venda_id
                           order.site_order_code,  # pedido_canal
                           '',  # numero_pedido_externo
                           str(datetime.strptime(
                               order.order_date.split('.')[0].replace('T', ' '), '%Y-%m-%d %H:%M:%S'))
                           if order.order_date is not None and order.order_date != '0001-01-01T00:00:00'
                           else None,# data_pedido
                           order.status_code,  # status
                           client_id,  # client_id
                           order.total_amount,  # valor
                           order.discount_value,  # valor_desconto
                           order.freight_value,  # valor_frete
                           0,  # valor_adicional_forma_pagt
                           str(datetime.strptime(
                               order.status_record.approved_at.split('.')[0].replace('T', ' '), '%Y-%m-%d %H:%M:%S'))
                           if order.status_record.approved_at is not None
                           and order.status_record.approved_at != '0001-01-01T00:00:00'
                           else None,  # data_pagamento
                           order.payment.payment_options.replace("'", ''),  # tipo_pagamento
                           order.payment.flag,  # bandeira
                           order.payment.plot_amount,  # parcelas
                           '',  # condicao_pagamento_erp
                           '',  # opcao_pagamento_erp
                           order.tracking_code or '',  # codigo_rastreio
                           str(datetime.strptime(order.delivery_forecast.split('.')[0].replace('T', ' '),
                                                 '%Y-%m-%d %H:%M:%S'))
                           if order.delivery_forecast is not None and order.delivery_forecast != '0001-01-01T00:00:00'
                           else None, # data_previsao_entrega
                           order.tracking.carrier,  # transportadora
                           '',  # opcao_forma_entrega
                           '',  # modo_envio
                           0,  # canal_id
                           job_config.get('db_seller'),  # loja_id
                           '',  # codigo_representante
                           order.document_intermediator or '',  # cnpj_intermediador
                           '',  # identificador_vendedor
                           order.delivery_address.postal_code,  # end_entrega_cep
                           '',  # end_entrega_tipo_logradouro
                           order.delivery_address.address,  # end_entrega_logradouro
                           order.delivery_address.number,  # end_entrega_numero
                           order.delivery_address.complement,  # end_entrega_complemento
                           order.delivery_address.neighborhood,  # end_entrega_bairro
                           order.delivery_address.city,  # end_entrega_cidade
                           order.delivery_address.state,  # end_entrega_estado
                           order.delivery_address.reference,  # END_ENTREGA_REFERENCIA_ENT
                           order.delivery_address.city_ibge_code or '',  # end_entrega_codigo_ibge
                           '',  # descritor_pre_definido_2
                           '',  # descritor_pre_definido_3
                           '',  # descritor_pre_definido_4
                           '',  # descritor_pre_definido_5
                           ''  # descritor_pre_definido_6
                       ]))

        if cursor.rowcount > 0:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'\tPedido [{order.order_id}]: Inserido com sucesso',
                LogType.INFO,
                'PEDIDO')
            cursor.execute(queries.get_query_order(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [order.order_id]))
            (order_id,) = cursor.fetchone()
            if order_id is None or order_id <= 0:
                cursor.close()
                raise Exception('Nao foi possivel obter o pedido inserido no banco de dados')
        else:
            cursor.close()
            raise Exception('O cliente nao foi inserido')

        # insere itens
        step = 'P.8 -Itens Pedido Antes Executar a Query'
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'\tPedido [{order.order_id}]: Inserindo ITENS do pedido',
            LogType.INFO,
            'PEDIDO')
        for item in order.itempedido:
            cursor.execute(queries.get_insert_b2b_order_items_command(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [
                               order_id,  # pedido_id,
                               item.sku_seller_id,  # sku
                               item.sku_partner_id,  # codigo_erp
                               item.quantity,  # quantidade
                               '',  # ean
                               item.sale_price,  # valor
                               item.discount,  # valor_desconto
                               item.freight_value,  # valor_frete
                               # '',  # codigo_filial_erp
                               '',  # codigo_filial_expedicao_erp
                               '',  # CODIGO_FILIAL_FATURAMENT_ERP
                               '',  # cnpj_filial_venda
                               0,  # valor_taxa_servico
                               0, 0, 0, 0, 0, 0, 0  # demais campos relacionados a imposto
                           ]))

        cursor.close()
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Passo {step} - Erro durante a inserção dos dados do pedido {order.order_id}: {str(e)}',
            LogType.ERROR,
            str(order.order_id))
        conn.rollback()
        conn.close()
        return False


# endregion

# region Okvendas

def process_order_queue_okvendas(job_config: dict, status: str, db_config: DatabaseConfig, status_to_insert: bool = False) -> None:
    try:
        # Mapeamento de status para nomes de job
        status_job_mapping = {
            'CANCELADO': 'CANCELA_PEDIDO_JOB',
            'PEDIDO': 'INTERNALIZA_PEDIDOS_JOB',
            'PEDIDO_PAGO': 'INTERNALIZA_PEDIDOS_PAGOS_JOB'
        }

        # LOG de Inicialização do Método - Para acompanhamento de execução
        job_type = status_job_mapping.get(status, 'INTERNALIZA_PEDIDOS_JOB')  # Default caso o status não exista

        # LOG de Inicialização do Método - Para acompanhamento de execução
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), job_config.get('enviar_logs_debug'), f'OKVENDAS - Pedido - Iniciado[{status}]', LogType.EXEC, f'PEDIDO_FILA_{status}')

        # Executa Query de Semaforo se necessário
        if job_config['executar_query_semaforo'] == 'S':
            executa_comando_sql(db_config, job_config)

        # Consulta Fila de acordo com o Status    
        queue = api_okVendas.get_order_queue_okvendas(status)
        qty = 0
        for q_order in queue:
            try:
                sleep(0.5)
                qty = qty + 1
                print()
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Pedido [{q_order.pedido_oking_id}] - FILA [{job_type}] - Processando ({qty} de {len(queue)}) ',
                    LogType.INFO,
                    f'PEDIDO_{q_order.pedido_oking_id}')
                order = api_okVendas.get_order_okvendas(q_order.pedido_oking_id)
                # Pedido integrado anteriormente
                if q_order.numero_pedido_externo is not None and q_order.numero_pedido_externo != '':

                    if check_order_existence(db_config, order.id):
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'P.1-Pedido [{order.id}] - Pedido ja integrado com o ERP, chamando '
                            f'procedure de atualizacao...',
                            LogType.INFO,
                            f'PEDIDO_{order.id}_P.1')
                        if query_update_status_observacao(job_config, db_config, order):
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'P.2-Pedido [{order.id}] - Log integracao do pedido {order.id} atualizado',
                                LogType.INFO,
                                f'PEDIDO_{order.id}_P.2')
                        if call_update_order_procedure(job_config, db_config, order.id, order.status):
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'P.3-Pedido [{order.id}] - Pedido atualizado com sucesso',
                                LogType.INFO,
                                f'PEDIDO_{order.id}_P.3')
                            set_codigo_erp_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                                 order_erp_id=q_order.numero_pedido_externo, client_erp_id='')
                    else:
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'P.4-Pedido [{order.id}] - :( NÃO existe :( no banco semaforo porem ja foi integrado '
                            f'previamente. Protocolando pedido...',
                            LogType.WARNING,
                            f'PEDIDO_{order.id}_P.4')
                        protocol_non_existent_order(job_config, q_order)

                else:  # Pedido nao integrado anteriormente

                    if check_order_existence(db_config, order.id):  # Pedido existente no banco semaforo
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'P.5-Pedido [{order.id}] - já EXISTE no banco semáforo, '
                            f'porem nao integrado com erp. Chamando >> PROCEDURES <<',
                            LogType.INFO,
                            f'PEDIDO_{order.id}_P.5')
                        
                        # https://app.clickup.com/t/86dxfk14y 
                        # Antes de Chamar as Procedures, atualiza a coluna [STATUS] da tabela [SEMAFORO.PEDIDO] 
                        #  * STATUS  => Recebe o Status que está na API do OKVENDAS
                        if query_update_status_pedido(job_config, db_config, order):
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'P.5.1-Pedido [{order.id}] - Atualiza [STATUS: {order.status}] do Pedido na Semaforo!',
                                LogType.INFO,
                                f'PEDIDO_{order.id}_P.5.1')
                        # ======================================================

                        # Após Atualizar o Status da tabela [SEMAFORO.PEDIDO] - segue fluxo normal.
                        sp_success, client_erp_id, order_erp_id = call_order_procedures(job_config, db_config,
                                                                                        q_order.pedido_oking_id)
                        log = query_get_log_integracao2(db_config, q_order.pedido_oking_id)
                        if log:
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'P.6-Pedido [{order.id}] - Log de integração: {log}',
                                LogType.ERROR,
                                f'PEDIDO_{order.id}_P.6')
                        if sp_success:
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'P.7-Pedido [{order.id}] - PROCEDURES executadas com sucesso!! :)'
                                f' protocolando pedido...',
                                LogType.INFO,
                                f'PEDIDO_{order.id}_P.7')
                            set_codigo_erp_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                                 order_erp_id=order_erp_id, client_erp_id=client_erp_id)

                    # Pedido nao existe no semaforo e esta em status de internalizacao (pending e paid)
                    elif status_to_insert:
                        # Se o status do pedido for cancelado, e ainda nao existir no semaforo, ira protocolar
                        if 'cancelado' in order.status.lower():
                            logger.info(f'=== Passo 1 - OKVENDAS - Pedido com status cancelado')
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'P.8-Pedido [{order.id}] - Pedido NÃO existe no semaforo, e está com status de '
                                f'[CANCELADO], Removendo pedido da fila - protocolo {q_order.protocolo}'
                                f'CPF:{(order.usuario.cpf or "")}, CNPJ:{(order.usuario.cnpj or "")}',
                                LogType.INFO,
                                f'PEDIDO_{order.id}_P.8')
                            protocoled_order = api_okVendas.put_protocol_order_okvendas([q_order.protocolo])
                            if protocoled_order:
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'P.9-Pedido [{order.id}] - Pedido protocolado via API OkVendas',
                                    LogType.INFO,
                                    f'PEDIDO_{order.id}_P.9')
                            else:
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'P.10-Pedido [{order.id}] - Falha ao protocolar pedido {order.id} via API OkVendas',
                                    LogType.WARNING,
                                    f'PEDIDO_{order.id}_P.10')

                            if query_update_status_observacao(job_config, db_config, order):
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'P.11-Pedido [{order.id}] - Log integracao atualizado',
                                    LogType.INFO,
                                    f'PEDIDO_{order.id}_P.11')

                        # NOVO PEDIDO - Inserir Primeiro na SEMAFORO
                        else:
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'P.12-Pedido [{order.id}] - Inserindo NOVO PEDIDO no banco semaforo',
                                LogType.INFO,
                                f'PEDIDO_{order.id}_P.12')
                            inserted = insert_temp_order_okvendas(job_config, order, db_config, job_type)
                            if inserted:
                                # LOG DEBUG -
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'P.13-Pedido [{order.id}]'
                                    f' -- SEMAFORO - PREENCHIDO - Chama PROCEDURE de Internalização',
                                    LogType.INFO,  # Voltar para - LogType.DEBUG
                                    f'PEDIDO_{order.id}_P.13')
                                sp_success, client_erp_id, order_erp_id = call_order_procedures(job_config, db_config,
                                                                                                q_order.pedido_oking_id)
                                log = query_get_log_integracao2(db_config, q_order.pedido_oking_id)
                                if log:
                                    # LOG DEBUG -
                                    send_log(
                                        job_config.get('job_name'),
                                        job_config.get('enviar_logs'),
                                        job_config.get('enviar_logs_debug'),
                                        f'P.14-Pedido [{order.id}]'
                                        f' -- Log de integração do pedido - {q_order.pedido_oking_id}: {log}',
                                        LogType.INFO,  # Voltar para - LogType.DEBUG
                                        f'PEDIDO_{order.id}_P.14')
                                if sp_success:
                                    # LOG DEBUG -
                                    send_log(
                                        job_config.get('job_name'),
                                        job_config.get('enviar_logs'),
                                        job_config.get('enviar_logs_debug'),
                                        f'P.15-Pedido [{order.id}] - PROCESSADO COM SUCESSO! (procedures executadas)'
                                        f' -- Protocolando pedido...',
                                        LogType.INFO,  # Voltar para - LogType.DEBUG
                                        f'PEDIDO_{order.id}_P.15')
                                    set_codigo_erp_order(job_config, db_config=db_config, order=order,
                                                         queue_order=q_order, order_erp_id=order_erp_id,
                                                         client_erp_id=client_erp_id)

                    else:  # Pedido nao existe no semaforo e nao esta em status de internalizacao (pending e paid)
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'P.16-Pedido [{order.id}] - Pedido nao existente no banco semaforo e nao se '
                            f'encontra em status de internalizacao',
                            LogType.WARNING,
                            f'PEDIDO_{order.id}_P.16')
                        api_okVendas.put_protocol_order_okvendas([q_order.protocolo])

            except Exception as e:
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'\tOKVENDAS - Pedido [{q_order.pedido_oking_id}]: Erro no processamento do pedido: {str(e)}',
                    LogType.ERROR,
                    q_order.pedido_oking_id)
                continue  # Opcional - o loop já continuaria sem isso, mas deixa explícito
    except Exception as e:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'OKVENDAS - Erro ao inicializar job de processamento de pedidos do status {status}: {str(e)}',
            LogType.ERROR,
            'PED_ERR_GEN')
        raise e


# endregion
def query_invoices(job_config: dict, db_config: DatabaseConfig, pedidoId: str = '') -> List[Invoice]:
    """
    Consulta as notas fiscais a serem enviadas na api
    Args:
        job_config: Configuração do job
        db_config: Configuracao do banco de dados
        pedidoId: Id do pedido da nota fiscal

    Returns:
        Lista de notas fiscais para enviar
    """
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    invoices = []
    try:
        if db_config.is_oracle():
            conn.outputtypehandler = database.output_type_handler

        newsql = db_config.sql.lower().replace(';', '')

        if src.client_data['operacao'].lower().__contains__('mplace') or \
                src.client_data['operacao'].lower().__contains__('okvendas'):
            newsql = newsql.replace("@pedido_id", f'{pedidoId}').replace('#v', ',')
        logger.info("LOG AUXILIAR - executando a query")
        if src.print_payloads:
            print(newsql)
        cursor.execute(newsql)
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        logger.info(f"LOG AUXILIAR - retornou {len(results)} registros")
        cursor.close()
        conn.close()
        if len(results) > 0:
            if src.client_data['operacao'].lower().__contains__('okvendas'):
                invoices = [InvoiceOkvendas(**p) for p in results]
            elif src.client_data['operacao'].lower().__contains__('mplace'):
                invoices = [InvoiceMplace(**p) for p in results]
            else:
                logger.info(f"LOG AUXILIAR - colocar o resultados no objeto Invoice")
                invoices = [Invoice(**p) for p in results]

    except Exception as ex:
        logger.error(f' ')
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Erro ao consultar notas fiscais no banco: {str(ex)}',
            LogType.ERROR,
            'PEDIDO')
        raise ex

    logger.info(f"LOG AUXILIAR - retornando os Invoices e saindo do método")
    return invoices


def set_status_processing(job_config: dict, queue_order: Queue) -> None:
    try:
        protocoled_order = api_Mplace.post_status_processing_mplace(queue_order.pedido_oking_id)
        if protocoled_order:
            logger.info(current_job + f' | Pedido {queue_order.pedido_oking_id} protocolado via api OkVendas')
        else:
            logger.warning(
                current_job + f' | Falha ao protocolar pedido {queue_order.pedido_oking_id} via api OkVendas')
    except Exception as ex:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Erro ao protocolar pedido {queue_order.pedido_oking_id}: {str(ex)}',
            LogType.ERROR,
            queue_order.pedido_oking_id)


def safe_set_isolation(conn, db_type: str):
    """Configura o nível de isolamento de forma segura para qualquer banco"""
    db_type = db_type.lower()
    try:
        if db_type == 'oracle':
            try:
                cursor = conn.cursor()
                cursor.execute("ALTER SESSION SET ISOLATION_LEVEL = READ COMMITTED ")
                cursor.close()
            except Exception as oracle_ex:
                logger.warning(f"Oracle: usando isolamento padrão (ERRO: {oracle_ex})")

        elif db_type == 'sqlserver':
            try:
                cursor = conn.cursor()
                cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
                cursor.close()
            except Exception as sqlsrv_ex:
                logger.warning(f"SQL Server: usando isolamento padrão (ERRO: {sqlsrv_ex})")

        elif hasattr(conn, 'set_session'):  # Para MySQL, PostgreSQL, etc.
            try:
                conn.set_session(isolation_level='REPEATABLE READ')
            except Exception as session_ex:
                logger.warning(f"set_session falhou: {session_ex}")
                conn.set_session(isolation_level='READ COMMITTED')

    except Exception as e:
        logger.error(f"ERRO GRAVE ao configurar isolamento: {str(e)}")
        # Não levanta exceção para não interromper o fluxo


def insert_temp_order_okvendas(job_config: dict, order: OrderOkvendas, db_config: DatabaseConfig,
                               job_type: str) -> bool:
    step = ''

    try:
        step = 'conexao'
        db = database.Connection(db_config)
        conn = db.get_conect()
        safe_set_isolation(conn, db_config.db_type)  # <--- Aqui!

        step = 'with conn.cursor()'
        with conn.cursor() as cursor:
            client_cpf_cnpj = (order.usuario.cpf or '') + (order.usuario.cnpj or '')
            tipo_pessoa = 'F' if order.usuario.cpf else 'J'
            client_cpf_cnpj = client_cpf_cnpj.translate(str.maketrans('', '', string.punctuation))
            if src.print_payloads:
                print(f'\t | client_cpf_cnpj:{client_cpf_cnpj}, tipo_pessoa:{tipo_pessoa}')

            # LOG DEBUG -
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'P.1-TMP-Pedido [{order.id}] - CPF/CNPJ [{client_cpf_cnpj}], '                
                f'codigo_referencia: {(order.usuario.codigo_referencia or "")}',
                LogType.INFO,  # Voltar para - LogType.DEBUG
                f'PED_{order.id}_P.1-TMP')

            # Consulta com lock
            cursor.execute(queries.get_query_cliente_cpfcnpj(db_config.db_type, for_update=True),
                           queries.get_command_parameter(db_config.db_type, [client_cpf_cnpj]))

            existent_client = cursor.fetchone()

            if existent_client is None:
                if src.print_payloads:
                    print('============================================')
                    print('=== Cliente não encontrado, vai INSERIR! ===')
                    print('============================================')

                # insere cliente
                step = 'P.1 -Inserindo Novo Cliente'
                logger.info(f'')
                # LOG DEBUG -
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'P.2-TMP-Pedido [{order.id}] - CPF/CNPJ [{client_cpf_cnpj}], '
                    f' -- Novo Cliente >> Inserindo na SEMAFORO.CLIENTE',
                    LogType.INFO,  # Voltar para - LogType.DEBUG
                    f'PED_{order.id}_P.2-TMP')

                cursor.execute(queries.get_insert_client_command(db_config.db_type),
                               queries.get_command_parameter(db_config.db_type, [
                                   order.usuario.nome,  # nome
                                   order.usuario.razao_social,  # razao_social
                                   tipo_pessoa,  # tipo_pessoa
                                   client_cpf_cnpj,  # cpf_cnpj
                                   order.usuario.sexo,  # sexo
                                   order.usuario.email,  # email
                                   order.usuario.rg,  # rg
                                   order.usuario.orgao,  # orgao
                                   str(datetime.strptime(
                                       order.usuario.data_nascimento.replace('T', ' '), '%Y-%m-%d %H:%M:%S'))
                                   if order.usuario.data_nascimento is not None
                                   and order.usuario.data_nascimento != '0001-01-01T00:00:00'
                                   else None,  # data_nascimento_constituicao
                                   order.usuario.TelefoneResidencial,  # telefone_residencial
                                   order.usuario.TelefoneCelular,  # telefone_celular
                                   order.usuario.RegistroEstadual,  # inscricao_estadual
                                   '',  # inscricao_municipal
                                   order.usuario.codigo_referencia,  # codigo_referencia_erp
                                   order.representante,  # codigo_representante
                                   order.usuario.Endereco.cep,  # end_principal_cep
                                   order.usuario.Endereco.tipo_logradouro,  # END_PRINCIPAL_TIPOLOGRADOURO
                                   order.usuario.Endereco.logradouro,  # end_principal_logradouro
                                   order.usuario.Endereco.numero,  # end_principal_numero
                                   order.usuario.Endereco.complemento,  # end_principal_complemento
                                   order.usuario.Endereco.bairro or " ",  # end_principal_bairro
                                   order.usuario.Endereco.cidade,  # end_principal_cidade
                                   order.usuario.Endereco.estado,  # end_principal_estado
                                   order.usuario.Endereco.referencia,  # end_principal_referencia_ent
                                   order.usuario.Endereco.codigo_ibge,  # end_principal_codigo_ibge
                                   'IN',  # direcao
                                   order.usuario.origem_cadastro
                               ]))
                step = 'P.2 -Populou os dados do Cliente'
                if cursor.rowcount > 0:
                    # LOG DEBUG -
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f'P.3-TMP-Pedido [{order.id}] - CPF/CNPJ [{client_cpf_cnpj}], '
                        f' -- >> INSERIU << Consultando na SEMAFORO.CLIENTE pelo CPF/CNPJ, para obter os dados.',
                        LogType.INFO,  # Voltar para - LogType.DEBUG
                        f'PED_{order.id}_P.3-TMP')

                    step = 'P.3 -Consultando o CLiente pelo CPF/CNPJ'
                    cursor.execute(queries.get_query_cliente_cpfcnpj(db_config.db_type),
                                   queries.get_command_parameter(db_config.db_type, [client_cpf_cnpj]))
                    step = 'P.4 -Query executada'
                    (client_id,) = cursor.fetchone()

                    if client_id is None or client_id <= 0:
                        # cursor.close()
                        # LOG DEBUG -
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'P.4-TMP-Pedido [{order.id}] - CPF/CNPJ [{client_cpf_cnpj}], '
                            f' -- Executou o Insert mas o SELECT pelo CPF/CNPJ não encontrou o cliente',
                            LogType.INFO,  # Voltar para - LogType.DEBUG
                            f'PED_{order.id}_P.4-TMP')
                        raise Exception('Nao foi possivel obter o cliente inserido do banco de dados')

                    # LOG DEBUG -
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f'P.5-TMP-Pedido [{order.id}] - CPF/CNPJ [{client_cpf_cnpj}], '
                        f' -- Cliente Encontrado - ID da SEMAFORO.CLIENTE: {client_id} ',
                        LogType.INFO,  # Voltar para - LogType.DEBUG
                        f'PED_{order.id}_P.5-TMP')
                else:
                    # cursor.close()
                    # LOG DEBUG -
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f'P.6-TMP-Pedido [{order.id}] - CPF/CNPJ [{client_cpf_cnpj}], '
                        f' -- Não conseguiu executar o comando de [INSERT] na SEMAFORO.CLIENTE',
                        LogType.INFO,  # Voltar para - LogType.DEBUG
                        f'PED_{order.id}_P.6-TMP')
                    raise Exception('O cliente nao foi inserido')
            else:
                print('==============================================')
                print('=== EXISTE! Cliente já existe, atualizando ===')
                print('==============================================')
                # =============================================
                # Verificação de consistência - INICIO
                client_id = existent_client[0]

                # LOG DEBUG -
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'P.7-TMP-Pedido [{order.id}] - CPF/CNPJ [{client_cpf_cnpj}], '
                    f' -- 1. [JÁ EXISTE] Cliente Encontrado - ID da SEMAFORO.CLIENTE: {client_id} '
                    f' -- 2. Vai Consultar utilizando o ID encontrado para Validar o CPF/CNPJ.',
                    LogType.INFO,  # Voltar para - LogType.DEBUG
                    f'PED_{order.id}_P.7-TMP')

                cursor.execute(queries.get_query_cpfcnpj_cliente_ByID(db_config.db_type),
                               queries.get_command_parameter(db_config.db_type, [client_id]))
                db_cpf_cnpj = cursor.fetchone()[0]
                if db_cpf_cnpj != client_cpf_cnpj:
                    # LOG DEBUG -
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f'P.8-TMP-Pedido [{order.id}] - CPF/CNPJ [{client_cpf_cnpj}], '
                        f' -- 1. [Inconsistência] Cliente ID da SEMAFORO.CLIENTE: {client_id} '
                        f' possui CPF/CNPJ {db_cpf_cnpj} mas era esperado {client_cpf_cnpj}.',
                        LogType.ERROR,  # Voltar para - LogType.DEBUG
                        f'PED_{order.id}_P.8-TMP')
                    raise Exception(
                        f"Inconsistência: cliente ID {client_id} possui CPF/CNPJ {db_cpf_cnpj} "
                        f"mas era esperado {client_cpf_cnpj}")
                # Verificação de consistência - FIM
                # =============================================

                # update no cliente existente
                step = 'P.5 -Atualizando Cliente existente'
                # LOG DEBUG -
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'P.9-TMP-Pedido [{order.id}] - CPF/CNPJ [{client_cpf_cnpj}], '
                    f' -- Vai atualizar os dados do Cliente Existente na SEMAFORO.CLIENTE: {client_id} ',
                    LogType.INFO,  # Voltar para - LogType.DEBUG
                    f'PED_{order.id}_P.9-TMP')
                step = 'P.6 -Antes de executar a Query'

                # =============================================================================================
                # == TRECHO SOMENTE PARA LOG
                sql = queries.get_update_client_sql(db_config.db_type)
                params = queries.get_command_parameter(db_config.db_type, [
                                   order.usuario.nome,  # 1. nome
                                   order.usuario.razao_social,  # 2. razao_social
                                   order.usuario.sexo,  # 3. sexo
                                   order.usuario.email,  # 4. email
                                   order.usuario.rg,  # 5. rg
                                   order.usuario.orgao,  # 6. orgao
                                   str(datetime.strptime(order.usuario.data_nascimento.replace('T', ' '),
                                                         '%Y-%m-%d %H:%M:%S'))
                                   if order.usuario.data_nascimento is not None
                                   and order.usuario.data_nascimento != '0001-01-01T00:00:00'
                                   else None,  # 7. data_nascimento_constituicao
                                   order.usuario.TelefoneResidencial,  # 8. telefone_residencial
                                   order.usuario.TelefoneCelular,  # 9. telefone_celular
                                   order.usuario.RegistroEstadual,  # 10. inscricao_estadual
                                   '',  # 11. inscricao_municipal
                                   order.representante,  # 12. codigo_representante
                                   order.usuario.Endereco.cep,  # 13. end_principal_cep
                                   order.usuario.Endereco.tipo_logradouro,  # 14. END_PRINCIPAL_TIPOLOGRADOURO
                                   order.usuario.Endereco.logradouro,  # 15. end_principal_logradouro
                                   order.usuario.Endereco.numero,  # 16. end_principal_numero
                                   order.usuario.Endereco.complemento,  # 17. end_principal_complemento
                                   order.usuario.Endereco.bairro or " ",  # 18. end_principal_bairro
                                   order.usuario.Endereco.cidade,  # 19. end_principal_cidade
                                   order.usuario.Endereco.estado,  # 20. end_principal_estado
                                   order.usuario.Endereco.referencia,  # 21. end_principal_referencia_ent
                                   order.usuario.Endereco.codigo_ibge,  # 22. end_principal_codigo_ibge
                                   client_id  # 23. ID -> da tabela SEMAFORO.CLIENTE
                               ])

                sql_log = log_sql_command_oracle(sql, params)

                logger.info(f"===> SQL a ser executado:\n{sql_log}")
                # == FIM TRECHO PARA LOG
                # =============================================================================================

                # A query na data [28/05/2025] estava fazendo update utilizando o campo order.usuario.codigo_referencia
                # para realizar o Update porém se o Cliente é Novo Esse campo estará NULL, mas como já foi feito a
                # consulta utilizando [CPF/CNPJ], para retornar o ID, então iremos alterar para utilizar o ID
                # ==== CAMPOS REMOVIDOS DO UPDATE
                # ====  1. TIPO PESSOA
                # ====  2. CPF/CNPJ
                # ====  3. CODIGO_REFERENCIA
                cursor.execute(queries.get_update_client_sql(db_config.db_type),
                               queries.get_command_parameter(db_config.db_type, [
                                   order.usuario.nome,  # 1. nome
                                   order.usuario.razao_social,  # 2. razao_social
                                   order.usuario.sexo,  # 3. sexo
                                   order.usuario.email,  # 4. email
                                   order.usuario.rg,  # 5. rg
                                   order.usuario.orgao,  # 6. orgao
                                   str(datetime.strptime(order.usuario.data_nascimento.replace('T', ' '),
                                                         '%Y-%m-%d %H:%M:%S'))
                                   if order.usuario.data_nascimento is not None
                                   and order.usuario.data_nascimento != '0001-01-01T00:00:00'
                                   else None,  # 7. data_nascimento_constituicao
                                   order.usuario.TelefoneResidencial,  # 8. telefone_residencial
                                   order.usuario.TelefoneCelular,  # 9. telefone_celular
                                   order.usuario.RegistroEstadual,  # 10. inscricao_estadual
                                   '',  # 11. inscricao_municipal
                                   order.representante,  # 12. codigo_representante
                                   order.usuario.Endereco.cep,  # 13. end_principal_cep
                                   order.usuario.Endereco.tipo_logradouro,  # 14. END_PRINCIPAL_TIPOLOGRADOURO
                                   order.usuario.Endereco.logradouro,  # 15. end_principal_logradouro
                                   order.usuario.Endereco.numero,  # 16. end_principal_numero
                                   order.usuario.Endereco.complemento,  # 17. end_principal_complemento
                                   order.usuario.Endereco.bairro or " ",  # 18. end_principal_bairro
                                   order.usuario.Endereco.cidade,  # 19. end_principal_cidade
                                   order.usuario.Endereco.estado,  # 20. end_principal_estado
                                   order.usuario.Endereco.referencia,  # 21. end_principal_referencia_ent
                                   order.usuario.Endereco.codigo_ibge,  # 22. end_principal_codigo_ibge
                                   client_id  # 23. ID -> da tabela SEMAFORO.CLIENTE
                               ]))
                step = 'P.7 -Query executada'
                client_id = existent_client[0]

            # insere pedido
            step = 'P.8 -Antes de Executar a Query de Pedido'
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'P.10-TMP-Pedido [{order.id}] - CPF/CNPJ [{client_cpf_cnpj}], Inserindo SEMAFORO.PEDIDO',
                LogType.INFO,
                f'PED_{order.id}_P.10-TMP')

            cursor.execute(queries.get_insert_okvendas_order_command(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [
                               order.id,  # pedido_oking_id
                               order.pedido_venda_id,  # pedido_venda_id
                               order.pagamento[0].codigo_pedido_canal,  # pedido_canal
                               '',  # numero_pedido_externo
                               str(datetime.strptime(order.data_pedido.replace('T', ' '), '%Y-%m-%d %H:%M:%S'))
                               if order.data_pedido is not None
                               and order.data_pedido != '0001-01-01T00:00:00' else None,  # data_pedido
                               order.status,  # status
                               client_id,  # client_id
                               order.valor_total,  # valor
                               order.valor_desconto,  # valor_desconto
                               order.valor_frete,  # valor_frete
                               order.valor_forma_pagamento,  # valor_adicional_forma_pagt
                               str(datetime.strptime(order.pagamento[0].data_movimento.replace('T', ' '),
                                                     # data_pagamento
                                                     '%Y-%m-%d %H:%M:%S'))
                               if order.pagamento[0].data_movimento is not None
                               and order.pagamento[0].data_movimento != '0001-01-01T00:00:00' else None,
                               order.pagamento[0].opcao_pagamento.replace("'", ''),  # tipo_pagamento
                               order.pagamento[0].bandeira,  # bandeira
                               order.pagamento[0].parcelas,  # parcelas
                               order.pagamento[0].condicao_pagamento_erp,  # condicao_pagamento_erp
                               order.pagamento[0].opcao_pagamento_erp,  # opcao_pagamento_erp
                               order.codigo_rastreio or '',  # codigo_rastreio
                               str(datetime.strptime(order.previsao_entrega.replace('T', ' '),  # data_previsao_entrega
                                                     '%Y-%m-%d %H:%M:%S'))
                               if order.previsao_entrega is not None
                               and order.previsao_entrega != '0001-01-01T00:00:00' else None,
                               order.transportadora,  # transportadora
                               order.opcao_forma_entrega,  # opcao_forma_entrega
                               order.forma_envio_parceiro[0].modo_envio if src.client_data[
                                   'operacao'].lower().__contains__(
                                   'b2c') else order.forma_envio_parceiro.modo_envio,  # modo_envio
                               order.canal_id,  # canal_id
                               job_config.get('db_seller'),  # loja_id
                               order.representante,  # codigo_representante
                               order.cnpj_intermediador or '',  # cnpj_intermediador
                               order.identificador_vendedor,  # identificador_vendedor
                               order.usuario.EnderecoEntrega.cep,  # end_entrega_cep
                               order.usuario.EnderecoEntrega.tipo_logradouro,  # end_entrega_tipo_logradouro
                               order.usuario.EnderecoEntrega.logradouro,  # end_entrega_logradouro
                               order.usuario.EnderecoEntrega.numero,  # end_entrega_numero
                               order.usuario.EnderecoEntrega.complemento,  # end_entrega_complemento
                               order.usuario.EnderecoEntrega.bairro,  # end_entrega_bairro
                               order.usuario.EnderecoEntrega.cidade,  # end_entrega_cidade
                               order.usuario.EnderecoEntrega.estado,  # end_entrega_estado
                               order.usuario.EnderecoEntrega.referencia,  # END_ENTREGA_REFERENCIA_ENT
                               order.usuario.EnderecoEntrega.codigo_ibge or '',  # end_entrega_codigo_ibge
                               order.descritor_pre_definido_2,  # descritor_pre_definido_2
                               order.descritor_pre_definido_3,  # descritor_pre_definido_3
                               order.descritor_pre_definido_4,  # descritor_pre_definido_4
                               order.descritor_pre_definido_5,  # descritor_pre_definido_5
                               order.descritor_pre_definido_6,  # descritor_pre_definido_6
                               order.canal_site,
                               order.valor_taxa_servico
                           ]))

            if cursor.rowcount > 0:
                # LOG DEBUG -
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'P.11-TMP-Pedido [{order.id}] - CPF/CNPJ [{client_cpf_cnpj}], '
                    f' -- PEDIDO inserido na tabela SEMAFORO.PEDIDO do cliente SEMAFORO.CLIENTE: {client_id} '
                    f' -- Vai consultar no SEMAFORO os dados do PEDIDO, utilizando [PEDIDO_OKING_ID] ',
                    LogType.INFO,  # Voltar para - LogType.DEBUG
                    f'PED_{order.id}_P.11-TMP')

                cursor.execute(queries.get_query_order(db_config.db_type),
                               queries.get_command_parameter(db_config.db_type, [order.id]))
                (order_id,) = cursor.fetchone()
                if order_id is None or order_id <= 0:
                    # cursor.close()
                    # LOG DEBUG -
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f'P.12-TMP-Pedido [{order.id}] - CPF/CNPJ [{client_cpf_cnpj}], '
                        f' -- Não conseguiu recuperar os dados do Pedido',
                        LogType.ERROR,  # Voltar para - LogType.DEBUG
                        f'PED_{order.id}_P.12-TMP')
                    raise Exception('Nao foi possivel obter o pedido inserido no banco de dados')
            else:
                # cursor.close()
                # LOG DEBUG -
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'P.13-TMP-Pedido [{order.id}] - CPF/CNPJ [{client_cpf_cnpj}], '
                    f' -- Não conseguiu realizar o INSERT DO PEDIDO no banco de dados',
                    LogType.ERROR,  # Voltar para - LogType.DEBUG
                    f'PED_{order.id}_P.13-TMP')
                raise Exception('O pedido nao foi inserido')

            # insere itens
            step = 'P.9 -Itens Pedido Antes Executar a Query'
            # LOG DEBUG -
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'P.14-TMP-Pedido [{order.id}] - CPF/CNPJ [{client_cpf_cnpj}], '
                f' -- Vai inserir os itens da SEMAFORO.PEDIDO ID: {order_id}',
                LogType.INFO,  # Voltar para - LogType.DEBUG
                f'PED_{order.id}_P.14-TMP')

            for item in order.itens:
                item_params = queries.get_command_parameter(db_config.db_type, [
                   order_id,  # pedido_id,
                   item.sku_principal,  # sku
                   item.sku_variacao,  # codigo_erp
                   item.quantidade,  # quantidade
                   item.ean,  # ean
                   item.value,  # valor
                   item.valor_desconto,  # valor_desconto
                   0,  # valor_frete
                   # '',  # codigo_filial_erp
                   item.filial_expedicao,  # codigo_filial_expedicao_erp
                   item.filial_faturamento,  # CODIGO_FILIAL_FATURAMENT_ERP
                   item.cnpj_filial_venda,  # cnpj_filial_venda
                   item.valor_taxa_servico,  # cnpj_filial_venda
                   item.impostos.valor_substituicao_tributaria,
                   item.impostos.iva,
                   item.impostos.icms_intraestadual,
                   item.impostos.icms_interestadual,
                   item.impostos.valor_icms_interestadual,
                   item.impostos.percentual_ipi,
                   item.impostos.valor_ipi
                ])

                send_log(job_config.get('job_name'), False, False, f'P.14-TMP-Pedido [{order.id}] - Inserindo item no banco: {item_params}', LogType.INFO, f'PED_{order.id}_P.14-TMP')
                cursor.execute(queries.get_insert_b2b_order_items_command(db_config.db_type), item_params)

            # cursor.close()
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Passo {step} - Erro durante a inserção dos dados do pedido {order.id}: {str(e)}',
            LogType.ERROR,
            str(order.id))
        return False
    finally:
        # cursor.close()
        conn.close()


def query_get_log_integracao2(db_config: DatabaseConfig, order_id: str) -> str:
    try:
        db = database.Connection(db_config)
        conn = db.get_conect()
        with conn.cursor() as cursor:  # Fecha automaticamente ao sair do bloco
            cursor.execute(queries.get_log_integracao2(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [order_id]))
            row = cursor.fetchone()
            retorno = row[0] if row else ''  # Evita lançar erro
        conn.commit()
        return retorno
    except Exception as e:
        logger.error(f'Erro {e} ao consultar o log da integração do order {order_id}')
        return ''
    finally:
        if 'conn' in locals():  # Garante que a conexão será fechada
            conn.close()


def query_get_log_integracaoCliente(db_config: DatabaseConfig, order_id: str) -> str:
    try:
        db = database.Connection(db_config)
        conn = db.get_conect()
        with conn.cursor() as cursor:  # Fecha automaticamente ao sair do bloco
            cursor.execute(queries.get_log_integracao2(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [order_id]))
            row = cursor.fetchone()
            retorno = row[0] if row else ''  # Evita lançar erro
        conn.commit()
        return retorno
    except Exception as e:
        logger.error(f'Erro {e} ao consultar o log da integração de Cliente {order_id}')
        return ''
    finally:
        if 'conn' in locals():  # Garante que a conexão será fechada
            conn.close()


def job_send_suggested_sale(job_config):
    with lock:
        """
        Job para enviar venda sugerida no banco semáforo
        Args:
            job_config: Configuração do job
        """
        # Exibe mensagem monstrando que a Thread foi Iniciada
        logger.info(f'==== THREAD INICIADA -job: ' + job_config.get('job_name'))

        # LOG de Inicialização do Método - Para acompanhamento de execução
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Venda Sugerida - Iniciado',
            LogType.EXEC,
            'VENDA_SUGERIDA')
        db_config = utils.get_database_config(job_config)
        vendas_sugeridas = query_suggested_sale(job_config, db_config)
        try:
            api_suggested = []
            for venda in vendas_sugeridas:
                if api_suggested.__len__() < 50:
                    api_suggested.append(venda)
                else:
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f'Enviando Pacote: {api_suggested.__len__()}',
                        LogType.INFO,
                        'VENDA_SUGERIDA')
                    response = api_okVendas.send_suggested_sale(api_suggested)
                    if protocol_semaphore_suggested_sale(job_config, db_config, response):
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Venda Sugerida protocolada com sucesso no banco semaforo',
                            LogType.INFO,
                            'VENDA_SUGERIDA')
                    else:
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Falha ao protocolar venda sugerida no banco semaforo',
                            LogType.WARNING,
                            'VENDA_SUGERIDA')
                    api_suggested = []
            if api_suggested.__len__() > 0:
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Enviando Pacote: {api_suggested.__len__()}',
                    LogType.INFO,
                    'VENDA_SUGERIDA')
                response = api_okVendas.send_suggested_sale(api_suggested)
                if protocol_semaphore_suggested_sale(job_config, db_config, response):
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f'Venda Sugerida protocolada com sucesso no banco semaforo',
                        LogType.INFO,
                        'VENDA_SUGERIDA')
                else:
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f'Falha ao protocolar venda sugerida no banco semaforo',
                        LogType.WARNING,
                        'VENDA_SUGERIDA')

        except Exception as ex:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Erro {str(ex)}',
                LogType.ERROR,
                'VENDA_SUGERIDA')


def query_suggested_sale(job_config, db_config):
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        newsql = utils.final_query(db_config)
        if src.print_payloads:
            print(newsql)
        cursor.execute(newsql)
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        results = list(dict(zip(columns, row)) for row in rows)
        cursor.close()
        conn.close()
        vendas_sugeridas = []
        if len(results) > 0:
            vendas_sugeridas = (suggested_sale_dict(results))
        return vendas_sugeridas
    except Exception as ex:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f' Erro ao consultar vendas sugeridas: {str(ex)}',
            LogType.ERROR,
            'VENDA_SUGERIDA')
        raise ex


def suggested_sale_dict(sales):
    lista_body = []
    aux = []

    for i in sales:
        dicio = {}
        if i["codigo_cliente"] not in aux:
            aux.append(i["codigo_cliente"])
            dicio["codigo_cliente"] = i["codigo_cliente"]
            dicio["data_validade"] = (datetime.strptime(str(i["data_validade"]).replace('T', ' '),
                                                        '%Y-%m-%d %H:%M:%S.%f').strftime("%Y-%m-%d %H:%M:%S")) if i[
                                                                                                                      "data_validade"] is not None else None
            dicio["items"] = []
            lista_body.append(dicio)

        dicio2 = {"codigo_erp": i["codigo_erp"],
                  "quantidade": int(i["quantidade"]),
                  "ordem": i["ordem"]
                  }
        for a in range(len(lista_body)):
            if i["codigo_cliente"] == lista_body[a]["codigo_cliente"]:
                lista_body[a]["items"].append(dicio2)
                break
    return lista_body


def protocol_semaphore_suggested_sale(job_config, db_config, response):
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        for item in response:
            if item.Status == 1:
                msgret = 'SUCESSO'
            else:
                msgret = item.Message[:150]
            if item.Identifiers is not None:
                for identificador in item.Identifiers:
                    cursor.execute(queries.get_semaphore_command_data_sincronizacao(db_config.db_type),
                                   queries.get_command_parameter(db_config.db_type,
                                                                 [identificador, ' ',
                                                                  IntegrationType.VENDA_SUGERIDA.value,
                                                                  msgret]))
        count = cursor.rowcount
        cursor.close()
        conn.commit()
        conn.close()
        return count > 0

    except Exception as ex:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f' Erro ao protocolar venda sugerida no banco semaforo: {str(ex)}',
            LogType.ERROR,
            'VENDA_SUGERIDA')


def job_duplicate_internalized_order(job_config: dict):
    with lock:
        db_config = utils.get_database_config(job_config)
        # Exibe mensagem monstrando que a Thread foi Iniciada
        logger.info(f'==== THREAD INICIADA -job: ' + job_config.get('job_name'))

        # LOG de Inicialização do Método - Para acompanhamento de execução
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Duplica pedido internalizado - Iniciado',
            LogType.EXEC,
            'DUPLICARPEDIDO')

        if db_config.sql is None:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Comando sql para duplicar pedidos',
                LogType.WARNING,
                'DUPLICARPEDIDO')
            return
        if job_config['executar_query_semaforo'] == 'S':
            executa_comando_sql(db_config, job_config)

        queue = api_okHUB.get_queue_order_to_duplicate()
        qty = 0
        for q_order in queue:
            try:
                sleep(0.5)
                qty = qty + 1
                print()
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Iniciando processamento ({qty} de {len(queue)}) Pedido OKING ID: {q_order.pedido_oking_id}',
                    LogType.INFO,
                    'DUPLICARPEDIDO')
                order = api_okHUB.get_order(src.client_data, q_order.pedido_oking_id)
                # Pedido integrado anteriormente
                if order.capa.numero_pedido_externo is not None and order.capa.numero_pedido_externo != '':

                    if check_order_existence(db_config, int(order.capa.pedido_oking_id)):
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Pedido ja integrado com o ERP, chamando procedure de atualizacao...',
                            LogType.INFO,
                            'DUPLICARPEDIDO')
                        if call_update_order_procedure(job_config, db_config, int(order.capa.pedido_oking_id),
                                                       order.capa.status):
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'Pedido atualizado com sucesso',
                                LogType.INFO,
                                'DUPLICARPEDIDO')
                            set_codigo_erp_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                                 order_erp_id=order.capa.numero_pedido_externo, client_erp_id='')
                    else:
                        # Duplicar o Pedido - Inserir novo
                        if check_non_integrated_order_existence(db_config,
                                                                int(order.capa.pedido_oking_id)):  # Pedido existente no banco semaforo

                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'Pedido já existente no banco semáforo, porem nao integrado com erp. '
                                f' Chamando procedures',
                                LogType.INFO,
                                'DUPLICARPEDIDO')
                            # Chama a Procedure para Inserir o Pedido no ERP (cliente)
                            sp_success, client_erp_id, order_erp_id = call_order_procedures(job_config, db_config,
                                                                                            int(order.capa.pedido_oking_id))
                            log = query_get_log_integracao2(db_config, q_order.pedido_oking_id)
                            if log:
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'Log de integração do pedido - {q_order.pedido_oking_id}: {log}',
                                    LogType.ERROR,
                                    'DUPLICARPEDIDO')
                            if sp_success:
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'Chamadas das procedures executadas com sucesso, protocolando pedido...',
                                    LogType.INFO,
                                    'DUPLICARPEDIDO')
                                set_codigo_erp_order(job_config, db_config=db_config, order=order, queue_order=q_order,
                                                     order_erp_id=order_erp_id, client_erp_id=client_erp_id)

                        elif True:  # Pedido nao existe no semaforo e esta em status de internalizacao (pending e paid)

                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'Inserindo novo pedido no banco semaforo',
                                LogType.INFO,
                                'DUPLICARPEDIDO')
                            inserted = insert_temp_order(job_config, order, db_config)
                            if inserted:
                                send_log(
                                    job_config.get('job_name'),
                                    job_config.get('enviar_logs'),
                                    job_config.get('enviar_logs_debug'),
                                    f'Pedido inserido com sucesso, chamando procedures...',
                                    LogType.INFO,
                                    'DUPLICARPEDIDO')
                                # Chama a Procedure para Inserir o Pedido no ERP (cliente)
                                sp_success, client_erp_id, order_erp_id = call_order_procedures(job_config, db_config,
                                                                                                int(order.capa
                                                                                                    .pedido_oking_id))
                                log = query_get_log_integracao2(db_config, q_order.pedido_oking_id)
                                if log:
                                    send_log(
                                        job_config.get('job_name'),
                                        job_config.get('enviar_logs'),
                                        job_config.get('enviar_logs_debug'),
                                        f'Log de integração do pedido - {q_order.pedido_oking_id}: {log}',
                                        LogType.ERROR,
                                        'DUPLICARPEDIDO')
                                if sp_success:
                                    send_log(
                                        job_config.get('job_name'),
                                        job_config.get('enviar_logs'),
                                        job_config.get('enviar_logs_debug'),
                                        f'Chamadas das procedures executadas com sucesso, protocolando pedido...',
                                        LogType.INFO,
                                        'PEDIDO')
                                    set_codigo_erp_order(job_config, db_config=db_config, order=order,
                                                         queue_order=q_order,
                                                         order_erp_id=order_erp_id, client_erp_id=client_erp_id)

                else:  # Pedido nao integrado - Não deverá ser Duplicado
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f' MENSAGEM',
                        LogType.ERROR,
                        'DUPLICARPEDIDO')

            except Exception as e:
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Erro no processamento do pedido {q_order.pedido_oking_id}: {str(e)}',
                    LogType.ERROR,
                    q_order.pedido_oking_id)
                raise


def query_update_status_observacao(job_config, db_config, order):
    logger.info(f'=== Passo 3 - No método de update')
    try:
        db = database.Connection(db_config)
        conn = db.get_conect()
        cursor = conn.cursor()
        cursor.execute(queries.update_status_observacao(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type,
                                                     [order.status_observacao, order.id]))
        count = cursor.rowcount
        cursor.close()
        conn.commit()
        conn.close()
        logger.info(f'=== Passo 4 - Antes de retornar se cursor.rowcount > 0')
        return count > 0
    except Exception as ex:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f' Erro ao ATUALIZAR Log_Integracao do pedido {order.id} erro : {str(ex)}',
            LogType.ERROR,
            'PEDIDO')
    logger.info(f'=== Passo 5 - Retorno False do método de update')
    return False


def query_update_status_pedido(job_config, db_config, order):
    logger.info(f'=== Passo 1 - Método: query_update_status_pedido ')
    try:
        db = database.Connection(db_config)
        conn = db.get_conect()
        cursor = conn.cursor()
        cursor.execute(queries.update_status_pedido(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type,
                                                     [order.status, order.id]))
        count = cursor.rowcount
        cursor.close()
        conn.commit()
        conn.close()
        logger.info(f'=== Passo 2 - Antes de retornar se cursor.rowcount > 0')
        return count > 0
    except Exception as ex:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f' Erro ao ATUALIZAR [STATUS] da tabela [SEMAFORO.PEDIDO] - {order.id} erro : {str(ex)}',
            LogType.ERROR,
            'PEDIDO')
    logger.info(f'=== Passo 3 - Retorno False do Método: query_update_status_pedido ')
    return False


def job_send_order_to_okvendas(job_config: dict):
    with lock:
        """
        Job para enviar pedido para okvendas
        Args:
            job_config: Configuração do job
        """
        # Exibe mensagem monstrando que a Thread foi Iniciada
        logger.info(f'==== THREAD INICIADA -job: ' + job_config.get('job_name'))

        # LOG de Inicialização do Método - Para acompanhamento de execução
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Envia pedido para Okvendas - Iniciado',
            LogType.EXEC,
            'PEDIDO_PARA_OKVENDAS')
        db_config = utils.get_database_config(job_config)
        pedido_para_okvendas = query_send_order_to_okvendas(db_config, job_config)
        try:
            for pedido in pedido_para_okvendas:
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Enviando Pedido',
                    LogType.INFO,
                    'PEDIDO_PARA_OKVENDAS')
                response = api_okVendas.post_send_order_to_okvenas(job_config, pedido)
                if protocol_semaphore_order_to_okvendas(job_config, db_config, response,
                                                        pedido["numero_pedido_externo"]):
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f'Pedido para okvendas protocolado com sucesso no banco semaforo',
                        LogType.INFO,
                        'PEDIDO_PARA_OKVENDAS')
                else:
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f'Falha ao protocolar pedido para okvendas no banco semaforo',
                        LogType.WARNING,
                        'PEDIDO_PARA_OKVENDAS')

        except Exception as ex:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Erro {str(ex)}',
                LogType.ERROR,
                'PEDIDO_PARA_OKVENDAS')


def query_send_order_to_okvendas(db_config, job_config):
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        newsql = utils.final_query(db_config)
        if src.print_payloads:
            print(newsql)
        cursor.execute(newsql)
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        results = list(dict(zip(columns, row)) for row in rows)
        cursor.close()
        conn.close()
        vendas_to_okvendas = []
        if len(results) > 0:
            vendas_to_okvendas = (order_to_okvendas_dict(results))
        return vendas_to_okvendas
    except Exception as ex:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f' Erro ao consultar pedido para okvendas: {str(ex)}',
            LogType.ERROR,
            'PEDIDO_PARA_OKVENDAS')
        raise ex


def order_to_okvendas_dict(vendas_to_okvendas):
    lista_body = []
    aux = []

    for i in vendas_to_okvendas:
        dicio = {}
        if i["codigo_referencia"] not in aux:
            aux.append(i["codigo_referencia"])
            dicio["numero_pedido_externo"] = i["numero_pedido_externo"]
            dicio["codigo_referencia"] = i["codigo_referencia"]
            dicio["canal_venda"] = 29
            dicio["status_pedido"] = i["status_pedido"]
            dicio["tipo_pedido"] = 1
            dicio["valor_total"] = i["valor_total"]
            dicio["valor_frete"] = i["valor_frete"]
            dicio["valor_desconto"] = i["valor_desconto"]
            dicio["data_pedido"] = (datetime.strptime(str(i["data_pedido"]).replace('T', ' '),
                                                      '%Y-%m-%d %H:%M:%S.%f').strftime("%Y-%m-%d %H:%M:%S")) if i[
                                                                                                                    "data_pedido"] is not None else None
            dicio["tipo_frete"] = "CIF"
            dicio["previsao_entrega"] = (datetime.strptime(str(i["previsao_entrega"]).replace('T', ' '),
                                                           '%Y-%m-%d %H:%M:%S.%f').strftime("%Y-%m-%d %H:%M:%S")) if i[
                                                                                                                         "previsao_entrega"] is not None else None
            dicio["data_programada"] = (datetime.strptime(str(i["data_programada"]).replace('T', ' '),
                                                          '%Y-%m-%d %H:%M:%S.%f').strftime("%Y-%m-%d %H:%M:%S")) if i[
                                                                                                                        "data_programada"] is not None else None

            dicio["identificador_cliente"] = i["identificador_cliente"]
            dicio["identificadorFilial"] = i["identificadorfilial"]
            dicio["identificador_loja"] = i["identificador_loja"]
            dicio["identificador_representante"] = i["identificador_representante"]
            dicio["identificador_vendedor"] = i["identificador_vendedor"]
            dicio["identificador_pagamento"] = i["identificador_pagamento"]
            dicio["identificador_Forma_Entrega"] = i["identificador_forma_entrega"]

            dicio["codigo_financeiro"] = i["codigo_financeiro"]
            dicio["codigo_comercial"] = i["codigo_comercial"]
            dicio["observacao"] = "Pedido Criado VIA API - Histórico de Compra"
            dicio["sugestao_descricao"] = i["sugestao_descricao"]
            dicio["pedido_venda_canal_id"] = i["pedido_venda_canal_id"]
            dicio["pedido_venda_canal_alternativo"] = i["pedido_venda_canal_alternativo"]

            dicio["itens"] = []
            dicio["titulos"] = []
            dicio["entrega"] = {
                "telefone_contato": i["telefone_contato"],
                "cep": i["cep"],
                "endereco": i["endereco"],
                "numero": i["numero"],
                "bairro": i["bairro"],
                "cidade": i["cidade"],
                "estado": i["estado"],
                "pais": i["pais"],
                "descricao_endereco": i["descricao_endereco"],
                "referencia": i["referencia"],
                "complemento": i["complemento"]
            }
            dicio["protocolo"] = True
            lista_body.append(dicio)

        dicio2 = {
            "codigo_erp": i["codigo_erp"],
            "unidade_distribuicao": i["unidade_distribuicao"],
            "valor_item": i["valor_item"],
            "desconto": i["desconto"],
            "quantidade": i["quantidade"],
            "codigo_filial_faturamento_expedicao": i["codigo_filial_faturamento_expedicao"]
        }

        dicio3 = {
            "codigo_titulo": i["codigo_titulo"],
            "numero_parcela": i["numero_parcela"],
            "valor": float(i["valor"]),
            "valor_pago": float(i["valor_pago"]),
            "data_vencimento": (datetime.strptime(str(i["data_vencimento"]).replace('T', ' '),
                                                  '%Y-%m-%d %H:%M:%S.%f').strftime("%Y-%m-%d %H:%M:%S")) if i[
                                                                                                                "data_vencimento"] is not None else None,

            "data_pagamento": (datetime.strptime(str(i["data_pagamento"]).replace('T', ' '),
                                                 '%Y-%m-%d %H:%M:%S.%f').strftime("%Y-%m-%d %H:%M:%S")) if i[
                                                                                                               "data_pagamento"] is not None else None,

            "transacao": i["transacao"],
            "link_boleto": i["link_boleto"]
        }
        for a in range(len(lista_body)):
            if i["codigo_referencia"] == lista_body[a]["codigo_referencia"]:
                lista_body[a]["itens"].append(dicio2)
                lista_body[a]["titulos"].append(dicio3)
                break
    return lista_body


def protocol_semaphore_order_to_okvendas(job_config, db_config, response, numero_pedido_externo):
    logger.info("== Okvendas - Dentro do protocol order_to_okvendas")
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        if "status_code" in response and response["status_code"] == "Pedido_confirmado":
            msgret = 'SUCESSO'
            logger.info("== Okvendas - Antes de protocolar na semáforo")
            if src.print_payloads:
                print(response)
                print("Query: ", queries.get_insert_update_semaphore_command(db_config.db_type))
                print("Parametros da Query: ", queries.get_command_parameter(db_config.db_type,
                                                                             [numero_pedido_externo, ' ',
                                                                              IntegrationType.PEDIDO_PARA_OKVENDAS.value,
                                                                              msgret]))
            cursor.execute(queries.get_insert_update_semaphore_command(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type,
                                                         [numero_pedido_externo, ' ',
                                                          IntegrationType.PEDIDO_PARA_OKVENDAS.value,
                                                          msgret]))

            logger.info("==== ANTES DO ROWCOUNT ====")
            count = cursor.rowcount
            cursor.close()
            conn.commit()
            conn.close()
            return count > 0
        return False
    except Exception as ex:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f' Erro ao protocolar pedido para Okvendas no banco semaforo: {str(ex)}',
            LogType.ERROR,
            'PEDIDO_PARA_OKVENDAS')


def log_sql_command_oracle(sql, params):
    # Substitui os placeholders :1, :2, :3...
    def replace(match):
        index = int(match.group(1)) - 1
        if 0 <= index < len(params):
            return repr(params[index])
        return match.group(0)  # se não tiver parâmetro correspondente

    return re.sub(r":(\d+)", replace, sql)