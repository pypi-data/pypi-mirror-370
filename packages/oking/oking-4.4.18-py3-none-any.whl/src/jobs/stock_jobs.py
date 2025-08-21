import logging
import src.database.connection as database
import src.database.utils as utils
import src.api.api_mplace as api_Mplace
from src.database.queries import IntegrationType
from src.jobs.system_jobs import OnlineLogger
from src.database.utils import DatabaseConfig
import src.api.okinghub as api_okHUB
import src.api.okvendas as api_okVendas
from src.api import slack
from src.database import queries
import src
from threading import Lock

from src.jobs.utils import executa_comando_sql
from src.log_types import LogType

logger = logging.getLogger()
send_log = OnlineLogger.send_log
lock = Lock()


def job_send_stocks(job_config: dict):
    """
    Job para realizar a atualização dos estoques padrão
    Args:
        job_config: Configuração do job
    """
    with lock:
        global depositoMplace
        global unidade_distribuicao
        db_config = utils.get_database_config(job_config)
        # Exibe mensagem monstrando que a Thread foi Iniciada
        logger.info(f'==== THREAD INICIADA -job: ' + job_config.get('job_name'))
        # LOG de Inicialização do Método - Para acompanhamento de execução
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Estoque - Iniciado',
            LogType.EXEC,
            'ESTOQUE')
        # Executa o Comando da Semaforo Antes do Query Principal
        if job_config['executar_query_semaforo'] == 'S':
            logger.info(f'Executando a query semáforo')
            executa_comando_sql(db_config, job_config)

        # Executa a query Principal
        logger.info(f'Executando a query principal')
        stocks = query_stocks_erp(job_config, db_config)

        # atualizados = []
        if stocks is not None and len(stocks) or 0 > 0:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Total de estoques a serem atualizados: {len(stocks)}',
                LogType.INFO,
                'ATUALIZACAO_ESTOQUE')

            api_stocks = []
            for stock in stocks:
                try:
                    # time.sleep(1)
                    if api_stocks.__len__() < 50:
                        api_stocks.append(stock)
                    else:
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Enviando Pacote: {api_stocks.__len__()}',
                            LogType.INFO,
                            'ESTOQUE')
                        if src.client_data['operacao'].lower().__contains__('okvendas'):
                            response = api_okVendas.send_stocks(api_stocks)
                            unidade_distribuicao = api_stocks[0]['unidade_distribuicao']
                        elif src.client_data['operacao'].lower().__contains__('mplace'):
                            response = api_Mplace.send_stocks_mplace(api_stocks)
                            depositoMplace = api_stocks[0]['dc_code']  # Procurar maneira de fazer get do deposito 9643 1704
                        else:
                            response = api_okHUB.send_stocks_hub(api_stocks)

                        api_stocks = []
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Tratando retorno',
                            LogType.INFO,
                            'ESTOQUE')
                        validade_response_stocks(response, db_config, job_config)

                except Exception as e:
                    send_log(job_config.get('job_name'),
                             job_config.get('enviar_logs'),
                             job_config.get('enviar_logs_debug'),
                             f'Erro genérico ao atualizar o estoque, Erro: {str(e)}',
                             LogType.ERROR,
                             'ESTOQUE')

            # Se ficou algum sem processa
            if api_stocks.__len__() > 0:
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Enviando Pacote: {api_stocks.__len__()}',
                    LogType.INFO,
                    'ESTOQUE')
                if src.client_data['operacao'].lower().__contains__('okvendas'):
                    response = api_okVendas.send_stocks(api_stocks)
                    unidade_distribuicao = api_stocks[0]['unidade_distribuicao']
                elif src.client_data['operacao'].lower().__contains__('mplace'):
                    response = api_Mplace.send_stocks_mplace(api_stocks)
                    depositoMplace = api_stocks[0]['dc_code']  # Procurar maneira de fazer get do deposito
                else:
                    response = api_okHUB.send_stocks_hub(api_stocks)
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Tratando retorno',
                    LogType.INFO,
                    'ESTOQUE')
                validade_response_stocks(response, db_config, job_config)
        else:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Nao ha produtos para atualizar estoque no momento',
                LogType.WARNING,
                'ESTOQUE')


