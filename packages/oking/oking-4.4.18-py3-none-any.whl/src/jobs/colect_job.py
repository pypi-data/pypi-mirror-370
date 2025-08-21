from datetime import datetime
import logging

from src.jobs.utils import executa_comando_sql

import src.database.connection as database
import src.database.utils as utils
from src.database.queries import IntegrationType
from src.jobs.system_jobs import OnlineLogger
from src.database.utils import DatabaseConfig
import src.api.okinghub as api_okHUB
from src.api import okvendas as api_OkVendas
from src.api import slack
from src.database import queries
import src
import time
import json
import jsonpickle
from threading import Lock
from src.log_types import LogType

lock = Lock()

logger = logging.getLogger()
send_log = OnlineLogger.send_log


def job_send_clients_colect(job_config_dict: dict):
    """
    Job para enviar clientes
    Args:
        job_config_dict: Configuração do job
    """
    with lock:
        try:
            db_config = utils.get_database_config(job_config_dict)
            logger.info(f'==== THREAD INICIADA -job: ' + job_config_dict.get('job_name'))
            send_log(
                job_config_dict.get('job_name'),
                job_config_dict.get('enviar_logs'),
                job_config_dict.get('enviar_logs_debug'),
                f'Coleta cliente',
                LogType.EXEC,
                'COLETA_DADOS_CLIENTE')

            if job_config_dict['executar_query_semaforo'] == 'S':
                executa_comando_sql(db_config, job_config_dict)

            clients = query_colect_clients_erp(job_config_dict, db_config)
            if clients is not None and len(clients) > 0:
                send_log(
                    job_config_dict.get('job_name'),
                    job_config_dict.get('enviar_logs'),
                    job_config_dict.get('enviar_logs_debug'),
                    f'Clientes para atualizar {len(clients)}',
                    LogType.INFO,
                    'COLETA_DADOS_CLIENTE')

                api_clients = []
                for client in clients:
                    if api_clients.__len__() < 50:
                        api_clients.append(client)
                    else:
                        send_log(
                            job_config_dict.get('job_name'),
                            job_config_dict.get('enviar_logs'),
                            job_config_dict.get('enviar_logs_debug'),
                            f'Enviando Pacote: {api_clients.__len__()}',
                            LogType.INFO,
                            'COLETA_DADOS_CLIENTE')
                        response = api_okHUB.post_clients(api_clients)
                        api_clients = []
                        if LogType.ERROR in response:
                            send_log(
                                job_config_dict.get('job_name'),
                                job_config_dict.get('enviar_logs'),
                                job_config_dict.get('enviar_logs_debug'),
                                f'Erro {response["error"]}: {response["message"]}',
                                LogType.ERROR,
                                'COLETA_DADOS_CLIENTE')
                        else:
                            send_log(
                                job_config_dict.get('job_name'),
                                job_config_dict.get('enviar_logs'),
                                job_config_dict.get('enviar_logs_debug'),
                                f'Tratando retorno',
                                LogType.INFO,
                                'COLETA_DADOS_CLIENTE')
                            validate_response_client(response, db_config, job_config_dict)

                # Se ficou algum sem processa
                if api_clients.__len__() > 0:
                    send_log(
                        job_config_dict.get('job_name'),
                        job_config_dict.get('enviar_logs'),
                        job_config_dict.get('enviar_logs_debug'),
                        f'Enviando Pacote: {api_clients.__len__()}',
                        LogType.INFO,
                        'COLETA_DADOS_CLIENTE')
                    response = api_okHUB.post_clients(api_clients)
                    if LogType.ERROR in response:
                        send_log(
                            job_config_dict.get('job_name'),
                            job_config_dict.get('enviar_logs'),
                            job_config_dict.get('enviar_logs_debug'),
                            f'Erro {response["error"]}: {response["message"]}',
                            LogType.ERROR,
                            'COLETA_DADOS_CLIENTE')
                    else:
                        send_log(
                            job_config_dict.get('job_name'),
                            job_config_dict.get('enviar_logs'),
                            job_config_dict.get('enviar_logs_debug'),
                            f'Tratando retorno',
                            LogType.INFO,
                            'COLETA_DADOS_CLIENTE')
                        validate_response_client(response, db_config, job_config_dict)
            else:
                send_log(
                    job_config_dict.get('job_name'),
                    job_config_dict.get('enviar_logs'),
                    job_config_dict.get('enviar_logs_debug'),
                    f'Nao existem clientes a serem enviados no momento',
                    LogType.WARNING,
                    'CLIENTE')
        except Exception as e:
            send_log(
                job_config_dict.get('job_name'),
                job_config_dict.get('enviar_logs'),
                job_config_dict.get('enviar_logs_debug'),
                f'Erro durante execucao do job: {str(e)}',
                LogType.ERROR,
                'COLETA_DADOS_CLIENTE')


