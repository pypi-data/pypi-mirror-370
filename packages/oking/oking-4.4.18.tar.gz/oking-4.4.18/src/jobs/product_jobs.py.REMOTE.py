import logging

from src.jobs.utils import executa_comando_sql

import src.database.connection as database
import src.database.utils as utils
from src.api.entities.imposto_produto import ImpostoProduto
from src.api.entities.produto_mplace import Produto_Mplace
from src.api.entities.produto_okvendas import Produto_Okvendas
from src.api.entities.produto_parceiro_mplace import Produto_Parceiro_Mplace
from src.database.entities.product_tax import ProductTax
from src.database.queries import IntegrationType
from src.database.utils import DatabaseConfig
import src.api.okinghub as api_okHUB
from src.database import queries
import src
from typing import List
from src.jobs.system_jobs import OnlineLogger
from src.api import api_mplace as api_Mplace
from src.api import okvendas as api_OkVendas
from src.api.entities.foto_sku import Foto_Sku, Foto_Produto_Sku
import pandas as pd

logger = logging.getLogger()
send_log = OnlineLogger.send_log
from threading import Lock

lock = Lock()


def job_send_products(job_config_dict: dict):
    """
    Job para realizar a atualização de produtos
    Args:
        job_config_dict: Configuração do job
    """
    with lock:
        db_config = utils.get_database_config(job_config_dict)
        # Exibe mensagem monstrando que a Thread foi Iniciada
        logger.info(f'==== THREAD INICIADA -job: ' + job_config_dict.get('job_name'))

        # LOG de Inicialização do Método - Para acompanhamento de execução
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                 f'Produto - Iniciado', 'exec', 'envia_produto_job', 'PRODUTO')

        if db_config.sql is None:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                     f'Comando sql para criar produtos nao encontrado', 'warning', 'envia_produto_job')
            return

        if job_config_dict['executar_query_semaforo'] == 'S':
            executa_comando_sql(db_config, job_config_dict)

        if src.client_data['operacao'].lower().__contains__('mplace'):
            products = query_products_erp_mplace(job_config_dict, db_config)
            #products = query_partner_products_erp_mplace(job_config_dict, db_config)
        elif src.client_data['operacao'].lower().__contains__('okvendas'):
            produtos_repetidos = query_products(db_config)
            keys_photos_sent = {}
            photos_sku = mount_list_photos(produtos_repetidos)
            products = remove_repeat_products(produtos_repetidos)

        else:
            products = query_products_erp(job_config_dict, db_config)
        if products is not None and len(products) > 0:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                     f'Total de Produto(s) a serem atualizados: {len(products)}', 'info', 'envia_produto_job',
                     'PRODUTO')
            if src.client_data['operacao'].lower().__contains__('okvendas'):
                for prod in products:
                    try:
                        response = api_OkVendas.post_produtos([prod])

                        for res in response:
                            if res.status > 1:
                                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                                         f'Erro ao gerar produto {prod.codigo_referencia} na api okvendas. '
                                         f'Erro gerado na api: {res.message}',
                                         'warning', 'envia_produto_job', prod.codigo_referencia)
                            else:
                                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                                         f'Buscando o produto pelo {prod.codigo_referencia}', 'info', 'envia_produto_job')
                                product_info, msg = api_OkVendas.get_product_by_code(prod.codigo_referencia)

                                if product_info is None and len(msg) > 0:
                                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                                             msg, 'warning', 'envia_produto_job', prod.codigo_referencia)
                                elif product_info is not None and product_info.preco == prod.preco_estoque[0].preco and product_info.preco_lista == prod.preco_estoque[0].preco_lista and product_info.preco_custo == prod.preco_estoque[0].preco_custo:
                                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                                             f'Produto {prod.codigo_referencia} criado com sucesso', 'info', 'envia_produto_job')
                                    protocol_products(job_config_dict, prod, db_config)

                                    keys_photos_sent[(prod.codigo_erp, prod.preco_estoque[0].codigo_erp_atributo)] = ""
                                else:
                                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                                             f'Não foi atualizado o preço do produto: {prod.codigo_referencia}.',
                                             'warning', 'envia_produto_job', prod.codigo_referencia)

                    except Exception as e:
                        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                                 f'Erro durante o envio de produtos: {str(e)}', 'error', 'envia_produto_job')
                if len(photos_sku):
                    if send_photos_products(photos_sku, keys_photos_sent, 5):
                        logger.info(job_config_dict.get('job_name') + f' | Fotos dos produtos cadastradas com sucesso')
                    else:
                        print(" Erro ao cadastrar as fotos do produto")
                        logger.error(job_config_dict.get('job_name') + f' | Erro durante o cadastro das fotos dos produtos')
            else:
                api_products = []
                for product in products:

                    if api_products.__len__() < 10:
                        api_products.append(product)
                    else:
                        send_log(job_config_dict.get('job_name'), False, False
                                 , f'Enviando Pacote: {api_products.__len__()}', 'info', 'envia_produto_job'
                                 , 'PRODUTO')

                        if src.client_data['operacao'].lower().__contains__('mplace'):

                            response = api_Mplace.post_products_mplace(api_products, job_config_dict, db_config)
                            # ***********************************
                            #response = api_Mplace.post_products_mplace_partner(api_products, job_config_dict, db_config)
                        else:
                            response = api_okHUB.post_products(api_products)
                        validate_response_products(response, db_config, job_config_dict)
                        api_products = []
                        send_log(job_config_dict.get('job_name'), False, False, f'Tratando retorno', 'info'
                                 , 'envia_produto_job', 'PRODUTO')

                # Se ficou algum sem processa
                if api_products.__len__() > 0:
                    send_log(job_config_dict.get('job_name'), False, False,
                             f'Enviando Pacote: {api_products.__len__()}', 'info', 'envia_produto_job', 'PRODUTO')
                    if (src.client_data['operacao'].lower().__contains__('mplace')):

                        response = api_Mplace.post_products_mplace((src.client_data['url_api_principal']+'/api/Product')
                                                                   , api_products
                                                                   , src.client_data['token_api_integracao'])
                        # ***********************************
                        #response = api_Mplace.post_products_mplace_partner(api_products, job_config_dict, db_config)
                    else:
                        response = api_okHUB.post_products(api_products)
                    validate_response_products(response, db_config, job_config_dict)
                    send_log(job_config_dict.get('job_name'), False, False, f'Tratando retorno', 'info'
                             , 'envia_produto_job', 'PRODUTO')
        else:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True
                     , f'Nao existem produtos a serem enviados no momento', 'warning', 'envia_produto_job')


