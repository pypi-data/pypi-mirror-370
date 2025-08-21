import json
import logging
import time
from typing import List

import jsonpickle
import requests

import src
from src.api.entities.encaminha import Encaminha
from src.api.entities.entregue import Entregue
from src.api.entities.estoque_mplace import EstoqueMplace
from src.api.entities.foto import Foto
from src.api.entities.pedido import Queue, OrderMplace, QueueMplace
from src.api.entities.preco_mplace import Preco_Mplace
from src.api.entities.produto_mplace import Produto_Mplace
from src.api.entities.produto_parceiro_mplace import Produto_Parceiro_Mplace
from src.database.queries import IntegrationType
from src.entities.invoice import Invoice
from src.entities.response import PriceResponse, StockResponse, InvoiceResponse, SentResponse, DeliverResponse
from src.jobs.photo_jobs import validade_response_photos
from src.jobs.price_jobs import send_log, validade_response_price
from src.jobs.product_jobs import validate_response_single_product
from src.log_types import LogType

logger = logging.getLogger()


def send_stocks_mplace(body: List[EstoqueMplace]) -> List[StockResponse]:
    try:
        logger.info('Dormindo 1.2s Zzz...')
        time.sleep(1.2)
        # Alterar para enviar para o Endpoint do Mplace
        # verificar se é B2B OU B2C
        if src.client_data['operacao'].lower().__contains__('b2b'):
            url = f'{src.client_data.get("url_api_principal")}/api/product/StockByDistribuitionCenter'
            headers = {'Content-type': 'application/json',
                       'Accept': 'application/json',
                       'Authorization': src.client_data.get('token_api_integracao')
                       }
        else:
            url = f'{src.client_data.get("url_api_principal")}/api/product/stock'
            headers = {'Content-type': 'application/json',
                       'Accept': 'application/json',
                       'Authorization': src.client_data.get('token_api_integracao')
                       }
        json_body = jsonpickle.encode(body, unpicklable=False)

        if src.print_payloads:
            print(json_body)
        response = requests.put(url, headers=headers, json=json.loads(json_body))
        result = [StockResponse(**t) for t in response.json()]
        return result
    except Exception as ex:
        logger.error(f'Erro ao realizar PUT na API {str(ex)}')


###############################################################

def put_prices_mplace(body: List[Preco_Mplace], db_config, job_config) -> List[PriceResponse]:
    try:
        logger.info('Dormindo 1.2s Zzz...')
        time.sleep(1.2)
        if src.client_data['operacao'].lower().__contains__('b2b'):
            headers = {'Content-type': 'application/json',
                       'Accept': 'application/json',
                       'Authorization': f'{src.client_data.get("token_api_integracao")}'
                       }
            url = f'{src.client_data.get("url_api_principal")}/api/PriceList/Items'
        else:
            url = f'{src.client_data.get("url_api_principal")}/api/preco'
            headers = {'Content-type': 'application/json',
                       'Accept': 'application/json',
                       'access-token': src.client_data.get('token_api_integracao')
                       }
        lista_body = []

        #  variavel auxiliar para verificar se já existe marketplace_scope_code cadastrado

        aux = []

        #  formata jsonbody

        for i in body:
            dicio = {}
            if (i['marketplace_scope_code'] not in aux):
                aux.append(i['marketplace_scope_code'])
                dicio['marketplace_scope_code'] = i['marketplace_scope_code']
                dicio['items'] = []
                lista_body.append(dicio)

            dicio2 = {}
            dicio2['erp_code'] = i['erp_code']
            dicio2['variation_option_id'] = i['variation_option_id']
            dicio2['sale_price'] = i['sale_price']
            dicio2['list_price'] = i['list_price']
            dicio2['st_value'] = i['st_value']
            dicio2['ipi_value'] = i['ipi_value']
            for a in range(len(lista_body)):
                if i['marketplace_scope_code'] == lista_body[a]['marketplace_scope_code']:
                    lista_body[a]['items'].append(dicio2)
                    break
            # dicio['items'] = [dicio2]
            # lista_body.append(dicio)

        #  validate response com marketplace_scope_code como identificador2

        for num in range(len(lista_body)):
            lista_aux = [lista_body[num]]
            lista_scope_code = lista_body[num]['marketplace_scope_code']
            json_body = jsonpickle.encode(lista_aux, unpicklable=False)

            # if src.print_payloads:
            print(json_body)
            response = requests.put(url, headers=headers, json=json.loads(json_body))

            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'== Preço Enviado',
                LogType.INFO,
                'PRECO'
            )

            result = [PriceResponse(**t) for t in response.json()]
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Tratando retorno',
                LogType.INFO,
                'PRECO'
            )
            validade_response_price(result, lista_scope_code, db_config, job_config)

            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'== Esperando 1 segundo',
                LogType.INFO,
                'PRECO'
            )
            time.sleep(1.2)

        return job_config['job_name']
    # json_response = response.json()

    # if len(json_response) > 0:
    #    array_response = [json_response]
    #    result_dict = response_dict(json_response)
    # return result_dict
    except Exception as ex:
        logger.error(f'Erro ao realizar PUT na API MPLACE/api/preco {str(ex)}')