def query_colect_clients_erp(job_config_dict: dict, db_config: DatabaseConfig):
    """
    Consulta os clientes para atualizar no banco de dados
    Args:
        job_config_dict: Configuração do job
        db_config: Configuracao do banco de dados

    Returns:
        Lista de clientes para atualizar
    """
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()

    try:
        # monta query com EXISTS e NOT EXISTS
        # verificar se já possui WHERE
        newsql = utils.final_query(db_config)
        if src.print_payloads:
            print(newsql)
        cursor.execute(newsql)
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        results = list(dict(zip(columns, row)) for row in rows)
        cursor.close()
        conn.close()

        clients = []
        if len(results) > 0:
            clients = client_dict(results)
        return clients
    except Exception as ex:
        if src.exibir_interface_grafica:
            raise
        else:
            send_log(
                job_config_dict.get('job_name'),
                job_config_dict.get('enviar_logs'),
                job_config_dict.get('enviar_logs_debug'),
                f' Erro ao consultar clientes no banco semaforo: {str(ex)}',
                LogType.ERROR,
                'COLETA_DADOS_CLIENTE')


def client_dict(clients):
    lista = []
    for row in clients:
        row = {k.lower(): v for k, v in row.items()}
        pdict = {
            'token': str(src.client_data.get('token_oking')),
            'kdm': str(row['kdm']),
            'agente': str(row['agente']),
            'unidade': str(row['unidade']),
            'codigo_cliente': str(row['codigo_cliente']),
            'nome': str(row['nome']),
            'cnpj': str(row['cnpj']),
            'data_cadastro': str(row['data_cadastro']),
            'ddd': int(row['ddd']),
            'telefone': str(row['telefone']),
            'email': str(row['email']),
            'endereco': str(row['endereco']),
            'numero': str(row['numero']),
            'bairro': str(row['bairro']),
            'uf': str(row['uf']),
            'faturamento_anual_total': int(row['faturamento_anual_total']) if 'faturamento_anual_total' in row else 0,
            'consumo_cimento': float(row['consumo_cimento']) if 'consumo_cimento' in row else 0.0,
            'percentual_faturamento_cimento': int(
                row['percentual_faturamento_cimento']) if 'percentual_faturamento_cimento' in row else 0,
            'canal': str(row['canal']),
            'municipio': str(row['municipio']),
            'uf_municipio': str(row['uf_municipio']),
            'codigo_ibge': str(row['codigo_ibge']),
            "cep": str(row['cep']),
            "contato": str(row['contato']) if 'contato' in row else '',
            "contato_cargo": str(row['contato_cargo']) if 'contato_cargo' in row else '',
            "canal_segmento": str(row['canal_segmento']) if 'canal_segmento' in row else '',
            "status": str(row['status']) if 'status' in row else '',
            "vendedor": str(row['vendedor']) if 'vendedor' in row else '',
            "ultima_atualizacao": None,
            "segmento_cliente": str(row['segmento_cliente']) if 'segmento_cliente' in row else '',
            "marca_exclusivo": str(row['marca_exclusivo']) if 'marca_exclusivo' in row else '',
            "multimarca_percentual": int(row['multimarca_percentual']) if 'multimarca_percentual' in row else 0,
            "marca_principal_concorrente": str(
                row['marca_principal_concorrente']) if 'marca_principal_concorrente' in row else '',
            "marca_segundo_concorrente": str(
                row['marca_segundo_concorrente']) if 'marca_segundo_concorrente' in row else '',
        }
        lista.append(pdict)

    return lista