def query_products_erp(job_config_dict: dict, db_config: DatabaseConfig):
    """
    Consulta os produtos para atualizar no banco de dados
    Args:
        job_config_dict: Configuração do job
        db_config: Configuracao do banco de dados

    Returns:
        Lista de produtos para atualizar
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

        products = []
        if len(results) > 0:
            products = product_dict(results)
        return products
    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True
                 , f' Erro ao consultar produtos no banco semaforo: {str(ex)}', 'error', 'envia_produto_job')
        if src.exibir_interface_grafica:
            raise


def product_dict(products):
    lista = []
    for row in products:
        pdict = {
            'nome': str(row['nome'])
            , 'codigo_sku': str(row['codigo_sku_variacao'])
            , 'codigo_erp': str(row['codigo_erp'])
            , 'codigo_sku_principal': str(row['codigo_sku_principal'])
            , 'codigo_erp_variacao': str(row['codigo_erp_variacao'])
            , 'agrupador': str(row['agrupador'])
            , 'ean_13_variacao': str(row['ean_13_variacao'])
            , 'ean_14_variacao': str(row['ean_14_variacao'])
            , 'variacao_opcao_1': str(row['variacao_opcao_1'])
            , 'variacao_opcao_valor_1': str(row['variacao_opcao_valor_1'])
            , 'variacao_opcao_2': str(row['variacao_opcao_2'])
            , 'variacao_opcao_valor_2': str(row['variacao_opcao_valor_2'])
            , 'variacao_opcao_3': str(row['variacao_opcao_3'])
            , 'variacao_opcao_valor_3': str(row['variacao_opcao_valor_3'])
            , 'descricao': str(row['descricao'])
            , 'metakeyword': str(row['palavra_chave'])
            , 'metadescription': str(row['meta_descricao'])
            , 'quantidade_minima': int(row['quantidade_minima'])
            , 'quantidade_caixa': int(row['quantidade_caixa'])
            , 'multiplo': bool(row['multiplo'])
            , 'ativo': bool(row['ativo'])
            , 'peso': str(row['peso'])
            , 'volume': str(row['volume'])
            , 'largura': str(row['largura'])
            , 'altura': str(row['altura'])
            , 'comprimento': str(row['comprimento'])
            , 'marca_codigo': str(row['marca_codigo'])
            , 'marca_descricao': str(row['marca_descricao'])
            , 'fabricante_codigo': str(row['fabricante_codigo'])
            # , 'fabricante_descricao': str(row['fabricante_descricao'])
            , 'fabricante_link_imagem': str(row['fabricante_link_imagem'])
            , 'medida_descricao': str(row['medida_descricao'])
            , 'medida_codigo': str(row['medida_codigo'])
            , 'medida_sigla': str(row['medida_sigla'])
            , 'codigo_categoria_n1': str(row['codigo_categoria_n1'])
            , 'nome_categoria_n1': str(row['nome_categoria_n1'])
            , 'codigo_categoria_n2': str(row['codigo_categoria_n2'])
            , 'nome_categoria_n2': str(row['nome_categoria_n2'])
            , 'codigo_categoria_n3': str(row['codigo_categoria_n3'])
            , 'nome_categoria_n3': str(row['nome_categoria_n3'])
            , 'codigo_categoria_n4': str(row['codigo_categoria_n4'])
            , 'nome_categoria_n4': str(row['nome_categoria_n4'])
            , 'modelo': str(row['modelo'])
            , 'meses_garantia': int(row['meses_garantia'])
            , 'ncm': str(row['ncm'])
            , 'ipi': int(row['ipi'])
            , 'estoque_minimo': int(row['estoque_minimo'])
            , 'data_desativacao': None
            , 'data_alteracao': None
            , 'data_sincronizacao': None
            , 'tempo_adicional_entrega': int(row['tempo_adicional_entrega'])
            , 'adicional_descricao_1': str(row['adicional_descricao_1'])
            , 'adicional_conteudo_1': str(row['adicional_conteudo_1'])
            #  , 'preco_custo': int(row['preco_custo'])
            , 'token': str(src.client_data.get('token_oking'))
        }
        lista.append(pdict)

    return lista


def validate_response_single_product(identificador: str, identificador2: str, mensagem: str, db_config,
                                     job_config_dict):
    send_log(job_config_dict.get('job_name'), False, False, f'SINGLE- Inserir na Semaforo'
             , 'info', 'envia_produto_job', '')

    print(f'=========================================================================')
    print(f' identificador:{identificador},   Identificado2:{identificador2}, TIPO:{IntegrationType.PRODUTO.value}'
          f', MSG:{mensagem}')

    conexao = database.Connection(db_config)
    conn = conexao.get_conect()
    cursor = conn.cursor()

    try:
        qry = queries.get_insert_update_semaphore_command(db_config.db_type)

        cursor.execute(qry,
                       queries.get_command_parameter(db_config.db_type, [identificador, identificador2, 1, mensagem]))
    except Exception as e:
        send_log(job_config_dict.get('job_name')
                 , job_config_dict.get('enviar_logs')
                 , True
                 , f'Erro ao atualizar Produto do sku: {identificador}, Erro: {str(e)}'
                 , 'error'
                 , 'PRODUTO'
                 , f'{identificador}-{identificador2}')

    cursor.close()
    conn.commit()
    conn.close()


def query_products_erp_mplace(job_config: dict, db_config: DatabaseConfig):
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    product: List[Produto_Mplace] = []
    try:
        if db_config.is_oracle():
            conn.outputtypehandler = database.output_type_handler
        newsql = db_config.sql.lower().replace(';', '').replace('#v', ',')
        if src.print_payloads:
            print(newsql)
        cursor.execute(newsql.lower())
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        cursor.close()
        conn.close()
        if len(results) > 0:
            product = [Produto_Mplace(**p) for p in results]
    except Exception as ex:
        logger.error(f' ')
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), True,
                 f'Erro ao consultar produtos no banco: {str(ex)}', 'error', 'envia_produto_job')

    return product


def query_partner_products_erp_mplace(job_config: dict, db_config: DatabaseConfig):
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    partner_product: List[Produto_Parceiro_Mplace] = []
    try:
        if db_config.is_oracle():
            conn.outputtypehandler = database.output_type_handler
        newsql = utils.final_query(db_config)
        if src.print_payloads:
            print(newsql)
        conexao = database.Connection(db_config)
        conn = conexao.get_conect()

        cursor.execute(newsql.lower().replace(';', ''))
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        cursor.close()
        conn.close()
        if len(results) > 0:
            partner_product = [Produto_Parceiro_Mplace(**p) for p in results]
    except Exception as ex:
        logger.error(f' ')
        send_log(job_config.get('job_name'), job_config.get('enviar_logs'), True,
                 f'Erro ao consultar produtos no banco: {str(ex)}', 'error', 'envia_produto_job')
        raise ex

    return partner_product


# def insert_produto(db_config: DatabaseConfig, product_code: str):
#     db = database.Connection(db_config)
#     conn = db.get_conect()
#     cursor = conn.cursor()
#     try:
#         cursor.execute(queries.get_insert_produto_command(db_config.db_type),
#                        queries.get_command_parameter(db_config.db_type, [
#                        codigo_erp,
#                        codigo_erp_sku,
#                        data_atualizacao,
#                        data_sincronizacao,
#                        data_envio_foto]
#                         ))
#         cursor.close()
#         conn.commit()
#         conn.close()
#     except Exception as ex:
#         print(f'Erro {ex} ao atualizar a tabela do pedido {product_code}')
#         raise ex

def validate_response_products(response, db_config, job_config_dict):
    if response is None:
        return
    conexao = database.Connection(db_config)
    conn = conexao.get_conect()
    cursor = conn.cursor()

    # Percorre todos os registros
    for item in response:
        sucesso = None
        if src.client_data['operacao'].lower().__contains__('mplace'):
            identificador = item.product_code
            identificador2 = item.product_sku
            sucesso = item.sucess
        else:
            identificador = item.identificador
            identificador2 = item.identificador2
            sucesso = item.sucesso

        print(f'{item.identificador}-{item.identificador2}')
        if sucesso == 1 or sucesso == True or sucesso == 'true':
            msgret = 'SUCESSO'
            try:
                cursor.execute(queries.get_insert_update_semaphore_command(db_config.db_type),
                               queries.get_command_parameter(db_config.db_type, [identificador, identificador2,
                                                                                 IntegrationType.PRODUTO.value,
                                                                                 msgret]))
                # atualizados.append(response['identificador'])
            except Exception as e:
                send_log(job_config_dict.get('job_name')
                         , job_config_dict.get('enviar_logs')
                         , True
                         , f'Erro inserir Produto: {item.identificador}, Erro: {str(e)}'
                         , 'error'
                         , 'FOTO'
                         , f'{item.identificador}-{item.identificador2}')
        else:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                     f'Erro ao inserir Produto: {identificador}, {item.mensagem}', 'warning',
                     'FOTO', identificador)

    cursor.close()
    conn.commit()
    conn.close()


def query_products(db_config: DatabaseConfig):
    """
    Consulta os produtos contidos no banco semaforo juntamente com os dados do banco do ERP
    Args:
        db_config: Configuracao do banco de dados

    Returns:
        Lista de produtos
    """
    # abre a connection com o banco
    db = database.Connection(db_config)
    connection = db.get_conect()
    # connection.start_transaction()
    cursor = connection.cursor()

    # obtem os dados do banco
    # logger.warning(query)
    newsql = db_config.sql.replace('#v', ',')
    if src.print_payloads:
        print(newsql)
    cursor.execute(newsql)
    columns = [col[0].lower() for col in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    connection.close()

    produtos = []
    for result in results:
        produtos.append(Produto_Okvendas(result))

    return produtos


def mount_list_photos(products: List[Produto_Okvendas]):
    photos = {}

    for product in products:
        # Grouping by codigo_erp and codigo_erp_variacao
        codigo_erp = product.codigo_erp
        codigo_erp_variacao = product.preco_estoque[0].codigo_erp_atributo

        key = (codigo_erp, codigo_erp_variacao)

        if key in photos:

            length_photos = len(photos[key])

            if contains_photo(photos[key], product.imagem_base64):
                continue
            else:
                order_photo = length_photos + 1
                photo_sku = Foto_Produto_Sku(product.imagem_base64, codigo_erp, f'{codigo_erp}_{order_photo}',
                                             order_photo, False)
                photos[key].append(photo_sku)

        elif product.imagem_base64 is not None:
            # Mount photo
            photo_sku = Foto_Produto_Sku(product.imagem_base64, codigo_erp, f'{codigo_erp}_{1}', 1, True)

            photos[key] = [photo_sku]
    if src.print_payloads:
        print(photos)
    return photos


def remove_repeat_products(products: List[Produto_Okvendas]):
    product_keys = {}
    result_products = []

    for product in products:
        # Grouping by codigo_erp and codigo_erp_variacao
        codigo_erp = product.codigo_erp
        codigo_erp_variacao = product.preco_estoque[0].codigo_erp_atributo

        key = (codigo_erp, codigo_erp_variacao)

        if key in product_keys:
            continue
        else:
            product_keys[key] = ""
            result_products.append(product)

    return result_products


def contains_photo(photos: List[Foto_Sku], imagem_base64: str):
    for photo in photos:
        if photo.base64_foto == imagem_base64:
            return True
    return False


def job_product_tax(job_config_dict: dict):
    with lock:
        """
        Job para inserir o imposto do produto com as listas de imposto no banco semáforo
        Args:
            job_config_dict: Configuração do job
        """
        # Exibe mensagem monstrando que a Thread foi Iniciada
        logger.info(f'==== THREAD INICIADA -job: ' + job_config_dict.get('job_name'))

        # LOG de Inicialização do Método - Para acompanhamento de execução
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                 f'Imposto - Iniciado', 'exec', 'envia_imposto_job', 'IMPOSTO')
        db_config = utils.get_database_config(job_config_dict)
        if db_config.sql is None:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                     f'Comando sql para inserir a relação de imposto de produtos no semaforo nao encontrado', 'warning',
                     'IMPOSTO')
            return
        if job_config_dict['executar_query_semaforo'] == 'S':
            executa_comando_sql(db_config, job_config_dict)
        try:
            # 1. Obter produtos com impostos
            db_product_tax = query_list_products_tax(job_config_dict, db_config)
            if not db_product_tax:  # Verifica se é None ou lista vazia
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                        'Nenhum imposto de produto encontrado para processar',
                        'info', 'envia_imposto_job', 'IMPOSTO')
                return
            
            # 2. Inserir/Atualizar semáforo
            if not insert_update_semaphore_product_tax(job_config_dict, db_config, db_product_tax):
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                         f'Nao foi possivel inserir os impostos de produtos no banco semaforo'
                         , 'error', 'envia_imposto_job', 'IMPOSTO')
                return
            
            # 3. Preparar dados para API
            api_productstax = []
            for prod in db_product_tax:
                if not prod:  # Verifica se o produto é None
                    continue
                api_productstax.append(ImpostoProduto(
                    prod.sku_code
                    , prod.ncm
                    , prod.taxation_group
                    , prod.customer_group
                    , prod.origin_uf
                    , prod.destination_uf
                    , prod.mva_iva
                    , prod.intrastate_icms
                    , prod.interstate_icms
                    , prod.percentage_reduction_base_calculation
                    , prod.identifier
                    , prod.branch
                ))

            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                     f'Enviando impostos via api okvendas', 'info', 'envia_imposto_job', 'IMPOSTO')
            
            # 4. Enviar para API em lotes
            total = len(api_productstax)
            page = 100
            limit = min(100, total)  # Usa min() para evitar problemas
            offset = 0

            while offset < total:
                partial_taxes = api_productstax[offset:limit]
                
                response = api_OkVendas.post_product_tax(partial_taxes)
                if not response:
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                             'Nenhuma resposta da API ao enviar impostos',
                             'error', 'envia_imposto_job', 'IMPOSTO')
                    offset += page
                    limit += page
                    continue
                
                for res in response:
                    if not res or not res.identifiers:
                        continue
                        
                    identificador = next((i.identificador for i in api_productstax 
                                       if i and i.identificador == res.identifiers[0]), None)
                    if not identificador:
                        continue
                        
                    if res.status == 1:
                        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                                 f'Imposto Cadastrado/Atualizado com sucesso - Identificador: {identificador}',
                                 'warning', 'envia_imposto_job', 'IMPOSTO')
                        if protocol_semaphore_product_tax(job_config_dict, db_config, identificador):
                            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                                     f'Imposto de Produtos {identificador} protocolado no banco semaforo', 
                                     'info', 'IMPOSTO')
                        else:
                            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                                     f'Falha ao protocolar o imposto do produto {identificador}',
                                     'warning', 'envia_imposto_job', 'IMPOSTO')

                offset += page
                limit = min(offset + page, total)  # Atualiza limit para não ultrapassar o total

        except Exception as ex:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                     f'Erro durante execução do job: {str(ex)}', 
                     'error', 'envia_imposto_job', 'IMPOSTO')
            logger.exception("Erro detalhado:")  # Loga o stack trace completo


def job_product_tax_full(job_config_dict: dict):
    with lock:
        """
        Job para inserir os impostos dos produtos em lote no banco semáforo
        Args:
            job_config_dict: Configuração do job
        """
        # Exibe mensagem monstrando que a Thread foi Iniciada
        logger.info(f'==== THREAD INICIADA -job: ' + job_config_dict.get('job_name'))

        # LOG de Inicialização do Método - Para acompanhamento de execução
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                 f'Imposto - Iniciado', 'exec', 'envia_imposto_lote_job', 'IMPOSTO_LOTE')
        db_config = utils.get_database_config(job_config_dict)

        if db_config.sql is None:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                     f'Comando sql para inserir a relação de impostos dos produtos em lote no semaforo nao encontrado',
                     'warning', 'envia_imposto_lote_job', 'IMPOSTO_LOTE')
            return
        if job_config_dict['executar_query_semaforo'] == 'S':
            executa_comando_sql(db_config, job_config_dict)
        try:
            db_product_tax = query_list_products_tax(job_config_dict, db_config)
            if not insert_update_semaphore_product_tax(job_config_dict, db_config, db_product_tax):
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                         f'Nao foi possivel inserir os impostos dos produtos em lote no banco semaforo'
                         , 'error', 'envia_imposto_lote_job', 'IMPOSTO_LOTE')
                return

            # Define a lista de dicionários para construir o DataFrame
            data = []
            for product_tax in db_product_tax:
                if data.__len__() < 10000:
                    data.append({
                        'codigo_sku': product_tax.sku_code,
                        'ncm': product_tax.ncm,
                        'grupo_tributacao': product_tax.taxation_group,
                        'grupo_cliente': product_tax.customer_group,
                        'uf_origem': product_tax.origin_uf,
                        'uf_destino': product_tax.destination_uf,
                        'mva_iva': None if product_tax.mva_iva is None else round(product_tax.mva_iva, 2),
                        # arredonda para 2 casas decimais
                        'icms_intraestadual': None if product_tax.intrastate_icms is None
                        else round(product_tax.intrastate_icms, 2),  # arredonda para 2 casas decimais
                        'icms_interestadual': product_tax.interstate_icms,
                        'percentual_reducao_base_calculo': None if product_tax.percentage_reduction_base_calculation is None
                        else round(product_tax.percentage_reduction_base_calculation, 2)  # arredonda para 4 casas decimais
                        # arredonda para 4 casas decimais
                    })
                else:
                    # Cria um DataFrame a partir da lista de dicionários
                    df = pd.DataFrame(data)
                    data = []
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                             f'Enviando impostos em lote via api okvendas', 'info'
                             , 'envia_imposto_lote_job', 'IMPOSTO_LOTE')
                    response = api_OkVendas.post_product_full_tax(df)

                    if response['Status'] == 1:
                        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                                 f'Impostos em lote Cadastrados/Atualizados com sucesso na Api OkVendas'
                                 , 'warning', 'envia_imposto_lote_job', 'IMPOSTO_LOTE')
                        if protocol_semaphore_product_tax_full(job_config_dict, db_config, db_product_tax):
                            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                                     f'Impostos em lote protocolados com sucesso no banco semaforo'
                                     , 'info', 'envia_imposto_lote_job', 'IMPOSTO_LOTE')
                        else:
                            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                                     f'Falha ao protocolar os impostos dos produtos em lote no banco semaforo'
                                     , 'warning', 'envia_imposto_lote_job', 'IMPOSTO_LOTE')
                    else:
                        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                                 f'Falha ao Cadastrar/Atualizar os Impostos dos produtos em lote na Api OkVendas'
                                 , 'warning', 'envia_imposto_lote_job', 'IMPOSTO_LOTE')

            if data.__len__() > 0:
                # Cria um DataFrame a partir da lista de dicionários
                df = pd.DataFrame(data)
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                         f'Enviando impostos em lote via api okvendas', 'info'
                         , 'envia_imposto_lote_job', 'IMPOSTO_LOTE')
                response = api_OkVendas.post_product_full_tax(df)

                if response['Status'] == 1:
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                             f'Impostos em lote Cadastrados/Atualizados com sucesso na Api OkVendas'
                             , 'warning', 'envia_imposto_lote_job', 'IMPOSTO_LOTE')
                    if protocol_semaphore_product_tax_full(job_config_dict, db_config, db_product_tax):
                        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                                 f'Impostos em lote protocolados com sucesso no banco semaforo'
                                 , 'info', 'envia_imposto_lote_job', 'IMPOSTO_LOTE')
                    else:
                        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                                 f'Falha ao protocolar os impostos dos produtos em lote no banco semaforo'
                                 , 'warning', 'envia_imposto_lote_job', 'IMPOSTO_LOTE')
                else:
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                             f'Falha ao Cadastrar/Atualizar os Impostos dos produtos em lote na Api OkVendas'
                             , 'warning', 'envia_imposto_lote_job', 'IMPOSTO_LOTE')

        except Exception as ex:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True
                     , f'Erro {str(ex)}', 'error', 'envia_imposto_lote_job', 'IMPOSTO_LOTE')


def query_list_products_tax(job_config_dict: dict, db_config: DatabaseConfig) -> List[ProductTax]:
    """
        Consultar no banco semáforo a lista de produtos relacionados a lista de preço

        Args:
            job_config_dict: Configuração do job
            db_config: Configuração do banco de dados

        Returns:
        Lista de produtos relacionados ao imposto informada
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
            lists = [ProductTax(**p) for p in results]
            return lists

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                 f' Erro ao consultar imposto do produto no banco semaforo: {str(ex)}', 'error', 'IMPOSTO')

    return []