###############################################################
def get_order_queue_mplace(body: dict, status) -> List[Queue]:
    logger.info('Dormindo 1.2s Zzz...')
    time.sleep(1.2)
    retqueue = []
    url_api = ""
    try:
        url_api = f'{body.get("url_api_secundaria")}/api/Order/queue/{status}'
        token = body.get('token_api_integracao')
        response = requests.get(url_api,
                                headers={'Accept': 'application/json', 'Authorization': f'{token}'},
                                params={})
        if response.ok:
            retqueue = [QueueMplace(**t) for t in response.json()]
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
    except Exception as ex:
        logger.error(f'Erro ao realizar GET na api MPLACE {url_api}' + str(ex), exc_info=True)
        raise

    return retqueue


def get_order_mplace(body: dict, pedido_oking_id) -> OrderMplace:
    logger.info('Dormindo 1.2s Zzz...')
    time.sleep(1.2)
    retorder = None
    url_api = f'{body.get("url_api_secundaria")}/api/Order/{pedido_oking_id}'
    try:
        token = body.get('token_api_integracao')
        response = requests.get(url_api,
                                headers={'Accept': 'application/json', 'Authorization': f'{token}'},
                                params={})
        if response.ok:
            obj = jsonpickle.decode(response.content)
            retorder = OrderMplace(**obj)
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
    except Exception as ex:
        logger.error(f'Erro ao realizar GET na api mplace {url_api} - {str(ex)}')
        raise ex

    return retorder


def post_invoices_mplace(order_id, invoice: Invoice) -> None | str | InvoiceResponse:
    """
    Enviar NF de um pedido para api okvendas
    Args:
        invoice: Objeto com os dados da NF
        order_id: Id do pedido que vai receber os dados da NF

    Returns:
    None se o envio for sucesso. Caso falhe, um objeto contendo status e descrição do erro
    """
    try:
        logger.info('Dormindo 1.2s Zzz...')
        time.sleep(1.2)
        # headers = {'Content-type': 'application/json',
        #            'Accept': 'application/json',
        #            'access-token': token}
        token = src.client_data.get('token_api_integracao')

        url = f'{src.client_data.get("url_api_secundaria")}/api/Order/{order_id}/invoice'

        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'Authorization': token
                   }

        jsonpickle.set_encoder_options('simplejson', use_decimal=True, sort_keys=True)
        json_invoice = jsonpickle.encode(invoice, unpicklable=False)
        # TODO ----> Melhorar solução para json_enconde com o campo amount em Decimal
        json_invoice = json_invoice.replace('"amount": null', f'"amount":{invoice.amount}')
        if src.print_payloads:
            print(json_invoice)
        print(json_invoice)
        response = requests.post(url, json=json.loads(json_invoice), headers=headers)

        if response.ok:
            return None
        else:
            # jsonReturn = f'"text":{response.text}, "status_code":{response.status_code}'
            # err = jsonpickle.decode(response.content)
            # invoice_response = InvoiceResponse(**err)
            invoice_response = response.text
            if '_okvendas' in invoice_response or '_openkuget' in invoice_response:
                invoice_response = 'Erro interno no servidor. Entre em contato com o suporte'
            return invoice_response

    except Exception as ex:
        return InvoiceResponse(IntegrationType.NOTA_FISCAL, str(ex))