def query_stocks_erp(job_config: dict, db_config: DatabaseConfig):
    """
    Consulta no banco de dados os estoques pendentes de atualização padrão
    Args:
        job_config: Configuração do job
        db_config: Configuração do banco de dados

    Returns:
    Lista de estoques para realizar a atualização
    """
    stocks = None
    if db_config.sql is None or db_config.sql == '':
        slack.register_warn("Query estoque de produtos nao configurada!")
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Query estoque de produtos nao configurada',
            LogType.WARNING,
            'ESTOQUE')
    else:
        try:
            # monta query com EXISTS e NOT EXISTS
            # verificar se já possui WHERE
            newsql = utils.final_query(db_config)
            conexao = database.Connection(db_config)
            conn = conexao.get_conect()
            cursor = conn.cursor()

            print("========================================")
            if src.print_payloads:
                print(newsql)
            print("=== Executando Query PRINCIAPL ")
            print("========================================")

            cursor.execute(newsql.lower().replace('#v', ','))

            print("========================================")
            print("=== RETORNOU DO BANCO ")
            print("========================================")
            rows = cursor.fetchall()
            # print(rows)
            columns = [col[0].lower() for col in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]

            cursor.close()
            conn.close()
            stocks = []
            if len(results) > 0:
                stocks = stock_dict(results)

        except Exception as ex:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'{str(ex)}', LogType.ERROR,
                'ESTOQUE')
            if src.exibir_interface_grafica:
                raise ex
            else:
                logger.error(f'Falha na conexão com o bando de dados: {str(ex)}')

    return stocks


def stock_dict(stocks):
    lista = []
    for row in stocks:
        if src.client_data['operacao'].lower().__contains__('mplace'):
            pdict = {
                'sku_seller_id': str(row['sku']),
                'variation_option_id': int(row['variation_id']),
                'dc_code': str(row['deposito']),
                'quantity': int(row['quantidade']),
                'deactivation_date': ""
            }
        elif src.client_data['operacao'].lower().__contains__('okvendas'):
            pdict = {
                'unidade_distribuicao': str(row['deposito']),
                'produto_id': '',
                'codigo_erp': str(row['sku']),
                'quantidade_total': int(row['quantidade']),
                'quantidade_reserva': 0,
                'protocolo': '',
                'parceiro': 0
            }
        else:
            pdict = {
                'sku': str(row['sku']),
                'token': str(src.client_data.get('token_oking')),
                'quantidade': int(row['quantidade']),
                'deposito': str(row['deposito'])
            }

        lista.append(pdict)

    return lista