def insert_update_semaphore_product_tax(job_config_dict: dict, db_config: DatabaseConfig,
                                        lists: List[ProductTax]) -> bool:
    """
    Insere os imposts no banco semáforo
    Args:
        job_config_dict: Configuração do job
        db_config: Configuracao do banco de dados
        lists: Lista de impostos dos produtos

    Returns:
        Boleano indicando se foram inseridos 1 ou mais registros
    """
    params = [(li.identifier, ' ', IntegrationType.IMPOSTO.value, 'SUCESSO') for li in lists]

    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        for p in params:
            cursor.execute(queries.get_insert_update_semaphore_command(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, list(p)))
        count = cursor.rowcount
        cursor.close()
        conn.commit()
        conn.close()
        return count > 0

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                 f' Erro ao consultar listas de impostos no banco semaforo: {str(ex)}', 'error', 'IMPOSTO')

    return False


def protocol_products(job_config_dict: dict, product, db_config: DatabaseConfig) -> None:
    """
    Protocola no banco semaforo os produtos que foram enviados para a api okvendas
    Args:
        job_config_dict: Configuração do job
        product: produto enviado para a api okvendas
        db_config: Configuracao do banco de dados
    """

    if product is None:
        return
    db = database.Connection(db_config)
    connection = db.get_conect()
    cursor = connection.cursor()
    try:
        dados_produto = [product.codigo_erp, product.preco_estoque[0].codigo_erp_atributo]
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                 f'Protocolando codigo_erp {dados_produto[0]} sku {dados_produto[1]}', 'info', 'PRODUTO')
        cursor.execute(queries.get_product_protocol_command(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type, dados_produto))
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                 f'Linhas afetadas {cursor.rowcount}', 'info', 'PRODUTO')
    except Exception as e:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                 f'Erro ao protocolar sku {product["codigo_erp_sku"]}: {str(e)}', 'error', 'PRODUTO')
    cursor.close()
    connection.commit()
    connection.close()