def post_sent_mplace(encaminha: Encaminha, oking_id) -> None | str | SentResponse:
    try:
        logger.info('Dormindo 1.2s Zzz...')
        time.sleep(1.2)
        url = src.client_data.get('url_api_secundaria') + f'/api/Order/{oking_id}/sent'
        token = src.client_data.get('token_api_integracao')
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'Authorization': token
                   }
        jsonpickle.set_encoder_options('simplejson', sort_keys=True)
        json_sent = jsonpickle.encode(encaminha, unpicklable=False)
        json_sent = json_sent.replace('[', '').replace(']', '')
        if src.print_payloads:
            print(json_sent)
        response = requests.post(url, json=json.loads(json_sent), headers=headers)
        if response.ok:
            return None
        else:
            sent_response = response.text
            if '_okvendas' in sent_response or '_openkuget' in sent_response:
                sent_response = 'Erro interno no servidor. Entre em contato com o suporte'
            return sent_response
    except Exception as e:
        return SentResponse(3, str(e))


def post_deliver_mplace(envia: Entregue):
    logger.info('Dormindo 1.2s Zzz...')
    time.sleep(1.2)
    url = src.client_data.get('url_api_secundaria') + f'/api/Order/{envia.id[0]}/delivered'
    token = src.client_data.get('token_api_integracao')
    try:
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'Authorization': token
                   }
        jsonpickle.set_encoder_options('simplejson', sort_key=True)
        json_deliver = jsonpickle.encode(envia, unpicklable=False)
        json_deliver = json_deliver.replace('[', '').replace(']', '')
        if src.print_payloads:
            print(json_deliver)
        response = requests.post(url, json_deliver, headers=headers)
        if response.ok:
            return None
        else:
            deliver_response = response.text
            if '_okvendas' in deliver_response or '_openkuget' in deliver_response:
                deliver_response = 'Erro interno no servidor. Entre em contato com o suporte'
            return deliver_response
    except Exception as e:
        return DeliverResponse(3, str(e))


def post_photo_mplace(body: List[Foto], job_config, db_config):
    try:
        logger.info('Dormindo 1.2s Zzz...')
        time.sleep(1.2)
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'Authorization': src.client_data.get("token_api_integracao")
                   }
        url = f'{src.client_data.get("url_api_principal")}/api/Product/Photos'
        lista_body = []
        #  variavel auxiliar para verificar se já existe marketplace_scope_code cadastrado
        aux = []
        #  formata jsonbody

        for i in body:
            dicio = {}
            if (i.product_code[0] not in aux):
                aux.append(i.product_code[0])
                dicio['product_code'] = i.product_code[0]
                dicio['photos'] = []
                lista_body.append(dicio)

            dicio2 = {}
            dicio2['code'] = i.code[0]
            dicio2['name'] = i.name[0]
            dicio2['variation_option_id'] = i.variation_option_id
            dicio2['link'] = i.link
            dicio2['erp_code'] = i.erp_code[0]
            for a in range(len(lista_body)):
                if i.product_code[0] == lista_body[a]['product_code']:
                    lista_body[a]['photos'].append(dicio2)

        for fotos_produto in lista_body:
            json_body = jsonpickle.encode(fotos_produto, unpicklable=False)
            if src.print_payloads:
                print(json_body)
            # Envia a Foto para API
            response = requests.post(url, json=json.loads(json_body), headers=headers)

            logger.info(f'============ Foto enviada para API ============ ')

            if response.ok:
                for item in fotos_produto['photos']:
                    validade_response_photos(fotos_produto['product_code'], item['code'], 'SUCESSO', db_config,
                                             job_config)
            else:
                sent_response = response.text
                print(f'==== Retorno: {response.status_code}')
                if response.status_code != 500:
                    for item in fotos_produto['photos']:
                        validade_response_photos(fotos_produto['product_code'], item['code'], sent_response,
                                                 db_config, job_config)

                if '_okvendas' in sent_response or '_openkuget' in sent_response:
                    sent_response = 'Erro interno no servidor. Entre em contato com o suporte'

    except Exception as e:
        raise e