def validade_response_stocks(response, db_config, job_config):
    logger.info("Validando o Response de Estoque")
    if response is not None:
        if src.print_payloads:
            print('Passo 1 - Response não nulo')
        conexao = database.Connection(db_config)
        conn = conexao.get_conect()
        cursor = conn.cursor()
        if src.print_payloads:
            print('Passo 2 - Get Connection do Banco')
        print(f'=== Operacao: ' + src.client_data['operacao'].lower())
        # Percorre todos os registros
        if src.client_data['operacao'].lower().__contains__('mplace'):
            for item in response:
                if src.print_payloads:
                    print('Passo 3 - Identificador ', item.sku_seller_id)
                identificador = item.sku_seller_id
                identificador2 = depositoMplace  # colocar variavel Deposito
                if item.success == 1 or item.success == 'true' or 'Estoque não atualizado - Produto não encontrado/desativado,' in item.message:
                    msgret = 'SUCESSO'
                else:
                    msgret = item.message
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f'Erro ao atualizar estoque para o sku: {identificador},'
                        f'Deposito:{identificador2} {msgret}',
                        LogType.WARNING,
                        'ESTOQUE')

                try:
                    if src.print_payloads:
                        print('Passo 4 - Antes de executar query')
                    cursor.execute(queries.get_insert_update_semaphore_command(db_config.db_type),
                                   queries.get_command_parameter(db_config.db_type, [identificador, identificador2,
                                                                                     IntegrationType.ESTOQUE.value,
                                                                                     msgret]))
                    if src.print_payloads:
                        print('Passo 5 - Após executar a query')
                    # atualizados.append(response['identificador'])
                except Exception as e:
                    send_log(job_config.get('job_name'),
                             job_config.get('enviar_logs'),
                             job_config.get('enviar_logs_debug'),
                             f'Erro ao atualizar estoque do sku: {identificador}, Deposito:{identificador2},'
                             f'Erro: {str(e)}',
                             LogType.ERROR,
                             'ESTOQUE')

        elif src.client_data['operacao'].lower().__contains__('okvendas'):
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
                        if src.print_payloads:
                            print(f"Identificadores: Identificador = {item.Identifiers}, Identificador2 = {item.Identifiers2}")
                        for identificador in item.Identifiers:
                            cursor.execute(queries.get_semaphore_command_data_sincronizacao(db_config.db_type),
                                           queries.get_command_parameter(db_config.db_type,
                                                                         [identificador, item.Identifiers2,
                                                                          IntegrationType.ESTOQUE.value,
                                                                          msgret]))
                count = cursor.rowcount
                cursor.close()
                conn.commit()
                conn.close()
                return count > 0
            except Exception as e:
                send_log(job_config.get('job_name'),
                         job_config.get('enviar_logs'),
                         job_config.get('enviar_logs_debug'),
                         f'Erro ao atualizar estoque do sku: {identificador},'
                         f'Erro: {str(e)}',
                         LogType.ERROR,
                         'ESTOQUE')

            # for item in response:
            #     identificador = item.codigo_erp
            #     identificador2 = unidade_distribuicao
            #     if item.Status == 1:
            #         msgret = 'SUCESSO'
            #     else:
            #         msgret = item.Message
            #         send_log(job_config.get('job_name'), job_config.get('enviar_logs'), True,
            #                  f'Erro ao atualizar estoque para o sku: {identificador}, {msgret}',
            #                  LogType.WARNING,
            #                  'ESTOQUE', identificador)
            #     try:
            #         cursor.execute(queries.get_insert_update_semaphore_command(db_config.db_type),
            #                        queries.get_command_parameter(db_config.db_type,
            #                                                      [identificador, identificador2,
            #                                                       IntegrationType.ESTOQUE.value,
            #                                                       msgret]))
            #     except Exception as e:
            #         send_log(job_config.get('job_name')
            #                  , job_config.get('enviar_logs')
            #                  , True
            #                  ,
            #                  f'Erro ao atualizar estoque do sku: {identificador}, Deposito:{identificador2},'
            #                  f'Erro: {str(e)}'
            #                  , LogType.ERROR
            #                  , 'ESTOQUE'
            #                  , 'ESTOQUE')

        else:
            for item in response:
                identificador = item.identificador
                identificador2 = item.identificador2
                if item.sucesso == 1 or item.sucesso == 'true':
                    msgret = 'SUCESSO'
                else:
                    msgret = item.mensagem
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f'Erro ao atualizar estoque para o sku: {identificador},'
                        f'Deposito:{identificador2} {msgret}',
                        LogType.WARNING,
                        'ESTOQUE')
                # Mesmo se der erro retira da Fila, mas grava a mensagem no Banco
                try:
                    cursor.execute(queries.get_insert_update_semaphore_command(db_config.db_type),
                                   queries.get_command_parameter(db_config.db_type, [identificador, identificador2,
                                                                                     IntegrationType.ESTOQUE.value,
                                                                                     msgret]))
                    # atualizados.append(response['identificador'])
                except Exception as e:
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f'Erro ao atualizar estoque do sku: {item.identificador}, Deposito:{item.identificador2}, '
                        f'Erro: {str(e)} ',
                        LogType.ERROR,
                        'ESTOQUE')

        cursor.close()
        conn.commit()
        conn.close()