def send_photos_products(photos_sku: dict, keys_photos_sent: dict, limit_photos_sent: int):
    count_success = 0
    list_photos = []
    for photo_key in photos_sku:

        if photo_key in keys_photos_sent:
            list_photo = photos_sku[photo_key]

            for photo in list_photo:
                if (len(list_photos) + 1) <= limit_photos_sent:
                    list_photos.append(photo)

                if len(list_photos) == limit_photos_sent:
                    success = api_OkVendas.put_photos_sku(list_photos)
                    if not success:
                        return success
                    else:
                        count_success = count_success + 1
                        list_photos = []

    if 0 < len(list_photos) <= 50:
        return api_OkVendas.put_photos_sku(list_photos)

    return count_success > 0 if True else False


def protocol_semaphore_product_tax(job_config_dict: dict, db_config: DatabaseConfig, identifier: str) -> bool:
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        if identifier is not None:
            cursor.execute(queries.get_semaphore_command_data_sincronizacao(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, [identifier, ' ',
                                                                             IntegrationType.IMPOSTO.value,
                                                                             'SUCESSO', ]))
        count = cursor.rowcount
        cursor.close()
        conn.commit()
        conn.close()
        return count > 0

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                 f' Erro ao protocolar imposto do produto no banco semaforo: {str(ex)}', 'error', 'IMPOSTO')