def post_products_mplace(body: List[Produto_Mplace], job_config, db_config):
    try:
        logger.info('Dormindo 1.2s Zzz...')
        time.sleep(1.2)
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'Authorization': src.client_data.get("token_api_integracao")
                   }
        url = f'{src.client_data.get("url_api_principal")}/api/Product'
        jsonpickle.set_encoder_options('simplejson', sort_keys=True)
        json_body = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(json_body)
        dados = json.loads(json_body)
        for i in range(len(dados)):

            verify = True
            if src.client_data['operacao'].lower().__contains__('b2c'):
                for j in range(i - 1):
                    if dados[i]['product_code'] == dados[j]['product_code']:
                        indice = j
                        verify = False
                        break

                if verify:
                    dados_json = {}
                    dados_json['product_code'] = dados[i]['product_code']
                    dados_json['seller_id'] = dados[i]['seller_id']
                    dados_json['name'] = dados[i]['name']
                    dados_json['description'] = dados[i]['description']
                    dados_json['model'] = dados[i]['model']
                    dados_json['marketplace_category_code'] = dados[i]['marketplace_category_code']
                    dados_json['minimum_quantity'] = dados[i]['minimum_quantity']
                    dados_json['multiple_quantity'] = dados[i]['multiple_quantity']
                    dados_json['multiple'] = 1 if dados[i]['multiple'] == 'S' else 0
                    dados_json['package_quantity'] = int(float(dados[i]['package_quantity']))
                    dados_json['manufacturer_package_quantity'] = dados[i]['manufacturer_package_quantity']
                    dados_json['cst_a'] = dados[i]['cst_a']
                    dados_json['cst_b'] = dados[i]['cst_b']
                    dados_json['cst_c'] = dados[i]['cst_c']
                    dados_json['anatel_certificate'] = dados[i]['anatel_certificate']
                    dados_json['ncm'] = dados[i]['ncm']
                    dados_json['additional_delivery_time'] = dados[i]['additional_delivery_time']
                    dados_json['months_warranty'] = dados[i]['months_warranty']
                    dados_json['active'] = 1 if dados[i]['active'] == 'S' else 0

                    dados_json['price_attributes'] = [{'sku_seller_id': dados[i]['sku_seller_id'],
                                                       'current_price': dados[i]['current_price'],
                                                       'list_price': dados[i]['list_price'],
                                                       'variation_option_id': dados[i]['variation_option_id']}]

                    dados_json['list_price'] = []

                    dados_json['manufacturer'] = {'code': dados[i]['code'], 'name': dados[i]['name']}
                    dados_json['unit_measure'] = {'initials': dados[i]['initials'],
                                                  'description': dados[i]['description_measure']}
                    dados_json['dimensions'] = {'height': dados[i]['height'], 'width': dados[i]['width'],
                                                'length': dados[i]['length'], 'weight': dados[i]['weight']}

                    dados_json['attributes'] = [{'attribute_id': dados[i]['attribute_id'],
                                                 'attribute_option_id': dados[i]['attribute_option_id']}]

                    dados_json['tabs'] = [{'tab_id': dados[i]['tab_id'], 'content': dados[i]['content']}]

                stock_attributes = {"sku_seller_id": dados[i]['sku_seller_id'], "bar_code": dados[i]['bar_code'],
                                    "variation_option_id": dados[i]['variation_option_id'],
                                    "quantity": dados[i]['quantity'], 'dimensions': {"height": dados[i]['height'],
                                                                                     "width": dados[i]['width'],
                                                                                     "length": dados[i]['length'],
                                                                                     "weight": dados[i]['weight']},
                                    "reference_code": ''}

                if verify:
                    dados_json['stock_attributes_distribution_center'] = None
                    dados_json['stock_attributes'] = [stock_attributes]
                else:
                    dados_json['stock_attributes'].append(stock_attributes)

            if src.client_data['operacao'].lower().__contains__('b2b'):
                for j in range(i):
                    if dados[i]['product_code'] == dados[j]['product_code']:
                        indice = j
                        verify = False
                        break

                if verify:
                    dados_json = {}
                    dados_json['product_code'] = dados[i]['product_code']
                    dados_json['seller_id'] = dados[i]['seller_id']
                    dados_json['name'] = dados[i]['name']
                    dados_json['description'] = dados[i]['description']
                    dados_json['model'] = dados[i]['model']
                    dados_json['marketplace_category_code'] = dados[i]['marketplace_category_code']
                    dados_json['minimum_quantity'] = dados[i]['minimum_quantity']
                    dados_json['multiple_quantity'] = dados[i]['multiple_quantity']
                    dados_json['multiple'] = 1 if dados[i]['multiple'] == 'S' else 0
                    dados_json['package_quantity'] = int(float(dados[i]['package_quantity']))
                    dados_json['manufacturer_package_quantity'] = dados[i]['manufacturer_package_quantity']
                    dados_json['cst_a'] = dados[i]['cst_a']
                    dados_json['cst_b'] = dados[i]['cst_b']
                    dados_json['cst_c'] = dados[i]['cst_c']
                    dados_json['anatel_certificate'] = dados[i]['anatel_certificate']
                    dados_json['ncm'] = dados[i]['ncm']
                    dados_json['additional_delivery_time'] = dados[i]['additional_delivery_time']
                    dados_json['months_warranty'] = dados[i]['months_warranty']
                    dados_json['active'] = 1 if dados[i]['active'] == 'S' else 0

                    dados_json['price_attributes'] = []

                    dados_json['list_price'] = [{'current_price': dados[i]['current_price'],
                                                 'list_price': dados[i]['list_price'],
                                                 'st_value': dados[i]['st_value'],
                                                 'ipi_value': dados[i]['ipi_value'],
                                                 'variation_option_id': dados[i]['variation_option_id'],
                                                 'marketplace_scope_code': dados[i]['marketplace_scope_code']}]

                    dados_json['manufacturer'] = {'code': dados[i]['code'], 'name': dados[i]['name']}
                    dados_json['unit_measure'] = {'initials': dados[i]['initials'],
                                                  'description': dados[i]['description_measure']}
                    dados_json['dimensions'] = {'height': dados[i]['height'], 'width': dados[i]['width'],
                                                'length': dados[i]['length'], 'weight': dados[i]['weight']}

                    dados_json['attributes'] = [{'attribute_id': dados[i]['attribute_id'],
                                                 'attribute_option_id': dados[i]['attribute_option_id']}]

                    dados_json['tabs'] = [{'tab_id': dados[i]['tab_id'], 'content': dados[i]['content']}]

                stock_attributes_distribution_center = {"dc_code": dados[i]['dc_code'],
                                                        "variation_option_id": dados[i]['variation_option_id'],
                                                        "quantity": dados[i]['quantity'],
                                                        "sku_seller_id": dados[i]['sku_seller_id'],
                                                        "bar_code": dados[i]['bar_code'],
                                                        'dimensions': {"height": dados[i]['height'],
                                                                       "width": dados[i]['width'],
                                                                       "length": dados[i]['length'],
                                                                       "weight": dados[i]['weight']},
                                                        "reference_code": ''}
                if verify:
                    dados_json['stock_attributes'] = None
                    dados_json['stock_attributes_distribution_center'] = [stock_attributes_distribution_center]
                else:
                    dados_json['stock_attributes_distribution_center'].append(
                        stock_attributes_distribution_center)

            if src.print_payloads:
                print("")
                print("====================")
                print(dados_json)

            response = requests.post(url, headers=headers, json=dados_json)

            if response.ok:
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Produtos Enviados com Sucesso para o Mplace',
                    LogType.INFO,
                    'PRODUTO'
                )

                validate_response_single_product(dados_json['product_code'], dados_json['product_code'], 'SUCESSO',
                                                 db_config, job_config)

                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'== Esperando 1 segundo',
                    LogType.INFO,
                    'PRODUTO'
                )
                time.sleep(1.2)
            else:
                sent_response = response.text
                if src.print_payloads:
                    print("")
                    print("====================")
                    print("==> ERRO:")
                    print(sent_response)
                    print("====================")
                    print("")
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Falha ao Enviar para o Mplace: {sent_response} ',
                    LogType.INFO,
                    'PRODUTO'
                )
                if '_okvendas' in sent_response or '_openkuget' in sent_response:
                    sent_response = 'Erro interno no servidor. Entre em contato com o suporte'

                print("============================================================")
                print("== Esperando 1 segundo")
                time.sleep(1.2)
                # return sent_response - Não Retornar cominua seguindo em frente Verificar DEPOIS
    except Exception as e:
        raise e