def job_send_distribution_center(job_config: dict):
    """
    Job para enviar a unidade de distribuição
    Args:
        job_config: Configuração do job
    """
    with lock:
        db_config = utils.get_database_config(job_config)
        # Exibe mensagem monstrando que a Thread foi Iniciada
        logger.info(f'==== THREAD INICIADA -job: ' + job_config.get('job_name'))
        # LOG de Inicialização do Método - Para acompanhamento de execução
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Centro de Distribuição - Iniciado',
            LogType.EXEC,
            'ENVIA_CENTRO_DISTRIBUICAO')
        # Executa o Comando da Semaforo Antes do Query Principal
        if job_config['executar_query_semaforo'] == 'S':
            logger.info(f'Executando a query semáforo')
            executa_comando_sql(db_config, job_config)

        # Executa a query Principal
        logger.info(f'Executando a query principal')
        distribution_centers = query_distribution_center(job_config, db_config)

        if distribution_centers is not None and len(distribution_centers) or 0 > 0:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Unidades de Distribuição a serem inseridas: {len(distribution_centers)}',
                LogType.INFO,
                'ENVIA_CENTRO_DISTRIBUICAO')
            api_distribution_center = []
            for distribution_center in distribution_centers:
                try:
                    # time.sleep(1)
                    if api_distribution_center.__len__() < 50:
                        api_distribution_center.append(distribution_center)
                    else:
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Enviando Pacote: {api_distribution_center.__len__()}',
                            LogType.INFO,
                            'ENVIA_CENTRO_DISTRIBUICAO')
                        response = api_okVendas.post_send_distribution_center(api_distribution_center, job_config)
                        api_distribution_center = []
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Tratando retorno',
                            LogType.INFO,
                            'ENVIA_CENTRO_DISTRIBUICAO')
                        validade_response_distribution_center(response, db_config, job_config)

                except Exception as e:
                    send_log(job_config.get('job_name'),
                             job_config.get('enviar_logs'),
                             job_config.get('enviar_logs_debug'),
                             f'Erro genérico ao atualizar o estoque, Erro: {str(e)}',
                             LogType.ERROR,
                             'ENVIA_CENTRO_DISTRIBUICAO')

            # Se ficou algum sem processa
            if api_distribution_center.__len__() > 0:
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Enviando Pacote: {api_distribution_center.__len__()}',
                    LogType.INFO,
                    'ENVIA_CENTRO_DISTRIBUICAO')
                response = api_okVendas.post_send_distribution_center(api_distribution_center, job_config)
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Tratando retorno',
                    LogType.INFO,
                    'ENVIA_CENTRO_DISTRIBUICAO')
                validade_response_distribution_center(response, db_config, job_config)
        else:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Nao ha unidades de distribuicao para inserir no momento',
                LogType.WARNING,
                'ENVIA_CENTRO_DISTRIBUICAO')


def query_distribution_center(job_config: dict, db_config: DatabaseConfig):
    """
    Consulta no banco de dados as unidades de distribuicao
    Args:
        job_config: Configuração do job
        db_config: Configuração do banco de dados

    Returns:
    Lista de unidades de distribuicao para realizar a atualização
    """
    distribution_center = None
    if db_config.sql is None or db_config.sql == '':
        slack.register_warn("Query unidade de distribuicao nao configurada!")
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Query unidade de distribuicao nao configurada',
            LogType.WARNING,
            'ESTOQUE')
    else:
        try:
            # monta query com EXISTS e NOT EXISTS
            # verificar se já possui WHERE
            newsql = utils.final_query(db_config)
            conexao = database.Connection(db_config)
            conn = conexao.get_conect()
            cursor = conn.cursor()

            if src.print_payloads:
                print(newsql)

            cursor.execute(newsql.lower().replace('#v', ','))

            rows = cursor.fetchall()
            # print(rows)
            columns = [col[0].lower() for col in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]

            cursor.close()
            conn.close()
            distribution_center = []
            if len(results) > 0:
                distribution_center = distribution_center_dict(results)

        except Exception as ex:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'{str(ex)}',
                LogType.ERROR,
                'ENVIA_CENTRO_DISTRIBUICAO')
            if src.exibir_interface_grafica:
                raise ex
            else:
                logger.error(f'Falha na conexão com o bando de dados: {str(ex)}')

    return distribution_center