def protocol_semaphore_product_tax_full(job_config_dict: dict, db_config: DatabaseConfig,
                                        lists: List[ProductTax]) -> bool:
    """
    protocola os impostos em lote no banco semáforo
    Args:
        job_config_dict: Configuração do job
        db_config: Configuracao do banco de dados
        lists: Lista de impostos dos produtos

    Returns:
        Boleano indicando se foram inseridos 1 ou mais registros
    """
    params = [(li.identifier, IntegrationType.IMPOSTO.value) for li in lists]

    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        for p in params:
            cursor.execute(queries.get_protocol_semaphore_id3_command(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, list(p)))
        count = cursor.rowcount
        cursor.close()
        conn.commit()
        conn.close()
        return count > 0

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                 f' Erro ao protocolar as listas de impostos em lote no banco semaforo: {str(ex)}', 'error',
                 'IMPOSTO_LOTE')

    return False


# job_product_tax


def job_send_related_product(job_config_dict: dict):
    with lock:
        """
        Job para enviar produto relacionado no banco semáforo
        Args:
            job_config_dict: Configuração do job
        """
        # Exibe mensagem monstrando que a Thread foi Iniciada
        logger.info(f'==== THREAD INICIADA -job: ' + job_config_dict.get('job_name'))

        # LOG de Inicialização do Método - Para acompanhamento de execução
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                 f'Produto Relacionado - Iniciado', 'exec', 'envia_produto_relacionado_job', 'PRODUTO_RELACIONADO')
        db_config = utils.get_database_config(job_config_dict)
        try:
            produtos = query_associated_product(job_config_dict, db_config)
            produtos_list_dict = []
            if len(produtos) > 0:
                produtos_list_dict = associated_product(produtos, 2)
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                     f'Enviando produtos relacionados via api okvendas', 'info'
                     , 'envia_produto_relacionado_job', 'PRODUTO_RELACIONADO')
            for produto in produtos_list_dict:
                response = api_OkVendas.send_associated_product(produto)
                if protocol_semaphore_associated_product(job_config_dict, db_config, response,
                                                         IntegrationType.PRODUTO_RELACIONADO.value):
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                             f'Produto relacionado protocolado com sucesso no banco semaforo'
                             , 'info', 'envia_produto_relacionado_job', 'PRODUTO_RELACIONADO')
                else:
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                             f'Falha ao protocolar o produto relacionado no banco semaforo'
                             , 'warning', 'envia_produto_relacionado_job', 'PRODUTO_RELACIONADO')
        except Exception as ex:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True
                     , f'Erro {str(ex)}', 'error', 'envia_produto_relacionado_job', 'PRODUTO_RELACIONADO')