def post_products_mplace_partner(body: List[Produto_Parceiro_Mplace], job_config, db_config):
    try:
        logger.info('Dormindo 1.2s Zzz...')
        time.sleep(1.2)
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'Authorization': src.client_data.get("token_api_integracao")
                   }
        url = f'{src.client_data.get("url_api_principal")}/api/PartnerProducts'
        jsonpickle.set_encoder_options('simplejson', sort_keys=True)
        json_body = jsonpickle.encode(body, unpicklable=False)
        # if src.print_payloads:
        #    print(json_body)
        dados = json.loads(json_body)

        for i in range(len(dados)):
            dados_json = {}
            dados_json['product_code'] = dados[i]['product_code']
            dados_json['product_name'] = dados[i]['product_name']
            dados_json['product_description'] = dados[i]['product_description']
            dados_json['product_reference_code'] = dados[i]['product_reference_code']
            dados_json['product_model'] = dados[i]['product_model']
            dados_json['product_brand'] = dados[i]['product_brand']
            dados_json['product_minimum_quantity'] = dados[i]['product_minimum_quantity']
            dados_json['product_is_multiple'] = dados[i]['product_is_multiple']
            dados_json['product_package_quantity'] = dados[i]['product_package_quantity']
            dados_json['product_manufacturer_package_quantity'] = dados[i]['product_manufacturer_package_quantity']
            dados_json['product_multiple_quantity'] = dados[i]['product_multiple_quantity']
            dados_json['product_ncm'] = dados[i]['product_ncm']
            dados_json['product_ean'] = dados[i]['product_ean']
            dados_json['product_sku'] = dados[i]['product_sku']
            dados_json['product_sku_partner'] = dados[i]['product_sku_partner']
            dados_json['product_sku_reference_code'] = dados[i]['product_sku_reference_code']
            dados_json['product_additional_delivery_time'] = dados[i]['product_additional_delivery_time']
            dados_json['product_months_waranty'] = dados[i]['product_months_waranty']
            dados_json['product_active'] = dados[i]['product_active']

            dados_json['product_affiliate_id'] = dados[i]['product_affiliate_id']
            dados_json['cst_a'] = dados[i]['cst_a']
            dados_json['cst_b'] = dados[i]['cst_b']
            dados_json['cst_c'] = dados[i]['cst_c']
            dados_json['anatel_certificate'] = dados[i]['anatel_certificate']
            dados_json['product_manufacturer'] = {'manufacturer_code': dados[i]['manufacturer_code'],
                                                  'manufacturer_name': dados[i]['manufacturer_name']}
            dados_json['product_measurments'] = {'measurement_code': dados[i]['measurement_code'],
                                                 'measurement_unit': dados[i]['measurement_unit'],
                                                 'measurement_description': dados[i]['measurement_description']}
            dados_json['product_dimensions'] = {'height': dados[i]['height'], 'length': dados[i]['length'],
                                                'width': dados[i]['width'], 'weight': dados[i]['weight']}

            dados_json['product_category'] = dados[i]['product_category_hierarchy'][-1]

            dados_json['category_hierarchy'] = [dados[i]['category_hierarchy']]
            dados_json['product_category_hierarchy'] = dados[i]['product_category_hierarchy']
            dados_json['product_characteristics'] = [{'characteristic_code': dados[i]['characteristic_code'],
                                                      'characteristic_name': dados[i]['characteristic_name'],
                                                      'characteristic_options': [{'characteristic_option_code':
                                                                                      dados[i][
                                                                                          'characteristic_option_code'],
                                                                                  'characteristic_option_name':
                                                                                      dados[i][
                                                                                          'characteristic_option_code']}
                                                                                 ]}]

            if src.print_payloads:
                print(dados_json)

            response = requests.post(url, headers=headers, json=[dados_json])

            if response.ok:
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Produtos Enviados com Sucesso para o Mplace',
                    LogType.INFO,
                    'PRODUTO'
                )

                validate_response_single_product(dados_json['product_code'], dados_json['product_sku'], 'SUCESSO',
                                                 db_config, job_config)

                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'== Esperando 1 segundo',
                    LogType.INFO,
                    'PRODUTO'
                )
                time.sleep(1.2)
            else:
                sent_response = response.text
                if src.print_payloads:
                    print("")
                    print("====================")
                    print("==> ERRO:")
                    print(sent_response)
                    print("====================")
                    print("")
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Falha ao Enviar para o Mplace: {sent_response} ',
                    LogType.INFO,
                    'PRODUTO'
                )
                if '_okvendas' in sent_response or '_openkuget' in sent_response:
                    sent_response = 'Erro interno no servidor. Entre em contato com o suporte'

                print("============================================================")
                print("== Esperando 1 segundo")
                time.sleep(1.2)
                # return sent_response - Não Retornar cominua seguindo em frente Verificar DEPOIS
    except Exception as e:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'ERRO Enviar para o Mplace: {str(e)} ',
            LogType.INFO,
            'PRODUTO'
        )
        raise e