def validate_response_client(response, db_config, job_config_dict):
    if response is not None:
        conexao = database.Connection(db_config)
        conn = conexao.get_conect()
        cursor = conn.cursor()

        # Percorre todos os registros
        for item in response:
            identificador = item.identificador
            identificador2 = item.identificador2
            if item.sucesso == 1 or item.sucesso == 'true':
                try:
                    cursor.execute(queries.get_insert_update_semaphore_command(db_config.db_type),
                                   queries.get_command_parameter(db_config.db_type,
                                                                 [identificador, identificador2,
                                                                  IntegrationType.COLETA_DADOS_CLIENTE.value,
                                                                  'SUCESSO']))
                    # atualizados.append(response['identificador'])
                except Exception as e:
                    send_log(
                        job_config_dict.get('job_name'),
                        job_config_dict.get('enviar_logs'),
                        job_config_dict.get('enviar_logs_debug'),
                        f'Erro ao atualizar Cliente do sku: {item.identificador}, Erro: {str(e)}',
                        LogType.ERROR,
                        f'{item.identificador}-{item.identificador2}')
            else:
                send_log(
                    job_config_dict.get('job_name'),
                    job_config_dict.get('enviar_logs'),
                    job_config_dict.get('enviar_logs_debug'),
                    f'Erro ao atualizar Cliente para o sku: {identificador}, {item.Message}',
                    LogType.WARNING,
                    f'{item.identificador}-{item.identificador2}')

        cursor.close()
        conn.commit()
        conn.close()


