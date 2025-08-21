from datetime import datetime

import jsonpickle
import requests
from src.jobs.representative_jobs import query_list_representative

from src.jobs.client_payment_plan_jobs import query_list_client_payment_plan

from src.jobs.order_jobs import query_invoices

import src.database.connection as database
from src.database import utils
from src.database.queries import create_database, comandos_oracle, comandos_firebird
from src.database.utils import get_database_config2
from src.jobs.client_jobs import query_clients_erp, get_clients
from src.jobs.colect_job import query_colect_clients_erp
from src.jobs.deliver_jobs import query_entrega_erp
from src.jobs.photo_jobs import query_photos_erp
from src.jobs.price_jobs import query_prices_erp, query_price_lists, query_price_list_products
from src.jobs.sent_jobs import query_encaminha_erp
from src.jobs.stock_jobs import query_stocks_erp
from src.jobs.system_jobs import OnlineLogger
import logging
import src
from src.log_types import LogType
import PySimpleGUI as sg
from src.database.utils import get_database_config3
from src.jobs.product_jobs import query_products_erp, query_list_products_tax, query_product_launch, \
    query_associated_product, query_showcase_product, query_transportadora

logger = logging.getLogger()
send_log = OnlineLogger.send_log


def query_job(job_evento):
    if job_evento == 'envia_estoque_job':
        return query_stocks_erp
    elif job_evento == 'envia_produto_job':
        return query_products_erp
    elif job_evento == 'envia_preco_job':
        return query_prices_erp
    elif job_evento == 'lista_preco_job':
        return query_price_lists
    elif job_evento == 'produto_lista_preco_job':
        return query_price_list_products
    elif job_evento == 'internaliza_pedidos_job':
        return ...
    elif job_evento == 'encaminhar_entrega_job':
        return query_encaminha_erp
    elif job_evento == 'internaliza_pedidos_pagos_job':
        return ...
    elif job_evento == 'internaliza_pedidos_b2b_job':
        return ...
    elif job_evento == 'internaliza_pedidos_pagos_b2b_job':
        return ...
    elif job_evento == 'envia_cliente_job':
        if src.client_data['operacao'].lower().__contains__('okvendas'):
            return get_clients
        return query_clients_erp
    elif job_evento == 'coleta_dados_cliente_job':
        return query_colect_clients_erp
    elif job_evento == 'envia_notafiscal_job':
        return query_invoices
    elif job_evento == 'envia_notafiscal_semfila_job':
        return query_invoices
    elif job_evento == 'entregue_job':
        return query_encaminha_erp
    elif job_evento == 'envia_foto_job':
        return query_photos_erp
    elif job_evento == 'envia_plano_pagamento_cliente_job':
        return query_list_client_payment_plan
    elif job_evento == 'envia_imposto_job':
        return query_list_products_tax
    elif job_evento == 'envia_imposto_lote_job':
        return query_list_products_tax
    elif job_evento == 'envia_representante_job':
        return query_list_representative
    elif job_evento == 'integra_cliente_aprovado_job':
        return ...
    elif job_evento == 'envia_produto_relacionado_job':
        return query_associated_product
    elif job_evento == 'envia_produto_crosselling_job':
        return query_associated_product
    elif job_evento == 'envia_produto_lancamento_job':
        return query_product_launch
    elif job_evento == 'envia_produto_vitrine_job':
        return query_showcase_product
    elif job_evento == 'envia_tranportadora_fob_job':
        return query_transportadora


def realizar_operacao(job_config_dict: dict, job_nome: str):
    try:
        db_config = utils.get_database_config(job_config_dict)
        executa_query = query_job(job_nome)
        lines = executa_query(job_config_dict, db_config)
        send_log(
            job_nome,
            src.client_data.get('enviar_logs'),
            True,
            f'Validando {job_nome}',
            LogType.INFO,
            f'valida {job_nome}')
        return lines.__len__()

    except Exception as e:
        logger.error(f'Erro não tratado capturado: {str(e)}')
        send_log(
            'realizar_operacao',
            src.client_data.get('enviar_logs'),
            True,
            f'Erro ao Executar: {e}',
            LogType.ERROR,
            'realizar_operacao')
        raise e


def enviar_comando_operacao(shortname, tipo, status, comando, tempo, comentario, token):
    try:
        # chamar API para enviar configuração da tarefa
        dados = {'comando': comando.replace("'", "\\'"),
                 'intervalo': tempo,
                 'observacao': comentario,
                 'job': tipo,
                 'ativo': status,
                 'token': token}
        print(dados)

        response = requests.post(f"https://{shortname}.oking.openk.com.br/api/tarefa", json=dados)
        if response.json()['sucesso']:
            sg.popup('Configuração salva com sucesso')
        else:
            sg.popup_error(response.json()['mensagem'])
    except requests.ConnectionError as error:
        sg.popup_error(error)
    except Exception as e:
        sg.popup_error("Erro ao salvar configurações")