def distribution_center_dict(distribution_center):
    lista = []
    for row in distribution_center:
        pdict = {
            "nome": str(row['nome']),
            "cep": str(row['cep']),
            "codigo_externo": str(row['codigo_externo']),
            "telefone": str(row['telefone']),
            "codigo_externo_filial_faturamento": str(row['codigo_externo_filial_faturamento']),
            "cd_faturamento": bool(row['cd_faturamento']),
            "cnpj": str(row['cnpj']),
            "logradouro": str(row['logradouro']),
            "logradouro_numero": str(row['logradouro_numero']),
            "complemento": str(row['complemento']),
            "bairro": str(row['bairro']),
            "cidade": str(row['cidade']),
            "uf": str(row['uf']),
            "usuario_desativacao_id": int(row['usuario_desativacao_id']),
            "codigo_externo_reserva_estoque": str(row['codigo_externo_reserva_estoque']),
            "tipo_frete_restock": str(row['tipo_frete_restock']),
            "utiliza_estoque_fornecedor": bool(row['utiliza_estoque_fornecedor'])
        }
        lista.append(pdict)

    return lista


def validade_response_distribution_center(response, db_config, job_config):
    logger.info("Validando o Response de Unidade de Distribuição")
    if response is not None:
        if src.print_payloads:
            print('Passo 2 - Get Connection do Banco')
        print(f'=== Operacao: ' + src.client_data['operacao'].lower())
        # Percorre todos os registros

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
                    if src.print_payloads:
                        print(f"Identificadores: Identificador = {item.Identifiers}")
                    for identificador in item.Identifiers:
                        cursor.execute(queries.get_semaphore_command_data_sincronizacao(db_config.db_type),
                                       queries.get_command_parameter(db_config.db_type,
                                                                     [identificador, "",
                                                                      IntegrationType.UNIDADE_DISTRIBUICAO.value,
                                                                      msgret]))
            count = cursor.rowcount
            cursor.close()
            conn.commit()
            conn.close()
            return count > 0
        except Exception as e:
            send_log(job_config.get('job_name'),
                     job_config.get('enviar_logs'),
                     job_config.get('enviar_logs_debug'),
                     f'Erro ao atualizar estoque do sku: {identificador},'
                     f'Erro: {str(e)}',
                     LogType.ERROR,
                     'ENVIA_CENTRO_DISTRIBUICAO')

        cursor.close()
        conn.commit()
        conn.close()


def job_send_filial(job_config: dict):
    """
    Job para enviar a filial
    Args:
        job_config: Configuração do job
    """
    with lock:
        db_config = utils.get_database_config(job_config)
        # Exibe mensagem monstrando que a Thread foi Iniciada
        logger.info(f'==== THREAD INICIADA -job: ' + job_config.get('job_name'))
        # LOG de Inicialização do Método - Para acompanhamento de execução
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Filial - Iniciado',
            LogType.EXEC,
            'ENVIA_FILIAL')
        # Executa o Comando da Semaforo Antes do Query Principal
        if job_config['executar_query_semaforo'] == 'S':
            logger.info(f'Executando a query semáforo')
            executa_comando_sql(db_config, job_config)

        # Executa a query Principal
        logger.info(f'Executando a query principal')
        filiais = query_filial(job_config, db_config)

        if filiais is not None and len(filiais) or 0 > 0:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Filiais serem inseridas: {len(filiais)}',
                LogType.INFO,
                'ENVIA_FILIAL')
            api_filial = []
            for filial in filiais:
                try:
                    # time.sleep(1)
                    if api_filial.__len__() < 50:
                        api_filial.append(filial)
                    else:
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Enviando Pacote: {api_filial.__len__()}',
                            LogType.INFO,
                            'ENVIA_FILIAL')
                        response = api_okVendas.post_send_filial(api_filial, job_config)
                        api_filial = []
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Tratando retorno',
                            LogType.INFO,
                            'ENVIA_FILIAL')
                        validade_response_filial(response, db_config, job_config)

                except Exception as e:
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f'Erro genérico ao enviar filial, Erro: {str(e)}',
                        LogType.ERROR,
                        'ENVIA_FILIAL')

            # Se ficou algum sem processa
            if api_filial.__len__() > 0:
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Enviando Pacote: {api_filial.__len__()}',
                    LogType.INFO,
                    'ENVIA_FILIAL')
                response = api_okVendas.post_send_filial(api_filial, job_config)
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Tratando retorno',
                    LogType.INFO,
                    'ENVIA_FILIAL')
                validade_response_filial(response, db_config, job_config)
        else:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Nao ha unidades de distribuicao para inserir no momento',
                LogType.WARNING,
                'ENVIA_FILIAL')