def job_send_sales_colect(job_config_dict: dict):
    """
    Job para enviar vendas
    Args:
        job_config_dict: Configuração do job
    """
    with lock:
        try:
            db_config = utils.get_database_config(job_config_dict)
            logger.info(f'==== THREAD INICIADA -job: ' + job_config_dict.get('job_name'))
            send_log(
                job_config_dict.get('job_name'),
                job_config_dict.get('enviar_logs'),
                job_config_dict.get('enviar_logs_debug'),
                f'Coleta venda',
                LogType.EXEC,
                'COLETA_DADOS_VENDA')

            if job_config_dict['executar_query_semaforo'] == 'S':
                executa_comando_sql(db_config, job_config_dict)

            vendas = query_vendas_erp(job_config_dict, db_config)
            if vendas is not None and len(vendas) > 0:
                send_log(
                    job_config_dict.get('job_name'),
                    job_config_dict.get('enviar_logs'),
                    job_config_dict.get('enviar_logs_debug'),
                    f'VENDAS para atualizar {len(vendas)}',
                    LogType.INFO,
                    'COLETA_DADOS_VENDA')

                api_vendas = []
                for venda in vendas:
                    if api_vendas.__len__() < 50:
                        api_vendas.append(venda)
                    else:
                        send_log(
                            job_config_dict.get('job_name'),
                            job_config_dict.get('enviar_logs'),
                            job_config_dict.get('enviar_logs_debug'),
                            f'Enviando Pacote: {api_vendas.__len__()}',
                            LogType.INFO,
                            'COLETA_DADOS_VENDA')
                        response = api_okHUB.post_vendas(api_vendas)
                        api_vendas = []
                        if LogType.ERROR in response:
                            send_log(
                                job_config_dict.get('job_name'),
                                job_config_dict.get('enviar_logs'),
                                job_config_dict.get('enviar_logs_debug'),
                                f'Erro {response["error"]}: {response["message"]}',
                                LogType.ERROR,
                                'COLETA_DADOS_VENDA')
                        else:
                            send_log(
                                job_config_dict.get('job_name'),
                                job_config_dict.get('enviar_logs'),
                                job_config_dict.get('enviar_logs_debug'),
                                f'Tratando retorno',
                                LogType.INFO,
                                'COLETA_DADOS_VENDA')
                            validate_response_vendas(response, db_config, job_config_dict)

                # Se ficou algum sem processa
                if api_vendas.__len__() > 0:
                    send_log(
                        job_config_dict.get('job_name'),
                        job_config_dict.get('enviar_logs'),
                        job_config_dict.get('enviar_logs_debug'),
                        f'Enviando Pacote: {api_vendas.__len__()}',
                        LogType.INFO,
                        'COLETA_DADOS_VENDA')
                    response = api_okHUB.post_vendas(api_vendas)
                    if LogType.ERROR in response:
                        send_log(
                            job_config_dict.get('job_name'),
                            job_config_dict.get('enviar_logs'),
                            job_config_dict.get('enviar_logs_debug'),
                            f'Erro {response["error"]}: {response["message"]}',
                            LogType.ERROR,
                            'COLETA_DADOS_VENDA')
                    else:
                        send_log(
                            job_config_dict.get('job_name'),
                            job_config_dict.get('enviar_logs'),
                            job_config_dict.get('enviar_logs_debug'),
                            f'Tratando retorno',
                            LogType.INFO,
                            'COLETA_DADOS_VENDA')
                        validate_response_vendas(response, db_config, job_config_dict)
            else:
                send_log(
                    job_config_dict.get('job_name'),
                    job_config_dict.get('enviar_logs'),
                    job_config_dict.get('enviar_logs_debug'),
                    f'Nao existem vendas a serem enviadas no momento',
                    LogType.WARNING,
                    'COLETA_DADOS_VENDA')
        except Exception as e:
            send_log(
                job_config_dict.get('job_name'),
                job_config_dict.get('enviar_logs'),
                job_config_dict.get('enviar_logs_debug'),
                f'Erro durante execucao do job: {str(e)}',
                LogType.ERROR,
                'COLETA_DADOS_VENDA')


def query_vendas_erp(job_config_dict: dict, db_config: DatabaseConfig):
    """
    Consulta as vendas para atualizar no banco de dados
    Args:
        job_config_dict: Configuração do job
        db_config: Configuracao do banco de dados

    Returns:
        Lista de vendas para atualizar
    """
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()

    try:
        # monta query com EXISTS e NOT EXISTS
        # verificar se já possui WHERE
        newsql = utils.final_query(db_config)
        if src.print_payloads:
            print(newsql)
        cursor.execute(newsql)
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        results = list(dict(zip(columns, row)) for row in rows)
        cursor.close()
        conn.close()

        vendas = []
        if len(results) > 0:
            vendas = venda_dict(results)
        return vendas
    except Exception as ex:
        send_log(
            job_config_dict.get('job_name'),
            job_config_dict.get('enviar_logs'),
            job_config_dict.get('enviar_logs_debug'),
            f' Erro ao consultar vendas no banco semaforo: {str(ex)}',
            LogType.ERROR,
            'COLETA_DADOS_VENDA')
        if src.exibir_interface_grafica:
            raise