def job_send_crosselling_product(job_config_dict: dict):
    with lock:
        """
        Job para enviar produto crosselling no banco semáforo
        Args:
            job_config_dict: Configuração do job
        """
        # Exibe mensagem monstrando que a Thread foi Iniciada
        logger.info(f'==== THREAD INICIADA -job: ' + job_config_dict.get('job_name'))

        # LOG de Inicialização do Método - Para acompanhamento de execução
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                 f'Produto Crosselling - Iniciado', 'exec', 'envia_produto_crosselling_job', 'PRODUTO_CROSSELLING')
        db_config = utils.get_database_config(job_config_dict)
        try:
            produtos = query_associated_product(job_config_dict, db_config)
            produtos_list_dict = []
            if len(produtos) > 0:
                produtos_list_dict = associated_product(produtos, 3)
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                     f'Enviando produtos crosselling via api okvendas', 'info'
                     , 'envia_produto_crosselling_job', 'PRODUTO_CROSSELLING')
            for produto in produtos_list_dict:
                response = api_OkVendas.send_associated_product(produto)
                if protocol_semaphore_associated_product(job_config_dict, db_config, response,
                                                         IntegrationType.PRODUTO_CROSSELLING.value):
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                             f'Produto crosselling protocolado com sucesso no banco semaforo'
                             , 'info', 'envia_produto_crosselling_job', 'PRODUTO_CROSSELLING')
                else:
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                             f'Falha ao protocolar o produto crosselling no banco semaforo'
                             , 'warning', 'envia_produto_crosselling_job', 'PRODUTO_CROSSELLING')
        except Exception as ex:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True
                     , f'Erro {str(ex)}', 'error', 'envia_produto_crosselling_job', 'PRODUTO_CROSSELLING')