def post_order_erp_code_mplace(order_id, order_erp_id):
    logger.info('Dormindo 1.2s Zzz...')
    time.sleep(1.2)
    url = src.client_data.get('url_api_secundaria') + f'/api/Order/{order_id}/integrated'
    token = src.client_data.get('token_api_integracao')
    body = {"integrated": True,
            "partner_order_code": order_erp_id,
            "observation": "Pedido Internalizado no ERP"}
    try:
        data = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(data)
        response = requests.post(url, json=json.loads(data),
                                 headers={'Accept': 'application/json', 'Authorization': f'{token}'})
        if response.ok:
            return True
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
            return False
    except Exception as ex:
        logger.error(f'Erro ao realizar POST na api MPlace {url}' + str(ex), exc_info=True)
        return False


def put_order_erp_code_mplace(order_id, order_erp_id):
    logger.info('Dormindo 1.2s Zzz...')
    time.sleep(1.2)
    url = src.client_data.get('url_api_secundaria') + f'/api/Order/{order_id}/integrated'
    token = src.client_data.get('token_api_integracao')
    body = {"integrated": True,
            "partner_order_code": order_erp_id,
            "observation": "Pedido Internalizado no ERP"}
    try:
        data = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(data)
        response = requests.post(url, json=json.loads(data),
                                 headers={'Accept': 'application/json', 'Authorization': f'{token}'})
        if response.ok:
            return True
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
            return False
    except Exception as ex:
        logger.error(f'Erro ao realizar GET na api MPlace {url}' + str(ex), exc_info=True)
        return False