def enviar_criacao(db_config: dict):
    try:
        # coloca o tipo do banco de dados como 'oracle' para testar se está criando no banco de dados Oracle
        # db_config['db_type'] = 'oracle'
        data = get_database_config2(db_config)
        db = database.Connection(data)
        conn = db.get_conect()
        cursor = conn.cursor()
        cursor.execute(create_database(db_config['db_type']).lower())
        # Executa comandos auxiliares
        if db_config['db_type'].lower() == 'oracle':
            cursor.execute(comandos_oracle(1).lower())
            cursor.execute(comandos_oracle(2).lower())
            cursor.execute(comandos_oracle(3).lower())
            cursor.execute(comandos_oracle(4).lower())
            cursor.execute(comandos_oracle(5).lower())
            cursor.execute(comandos_oracle(6).lower())
            cursor.execute(comandos_oracle(7).lower())
            cursor.execute(comandos_oracle(8).lower())
            cursor.execute(comandos_oracle(9).lower())
            cursor.execute(comandos_oracle(10).lower())
            cursor.execute(comandos_oracle(11).lower())
            cursor.execute(comandos_oracle(12).lower())
            cursor.execute(comandos_oracle(13).lower())
            cursor.execute(comandos_oracle(14).lower())
            cursor.execute(comandos_oracle(15).lower())
            cursor.execute(comandos_oracle(16).lower())
            cursor.execute(comandos_oracle(17).lower())
            cursor.execute(comandos_oracle(18).lower())
            cursor.execute(comandos_oracle(19).lower())
            cursor.execute(comandos_oracle(20).lower())
            cursor.execute(comandos_oracle(21).lower())
            cursor.execute(comandos_oracle(22).lower())
            cursor.execute(comandos_oracle(23).lower())
            cursor.execute(comandos_oracle(24).lower())
            cursor.execute(comandos_oracle(25).lower())
            cursor.execute(comandos_oracle(26).lower())
            cursor.execute(comandos_oracle(27).lower())
            cursor.execute(comandos_oracle(28).lower())
            cursor.execute(comandos_oracle(29).lower())
            cursor.execute(comandos_oracle(30).lower())
            cursor.execute(comandos_oracle(31).lower())
            cursor.execute(comandos_oracle(32).lower())
            cursor.execute(comandos_oracle(33).lower())
        elif db_config['db_type'].lower() == 'firebird':
            cursor.execute(comandos_firebird(1).lower())
            cursor.execute(comandos_firebird(2).lower())
            cursor.execute(comandos_firebird(3).lower())
            cursor.execute(comandos_firebird(4).lower())
            cursor.execute(comandos_firebird(5).lower())
            cursor.execute(comandos_firebird(6).lower())
            cursor.execute(comandos_firebird(7).lower())
            cursor.execute(comandos_firebird(8).lower())
            cursor.execute(comandos_firebird(9).lower())
            cursor.execute(comandos_firebird(10).lower())
            cursor.execute(comandos_firebird(11).lower())
            cursor.execute(comandos_firebird(12).lower())
            cursor.execute(comandos_firebird(13).lower())
            cursor.execute(comandos_firebird(14).lower())
            cursor.execute(comandos_firebird(15).lower())
            cursor.execute(comandos_firebird(16).lower())
            cursor.execute(comandos_firebird(17).lower())
            cursor.execute(comandos_firebird(18).lower())
            cursor.execute(comandos_firebird(19).lower())
            cursor.execute(comandos_firebird(20).lower())
            cursor.execute(comandos_firebird(21).lower())
            cursor.execute(comandos_firebird(22).lower())
            cursor.execute(comandos_firebird(23).lower())
            cursor.execute(comandos_firebird(24).lower())
            cursor.execute(comandos_firebird(25).lower())
            cursor.execute(comandos_firebird(26).lower())
            cursor.execute(comandos_firebird(27).lower())
            cursor.execute(comandos_firebird(28).lower())
        logger.info('Banco de dados criado')
    except Exception as e:
        logger.error(f'Erro não tratado capturado: {str(e)}')


def testar_conexao(db_config: dict):
    data = get_database_config3(db_config)
    db = database.Connection(data)
    conn = db.get_conect()
    conn.close()


def get_logs(job_name):
    url = f'https://{src.shortname_interface}.oking.openk.com.br' \
          f'/api/consulta/log/filtros?token={src.token_interface}&nome_job={job_name}'
    try:
        response = requests.get(url)
        lista_logs = []
        if response.ok and response.text == 'Retorno sem dados!':
            return lista_logs
        elif response.ok:
            obj = jsonpickle.decode(response.content)
            i = 0
            for x in obj:
                if i == 10:
                    break
                primeiraOc = datetime.strptime(x['Primeira Ocorrência'], '%Y-%m-%d %H:%M:%S.%f')
                segundaOc = datetime.strptime(x['Última Ocorrências'], '%Y-%m-%d %H:%M:%S.%f')
                # indice = int(len(x['Mensagem'])/2)
                # msg = x['Mensagem'][:indice] + '\n' + x['Mensagem'][indice:]
                # x['Mensagem'] = msg
                lista_logs.append([x['nome_job'], x['identificador'], x['Tipo'], x['Mensagem'],
                                   x['Ocorrências'], primeiraOc, segundaOc])
                i += 1
            return lista_logs
        else:
            logger.warning(f'Sem retorno de logs {response.status_code} - {response.url}')
            return lista_logs
    except Exception as ex:
        logger.error(f'Erro ao realizar GET na api {url} - {str(ex)}')
        raise