def query_filial(job_config: dict, db_config: DatabaseConfig):
    """
    Consulta no banco de dados as filiais
    Args:
        job_config: Configuração do job
        db_config: Configuração do banco de dados

    Returns:
    Lista de unidades de distribuicao para realizar a atualização
    """
    filial = None
    if db_config.sql is None or db_config.sql == '':
        slack.register_warn("Query filial nao configurada!")
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Query filial nao configurada',
            LogType.WARNING,
            'FILIAL')
    else:
        try:
            # monta query com EXISTS e NOT EXISTS
            # verificar se já possui WHERE
            newsql = utils.final_query(db_config)
            conexao = database.Connection(db_config)
            conn = conexao.get_conect()
            cursor = conn.cursor()

            print("========================================")
            if src.print_payloads:
                print(newsql)
            print("=== Executando Query PRINCIAPL ")
            print("========================================")

            cursor.execute(newsql.lower().replace('#v', ','))

            print("========================================")
            print("=== RETORNOU DO BANCO ")
            print("========================================")
            rows = cursor.fetchall()
            # print(rows)
            columns = [col[0].lower() for col in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]

            cursor.close()
            conn.close()
            filial = []
            if len(results) > 0:
                filial = filial_dict(results)

        except Exception as ex:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'{str(ex)}',
                LogType.ERROR,
                'ENVIA_FILIAL')
            if src.exibir_interface_grafica:
                raise ex
            else:
                logger.error(f'Falha na conexão com o bando de dados: {str(ex)}')

    return filial


def filial_dict(filial):
    lista = []
    for row in filial:
        pdict = {
            "nome": str(row['nome']),
            "cnpj": str(row['cnpj']) if 'cnpj' in row else "",
            "codigo_externo": str(row['codigo_externo']),
            "valo_minimo_pedido": float(row['valo_minimo_pedido']) if 'valo_minimo_pedido' in row else 0,
            "restricao_mix": bool(row['restricao_mix']) if 'restricao_mix' in row else False,
            "codigo_empresa": str(row['codigo_empresa']) if 'codigo_empresa' in row else "",
        }
        lista.append(pdict)

    return lista


def validade_response_filial(response, db_config, job_config):
    logger.info("Validando o Response de Filial")
    if response is not None:
        if src.print_payloads:
            print('Passo 2 - Get Connection do Banco')
        print(f'=== Operacao: ' + src.client_data['operacao'].lower())
        # Percorre todos os registros

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
                    if src.print_payloads:
                        print(f"Identificadores: Identificador = {item.Identifiers}")
                    for identificador in item.Identifiers:
                        cursor.execute(queries.get_semaphore_command_data_sincronizacao(db_config.db_type),
                                       queries.get_command_parameter(db_config.db_type,
                                                                     [identificador, "",
                                                                      IntegrationType.FILIAL.value,
                                                                      msgret]))
            count = cursor.rowcount
            cursor.close()
            conn.commit()
            conn.close()
            return count > 0
        except Exception as e:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Erro ao enviar filial: {identificador},'
                f'Erro: {str(e)}',
                LogType.ERROR,
                'ENVIA_FILIAL')

        cursor.close()
        conn.commit()
        conn.close()