def put_protocol_orders_mplace(protocolo):
    logger.info('Dormindo 1.2s Zzz...')
    time.sleep(1.2)
    token = src.client_data.get('token_api_integracao')
    url = src.client_data.get('url_api_secundaria') + f'/api/Order/queue/{protocolo}'
    try:
        if src.print_payloads:
            print(protocolo)
        response = requests.put(url, json=protocolo,
                                headers={'Accept': 'application/json', 'Authorization': f'{token}'})
        if response.ok:
            return True
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
            return False
    except Exception as ex:
        logger.error(f'Erro ao protocolar pedidos na api MPlace {url}' + str(ex), exc_info=True)
        return False


def post_order_processing_mplace(order_id):
    logger.info('Dormindo 1.2s Zzz...')
    time.sleep(1.2)
    token = src.client_data.get('token_api_integracao')
    url = src.client_data.get('url_api_secundaria') + f'/api/Order/{order_id}/processing'
    try:
        if src.print_payloads:
            print(order_id)
        response = requests.post(url, json={},  # json=order_id,
                                 headers={'Content-Type': 'application/json-patch+json',
                                          'Accept': 'application/json',
                                          'Authorization': f'{token}'})
        if src.print_payloads:
            print(response.content)
        if response.ok:
            return True
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
            return False
    except Exception as ex:
        logger.error(f'Erro ao colocar o pedido em processamento no Mplace {url}' + str(ex), exc_info=True)
        return False


def post_status_processing_mplace(pedido_oking_id):
    logger.info('Dormindo 1.2s Zzz...')
    time.sleep(1.2)
    url = src.client_data.get('url_api_secundaria') + f'/api/Order/{pedido_oking_id}/processing'
    token = src.client_data.get('token_api_integracao')
    try:
        if src.print_payloads:
            print(pedido_oking_id)
        response = requests.post(url, json=pedido_oking_id,
                                 headers={'Accept': 'application/json', 'Authorization': f'{token}'})
        if response.ok:
            return True
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
            return False
    except Exception as ex:
        logger.error(f'Erro ao processar o status do pedido no Mplace {url}' + str(ex), exc_info=True)
        return False


def send_log_mplace(site_order_code, log):
    logger.info('Dormindo 1.2s Zzz...')
    time.sleep(1.2)
    url = f"{src.client_data.get('url_api_principal')}/api/Order/{site_order_code}/warning"
    token = src.client_data.get('token_api_integracao')
    header = {'Accept': 'application/json', 'Authorization': f'{token}'}
    try:
        response = requests.post(url, json=log, headers=header)
        if response.ok:
            return True
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
            return False
    except Exception as ex:
        logger.error(f'Erro ao enviar log do pedido no Mplace {url}' + str(ex), exc_info=True)
        return False