def validate_response_vendas(response, db_config, job_config_dict):
    if response is not None:
        conexao = database.Connection(db_config)
        conn = conexao.get_conect()
        cursor = conn.cursor()

        # Percorre todos os registros
        for item in response:
            identificador = item.identificador
            identificador2 = item.identificador2
            if item.sucesso == 1 or item.sucesso == 'true':
                try:
                    cursor.execute(queries.get_insert_update_semaphore_command(db_config.db_type),
                                   queries.get_command_parameter(db_config.db_type,
                                                                 [identificador, identificador2,
                                                                  IntegrationType.COLETA_DADOS_VENDA.value,
                                                                  'SUCESSO']))
                    # atualizados.append(response['identificador'])
                except Exception as e:
                    send_log(
                        job_config_dict.get('job_name'),
                        job_config_dict.get('enviar_logs'),
                        job_config_dict.get('enviar_logs_debug'),
                        f'Erro ao atualizar Venda do kdm: {item.identificador}, Erro: {str(e)}',
                        LogType.ERROR,
                        f'{item.identificador}-{item.identificador2}')
            else:
                send_log(
                    job_config_dict.get('job_name'),
                    job_config_dict.get('enviar_logs'),
                    job_config_dict.get('enviar_logs_debug'),
                    f'Erro ao atualizar Venda para o kdm: {identificador}, {item.Message}',
                    LogType.WARNING,
                    f'{item.identificador}-{item.identificador2}')

        cursor.close()
        conn.commit()
        conn.close()


def venda_dict(vendas):
    lista = []
    for row in vendas:
        pdict = {
            'token': str(src.client_data.get('token_oking')),
            'kdm': str(row['kdm']),
            'agente': str(row['agente']),
            'unidade': str(row['unidade']),
            'codigo_cliente': str(row['codigo_cliente']),
            'codigo_venda': str(row['codigo_venda']),
            'nome_cliente': str(row['nome_cliente']),
            'cnpj_cliente': str(row['cnpj_cliente']),
            'data_pedido': str(row['data_pedido']),
            'data_venda': str(row['data_venda']),
            'familia_produto': str(row['familia_produto']),
            # 'marca': str(row['marca']),
            'quantidade_sacos': int(row['quantidade_sacos']),
            'preco_saco': float(row['preco_saco']),
            'prazo_pagamento': str(row['prazo_pagamento']),
            'tipo_entrega': str(row['tipo_entrega']),
            'frete_entrega': float(row['frete_entrega']),
            'paletizado_unitario': str(row['paletizado_unitario']),
            'ajudante_descarga': bool(row['ajudante_descarga']),
            'custo_chapa': float(row['custo_chapa']),
            'acao_precos': bool(row['acao_precos']),
            'quantidade': str(row['quantidade']) if 'quantidade' in row else '',
            'expedicao': str(row['expedicao']) if 'expedicao' in row else '',
            'codigo_entrega': str(row['codigo_entrega']) if 'codigo_entrega' in row else '',
            'frete_entrega_total': float(row['frete_entrega_total']) if 'frete_entrega_total' in row else 0.0,
            'tipo_caminhao': str(row['tipo_caminhao']) if 'tipo_caminhao' in row else '',
            'taxa_ocupacao_caminhao': str(row['taxa_ocupacao_caminhao']) if 'taxa_ocupacao_caminhao' in row else '',
            'valor_total_ajudante': float(row['valor_total_ajudante']) if 'valor_total_ajudante' in row else 0.0,
            'valor_saco_ajudante': float(row['valor_saco_ajudante']) if 'valor_saco_ajudante' in row else 0.0,
            'acao_marketing': str(row['acao_marketing']) if 'acao_marketing' in row else '',
            'estoque_dia': int(row['estoque_dia']) if 'estoque_dia' in row else 0,
            'receita': float(row['receita']) if 'receita' in row else 0.0,
            'otif': str(row['otif']) if 'otfi' in row else '',
            'carteira': str(row['carteira']) if 'carteira' in row else '',
            'volume_dia_util': int(row['volume_dia_util']) if 'volume_dia_util' in row else 0,
            'custos_logisticos': float(row['custos_logisticos']) if 'custos_logisticos' in row else 0.0,
            'mkp': float(row['mkp']) if 'mkp' in row else 0.0,
            'coletas': str(row['coletas']) if 'coletas' in row else '',
            'forma_pagamento': str(row['forma_pagamento']),
            'acao_desconto': float(row['acao_desconto']),
            'valor_acao': float(row['valor_acao']),
            'marca_produto': str(row['marca_produto']),
            'peso_saco': int(row['peso_saco']),
            'peso': int(row['peso']),
        }
        lista.append(pdict)

    return lista