def query_associated_product(job_config_dict: dict, db_config: DatabaseConfig):
    """
        Consultar no banco semáforo a lista de produtos relacionados a lista de preço

        Args:
            job_config_dict: Configuração do job
            db_config: Configuração do banco de dados

        Returns:
        Lista de produtos relacionados
        """
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
        return results
    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                 f' Erro ao consultar produtos: {str(ex)}', 'error',
                 f'{job_config_dict.get("job_name").replace("_", " ").replace("job", "").upper()}')

    return []


def associated_product(products, relation_type):
    lista_body = []
    aux = []

    for i in products:
        dicio = {}
        if i["sku_principal"] not in aux:
            aux.append(i["sku_principal"])
            dicio["sku_principal"] = i["sku_principal"]
            dicio["tipo_relacao"] = relation_type
            dicio["produtos_associados"] = []
            lista_body.append(dicio)

        dicio2 = {"sku_associado": i["sku_associado"],
                  "ordem": i["ordem"]
                  }
        for a in range(len(lista_body)):
            if i["sku_principal"] == lista_body[a]["sku_principal"]:
                lista_body[a]["produtos_associados"].append(dicio2)
                break
    return lista_body


def protocol_semaphore_associated_product(job_config_dict: dict, db_config: DatabaseConfig, response,
                                          integration_type) -> bool:
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
                                   queries.get_command_parameter(db_config.db_type, [identificador, ' ',
                                                                                     integration_type,
                                                                                     msgret]))
        count = cursor.rowcount
        cursor.close()
        conn.commit()
        conn.close()
        return count > 0

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                 f' Erro ao protocolar produto no banco semaforo: {str(ex)}', 'error', 'PRODUTO')


def job_send_product_launch(job_config_dict: dict):
    with lock:
        """
        Job para enviar produto de lançamento no banco semáforo
        Args:
            job_config_dict: Configuração do job
        """
        # Exibe mensagem monstrando que a Thread foi Iniciada
        logger.info(f'==== THREAD INICIADA -job: ' + job_config_dict.get('job_name'))

        # LOG de Inicialização do Método - Para acompanhamento de execução
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                 f'Produto Lançamento - Iniciado', 'exec', 'envia_produto_lançamento_job', 'PRODUTO_LANCAMENTO')
        db_config = utils.get_database_config(job_config_dict)
        try:
            lancamentos = query_product_launch(job_config_dict, db_config)

            send_log(job_config_dict.get('job_name'), False, False,
                     f'Enviando Pacote: {lancamentos.__len__()}', 'info', 'PRODUTO_LANCAMENTO', '')
            response = api_OkVendas.send_product_launch(lancamentos)

            send_log(job_config_dict.get('job_name'), False, False, f'Tratando retorno', 'info',
                     'PRODUTO_LANCAMENTO', '')
            if protocol_semaphore_associated_product(job_config_dict, db_config, response,
                                                     IntegrationType.PRODUTO_LANCAMENTO.value):
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                         f'Produto lancamento protocolado com sucesso no banco semaforo'
                         , 'info', 'envia_produto_lancamento_job', 'PRODUTO_LANCAMENTO')
            else:
                send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                         f'Falha ao protocolar o produto lancamento no banco semaforo'
                         , 'warning', 'envia_produto_lancamento_job', 'PRODUTO_LANCAMENTO')

        except Exception as ex:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True
                     , f'Erro {str(ex)}', 'error', 'envia_produto_lancamento_job', 'PRODUTO_LANCAMENTO')