def job_send_colect_physical_shopping(job_config_dict: dict):
    """
        Job para compras físicas
        Args:
            job_config_dict: Configuração do job
        """
    with lock:
        try:
            db_config = utils.get_database_config(job_config_dict)
            logger.info(f'==== THREAD INICIADA -job: ' + job_config_dict.get('job_name'))
            send_log(
                job_config_dict.get('job_name'),
                job_config_dict.get('enviar_logs'),
                job_config_dict.get('enviar_logs_debug'),
                f'Coleta compras loja física',
                LogType.EXEC,
                'COLETA_DADOS_COMPRA_FISICA')

            if job_config_dict['executar_query_semaforo'] == 'S':
                executa_comando_sql(db_config, job_config_dict)

            compras = query_compras_erp(job_config_dict, db_config)

            if compras is not None and len(compras) > 0:
                send_log(
                    job_config_dict.get('job_name'),
                    job_config_dict.get('enviar_logs'),
                    job_config_dict.get('enviar_logs_debug'),
                    f'VENDAS para atualizar {len(compras)}',
                    LogType.INFO,
                    'COLETA_DADOS_VENDA')

                for compra in compras:
                    send_log(
                        job_config_dict.get('job_name'),
                        job_config_dict.get('enviar_logs'),
                        job_config_dict.get('enviar_logs_debug'),
                        f'Enviando Pacote',
                        LogType.INFO,
                        'COLETA_DADOS_COMPRA_FISICA')
                    response = api_OkVendas.post_colect_physical_shopping(compra)

                    if response is None:
                        send_log(
                            job_config_dict.get('job_name'),
                            job_config_dict.get('enviar_logs'),
                            job_config_dict.get('enviar_logs_debug'),
                            f'Dados compra física enviados com sucesso',
                            LogType.INFO,
                            'COLETA_DADOS_COMPRA_FISICA')
                    else:
                        # Tratamento inteligente do response
                        if hasattr(response, 'status_code'):
                            if response.status_code == 404:
                                send_log(
                                    job_config_dict.get('job_name'),
                                    job_config_dict.get('enviar_logs'),
                                    job_config_dict.get('enviar_logs_debug'),
                                    f'{str(response)}, '
                                    f'verifique os dados: { jsonpickle.encode(compra, unpicklable=False)}',
                                    LogType.WARNING,
                                    'COLETA_DADOS_COMPRA_FISICA')
                            else:
                                send_log(
                                    job_config_dict.get('job_name'),
                                    job_config_dict.get('enviar_logs'),
                                    job_config_dict.get('enviar_logs_debug'),
                                    f'Erro HTTP {response.status_code}: {str(response.content)}',
                                    LogType.ERROR,
                                    'COLETA_DADOS_COMPRA_FISICA')
                        else:
                            # Response de tipo desconhecido
                            send_log(
                                job_config_dict.get('job_name'),
                                job_config_dict.get('enviar_logs'),
                                job_config_dict.get('enviar_logs_debug'),
                                f'Falha ao enviar dados compra física para a api - '
                                f'tipo {type(response)}: {str(response)}',
                                LogType.ERROR,
                                'COLETA_DADOS_COMPRA_FISICA')
            else:
                send_log(
                    job_config_dict.get('job_name'),
                    job_config_dict.get('enviar_logs'),
                    job_config_dict.get('enviar_logs_debug'),
                    f'Nao existem vendas a serem enviadas no momento',
                    LogType.WARNING,
                    'COLETA_DADOS_COMPRA_FISICA')

        except Exception as e:
            send_log(
                job_config_dict.get('job_name'),
                job_config_dict.get('enviar_logs'),
                job_config_dict.get('enviar_logs_debug'),
                f'Erro durante execucao do job: {str(e)}',
                LogType.ERROR,
                'COLETA_DADOS_COMPRA_FISICA')
            raise e


def query_compras_erp(job_config_dict: dict, db_config: DatabaseConfig):
    """
    Consulta as vendas para atualizar no banco de dados
    Args:
        job_config_dict: Configuração do job
        db_config: Configuracao do banco de dados

    Returns:
        Lista de vendas para atualizar
    """
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()

    try:
        # monta query com EXISTS e NOT EXISTS
        # verificar se já possui WHERE
        newsql = utils.final_query(db_config)
        if src.print_payloads:
            print(newsql)
        cursor.execute(newsql)
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        results = list(dict(zip(columns, row)) for row in rows)
        cursor.close()
        conn.close()

        compras = []
        if len(results) > 0:
            compras = compra_dict(results)
        return compras
    except Exception as ex:
        send_log(
            job_config_dict.get('job_name'),
            job_config_dict.get('enviar_logs'),
            job_config_dict.get('enviar_logs_debug'),
            f' Erro ao consultar vendas no banco semaforo: {str(ex)}',
            LogType.ERROR,
            'COLETA_DADOS_COMPRA_FISICA')
        if src.exibir_interface_grafica:
            raise


def compra_dict(compras):
    lista = []
    aux = []

    for row in compras:
        dicio = {}
        if str(row["codigo_externo"]) not in aux:
            aux.append(str(row["codigo_externo"]))
            dicio["codigo_externo"] = str(row["codigo_externo"])
            dicio["codigo_parceiro"] = str(row["codigo_parceiro"])
            dicio["cpf_comprador"] = str(row["cpf_comprador"])
            dicio["data_compra"] = row["data_compra"].strftime('%d/%m/%Y %H:%M:%S')
            dicio["valor_compra"] = float(row["valor_compra"])
            dicio["compras_itens"] = []
            lista.append(dicio)

        dicio2 = {"codigo_sku": str(row["codigo_sku"]),
                  "nome_sku": str(row["nome_sku"]),
                  "valor_sku": float(row["valor_sku"]),
                  "quantidade": int(row["quantidade"]),
                  "valor_total": float(row["valor_total"])}

        for a in range(len(lista)):
            if str(row["codigo_externo"]) == lista[a]["codigo_externo"]:
                lista[a]["compras_itens"].append(dicio2)
                break
    return lista


def validate_response_compras(response, db_config, job_config_dict):
    if response is not None:
        conexao = database.Connection(db_config)
        conn = conexao.get_conect()
        cursor = conn.cursor()

        # Percorre todos os registros
        for item in response:
            identificador = item.identificador
            identificador2 = item.identificador2
            if item.sucesso == 1 or item.sucesso == 'true':
                try:
                    cursor.execute(queries.get_insert_update_semaphore_command(db_config.db_type),
                                   queries.get_command_parameter(db_config.db_type,
                                                                 [identificador, identificador2,
                                                                  IntegrationType.COLETA_DADOS_COMPRA.value,
                                                                  'SUCESSO']))
                    # atualizados.append(response['identificador'])
                except Exception as e:
                    send_log(
                        job_config_dict.get('job_name'),
                        job_config_dict.get('enviar_logs'),
                        job_config_dict.get('enviar_logs_debug'),
                        f'Erro ao atualizar Compra do kdm: {item.identificador}, Erro: {str(e)}',
                        LogType.ERROR,
                        f'{item.identificador}-{item.identificador2}')
            else:
                send_log(
                    job_config_dict.get('job_name'),
                    job_config_dict.get('enviar_logs'),
                    job_config_dict.get('enviar_logs_debug'),
                    f'Erro ao atualizar Compra para o sku: {identificador}, {item.Message}',
                    LogType.WARNING,
                    f'{item.identificador}-{item.identificador2}')

        cursor.close()
        conn.commit()
        conn.close()