def query_product_launch(job_config_dict: dict, db_config: DatabaseConfig):
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
        lancamentos = []
        if len(results) > 0:
            lancamentos=(launch_dict(results))
        return lancamentos
    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                 f' Erro ao consultar produtos: {str(ex)}', 'error',
                 f'{job_config_dict.get("job_name").replace("_", " ").replace("job", "").upper()}')

    return []


def launch_dict(releases):
    lista = []
    for launch in releases:
        ldict = {
            "codigo_erp": str(launch["codigo_erp"]),
            "data_lancamento": str(launch["data_lancamento"]) if launch["data_lancamento"] is not None else ''
        }
        lista.append(ldict)
    return lista


def protocol_semaphore_product_launch(job_config_dict: dict, db_config: DatabaseConfig, response) -> bool:
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
                                                                  IntegrationType.PRODUTO_LANCAMENTO.value,
                                                                  msgret]))
        count = cursor.rowcount
        cursor.close()
        conn.commit()
        conn.close()
        return count > 0

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                 f' Erro ao protocolar lançamento do produto no banco semaforo: {str(ex)}', 'error',
                 'PRODUTO_LANCAMENTO')


def job_send_showcase_product(job_config_dict: dict):
    with lock:
        """
            Job para enviar produto vitrine no banco semáforo
            Args:
                job_config_dict: Configuração do job
            """
        # Exibe mensagem monstrando que a Thread foi Iniciada
        logger.info(f'==== THREAD INICIADA -job: ' + job_config_dict.get('job_name'))

        # LOG de Inicialização do Método - Para acompanhamento de execução
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                 f'Produto Vitrine - Iniciado', 'exec', 'envia_produto_vitrine_job', 'PRODUTO_VITRINE')
        db_config = utils.get_database_config(job_config_dict)
        try:
            produtos_vitrine = query_showcase_product(job_config_dict, db_config)

            send_log(job_config_dict.get('job_name'), False, False,
                     f'Enviando Pacote: {produtos_vitrine.__len__()}', 'info', 'PRODUTO_VITRINE', '')
            for produto in produtos_vitrine:
                response = api_OkVendas.send_showcase_product(produto)
                send_log(job_config_dict.get('job_name'), False, False, f'Tratando retorno', 'info',
                         'PRODUTO_VITRINE', '')
                if protocol_semaphore_showcase_product(job_config_dict, db_config, response, produto):
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                             f'Produto vitrine protocolado com sucesso no banco semaforo'
                             , 'info', 'envia_produto_vitrine_job', 'PRODUTO_VITRINE')
                else:
                    send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), False,
                             f'Falha ao protocolar o produto lancamento no banco semaforo'
                             , 'warning', 'envia_produto_vitrine_job', 'PRODUTO_VITRINE')

        except Exception as ex:
            send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True
                     , f'Erro {str(ex)}', 'error', 'envia_produto_vitrine_job', 'PRODUTO_VITRINE')


def query_showcase_product(job_config_dict: dict, db_config: DatabaseConfig):
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
        vitrines = []
        if len(results) > 0:
            vitrines = (showcase_dict(results))
            return vitrines

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                 f' Erro ao consultar vitrine de produtos: {str(ex)}', 'error',
                 'PRODUTO_VITRINE')
        raise ex

    return []


def protocol_semaphore_showcase_product(job_config_dict: dict, db_config: DatabaseConfig, response, produto):
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
                                                                 [identificador, produto["area_exibicao_id"],
                                                                  IntegrationType.PRODUTO_VITRINE.value,
                                                                  msgret]))
        count = cursor.rowcount
        cursor.close()
        conn.commit()
        conn.close()
        return count > 0

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                 f' Erro ao protocolar produto vitrine no banco semaforo: {str(ex)}', 'error',
                 'PRODUTO_VITRINE')


def showcase_dict(produtos):
    aux = []
    lista = []
    for produto in produtos:
        if produto["area_exibicao_id"] not in aux:
            aux.append(produto["area_exibicao_id"])
            dicio = {
                "area_exibicao_id": produto["area_exibicao_id"],
                "produtos": []
            }
            lista.append(dicio)
        dicio2 = {
            "produto": produto["codigo_sku"],
            "ordem": produto["ordem"]
        }
        for i in range(len(lista)):
            if produto["area_exibicao_id"] == lista[i]["area_exibicao_id"]:
                lista[i]["produtos"].append(dicio2)
                break
    return lista


def query_transportadora(job_config_dict: dict, db_config: DatabaseConfig):
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
        transportadoras = []
        if len(results) > 0:
            transportadoras = (transportadora_dict(results))
            return transportadoras

    except Exception as ex:
        send_log(job_config_dict.get('job_name'), job_config_dict.get('enviar_logs'), True,
                 f' Erro ao consultar transportadoras: {str(ex)}', 'error',
                 'TRANSPORTADORA_PARA_OKVENDAS')
        raise ex

    return []

def transportadora_dict(transportadoras):
    aux = []
    lista = []
    for transportadora in transportadoras:
        if transportadora["codigo_externo"] not in aux:
            aux.append(transportadora["codigo_externo"])
            dicio = {
                "codigo_externo": transportadora["codigo_externo"]
            }
            lista.append(dicio)
    return lista