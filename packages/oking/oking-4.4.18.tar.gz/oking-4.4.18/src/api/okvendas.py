import json
import logging
from typing import Optional, List

import jsonpickle
import requests
import pandas as pd
from src.api.entities.cliente import Cliente

import src
from src.api.entities.client_erp_code import ClienteErpCode
from src.api.entities.cliente_aprovado import ApprovedClientResponse
from src.api.entities.foto_sku import Foto_Sku
from src.api.entities.imposto_produto import ImpostoProduto
from src.api.entities.pedido import QueueOkvendas, OrderOkvendas
from src.api.entities.plano_pagamento_cliente import PlanoPagamentoCliente
from src.api.entities.preco_lista import ListaPreco
from src.api.entities.representante import Representante
from src.database.entities.representative import Representative
from src.database.queries import IntegrationType
from src.entities.invoice import InvoiceOkvendas
from src.entities.log import Log
from src.entities.product import ResponseProductByCode
from src.entities.response import InvoiceResponse, CatalogoResponse, OkvendasResponse, ListaPrecoResponse, \
    ProductTaxResponse, RepresentativeResponse, ClientResponse, OkvendasEstoqueResponse, SbyResponse, SbyResponseError
from src.jobs.system_jobs import OnlineLogger
from src.log_types import LogType

# from src.database.entities.client_payment_plan import ClientPaymentPlan

send_log = OnlineLogger.send_log


logger = logging.getLogger()


def obj_dict(obj):
    return obj.__dict__


def object_list_to_dict(obj_list: list):
    lista = []
    for obj in obj_list:
        lista.append(obj.toJSON())
    return lista


def send_stocks(body):
    logger.info("Realizando o JOB send_stocks")
    try:
        # auth = HTTPBasicAuth('teste@example.com', 'real_password')
        headers = {'Content-type': 'application/json',
                   'Accept': 'text/html',
                   'access-token': src.client_data.get('token_api_integracao')}
        url = src.client_data.get('url_api_principal') + '/catalogo/estoqueUnidadeDistribuicao'
        json_stock = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(json_stock)
        logger.info("Executando o Post na API /catalogo/estoqueUnidadeDistribuicao")
        response = requests.post(url, json=json.loads(json_stock), headers=headers)
        # result = [OkvendasEstoqueResponse(**t) for t in response.json()]
        logger.info("Pegando Objeto OkvendasResponse retornado pelo Post")
        result = [OkvendasResponse(**t) for t in response.json()]
        if response.ok:
            logger.info("Response OK")
            return result
        else:
            logger.info("Response not OK")
            if response.content is not None and response.content != '':
                return result

    except Exception as ex:
        logger.info("ERRO Durante o Post")
        logger.error(str(ex))


def post_prices(price: List):
    try:
        headers = {'Content-type': 'application/json',
                   'Accept': 'text/html',
                   'access-token': src.client_data.get('token_api_integracao')}
        url = src.client_data.get('url_api_principal') + '/catalogo/precos'
        json_prices = jsonpickle.encode(price, unpicklable=False)
        if src.print_payloads:
            print(json_prices)
        response = requests.post(url, json=json.loads(json_prices), headers=headers)
        result = [OkvendasResponse(**t) for t in response.json()]

        send_log(
            'envia_preco_job',
            False,
            False,
            f'== Preço Enviado',
            LogType.INFO,
            'PRECO'
        )
        return result

    except Exception as ex:
        logger.error(f'Erro ao realizar POST na API OkVendas /catalogo/precos {str(ex)}')
        # PriceResponse([price.codigo_erp], 3, str(ex))


def post_invoices(invoice: InvoiceOkvendas) -> Optional[InvoiceResponse]:
    """
    Enviar NF de um pedido para api okvendas
    Args:
        invoice: Objeto com os dados da NF

    Returns:
    None se o envio for sucesso. Caso falhe, um objeto contendo status e descrição do erro
    """
    try:
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'access-token': src.client_data.get('token_api_integracao')}
        url = src.client_data.get('url_api_principal') + '/pedido/faturar'
        json_invoice = jsonpickle.encode(invoice, unpicklable=False)
        if src.print_payloads:
            print(json_invoice)
        response = requests.post(url, json=json.loads(json_invoice), headers=headers)
        if response.ok:
            return None
        else:
            err = (str(response.text))
            invoice_response = InvoiceResponse(IntegrationType.NOTA_FISCAL, err)
            if '_okvendas' in invoice_response.message or '_openkuget' in invoice_response.message:
                invoice_response.message = 'Erro interno no servidor. Entre em contato com o suporte'
            return invoice_response

    except Exception as ex:
        return InvoiceResponse(IntegrationType.NOTA_FISCAL, str(ex))


def put_price_lists(body: List[ListaPreco]) -> List[ListaPrecoResponse]:
    try:
        url = f'{src.client_data.get("url_api_principal")}/catalogo/listapreco'
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'access-token': src.client_data.get('token_api_integracao')}
        json_body = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(json_body)
        response = requests.put(url, headers=headers, json=json.loads(json_body))
        if response.ok:
            res = jsonpickle.decode(response.content)
            return [ListaPrecoResponse(**r) for r in res]
        else:
            raise Exception(response.content)
    except Exception as e:
        logger.error(f'Erro ao realizar PUT /catalogo/listapreco na api okvendas {str(e)}')
        return []


def post_produtos(produtos: list):
    try:
        url = f'{src.client_data.get("url_api_principal")}/catalogo/produtos'

        json_produtos = jsonpickle.encode(produtos, unpicklable=False)
        if src.print_payloads:
            print(json_produtos)
        response = requests.post(url, json=json.loads(json_produtos), headers={
            'Content-type': 'application/json',
            'Accept': 'text/html',
            'access-token': src.client_data.get('token_api_integracao')})

        obj = jsonpickle.decode(response.content)
        result = []
        if 200 <= response.status_code <= 299:
            for res in obj:
                result.append(CatalogoResponse(**res))
        else:
            if type(obj) is list:
                for res in obj:
                    result.append(CatalogoResponse(**res))
            else:
                result.append(CatalogoResponse(**obj))

        return result
    except Exception as e:
        logger.error(f'Erro ao enviar produto para api okvendas {e}', exc_info=True)


def get_product_by_code(code) -> (ResponseProductByCode, str):
    try:
        url = f'{src.client_data.get("url_api_principal")}/catalogo/produtos?skuCode={code}'

        response = requests.get(url, headers={
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'access-token': src.client_data.get('token_api_integracao')})

        result = response.json()

        if src.print_payloads:
            print(result)

        if response.status_code == 404:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
            return None, f"{result['message']} código sku: {code}" if 'message' in result \
                else f'Não foi encontrado o produto: {code} na api okvendas'

        if response.ok:
            products = [ResponseProductByCode(**t) for t in result]
            product = products[0] if len(products) > 0 else None
            return product, None
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
            return None, result[
                'message'] if 'message' in result else f'Não foi possível consultar o produto: {code} na api okvendas'

    except Exception as e:
        logger.error(f'Erro ao buscar produto na api okvendas {e}', exc_info=True)
        return None, f'Não foi possível consultar o produto {code} na api okvendas -  Error: {str(e)}'


def post_log(log: Log) -> bool:
    try:
        if not src.is_dev:
            url = f'{src.client_data.get("url_api_principal")}/log/logIntegracao'
            headers = {
                'Content-type': 'application/json',
                'Accept': 'application/json',
                'access-token': src.client_data.get('token_api_integracao')
            }

            json_log = jsonpickle.encode([log], unpicklable=False)
            if src.print_payloads:
                print(json_log)
            response = requests.post(url, json=json.loads(json_log), headers=headers)
            if response.ok:
                return True

            return False
        else:
            return True
    except Exception:
        return False


def put_photos_sku(body):
    """
        Cadastra Fotos do SKU
        Podem ser enviadas até 50 fotos por vez.
        Args:
            body: Objeto com os dados das Fotos
        Returns:
        True se foi atualizado com Sucesso. False se não foi atualizado
    """
    url = f'{src.client_data.get("url_api_principal")}/v2/catalogo/fotos/sku'
    try:

        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'access-token': src.client_data.get('token_api_integracao')}

        json_photos = jsonpickle.encode(body, unpicklable=False)
        logger.info(f'{url} - {json_photos}')
        if src.print_payloads:
            print(json_photos)
        response = requests.put(url,
                                headers=headers,
                                json=json.loads(json_photos))
        if response.ok:
            return True
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url} - {response.text}')
            return False
    except Exception as ex:
        logger.error(f'Erro ao realizar PUT /v2/catalogo/fotos/sku na api okvendas {url}' + str(ex), exc_info=True)
        return False


def get_order_queue_okvendas(status):
    queue = []
    url = ''
    try:
        url = src.client_data.get('url_api_principal') + f'/pedido/fila/{status}'
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'access-token': src.client_data.get('token_api_integracao')}
        response = requests.get(url, headers=headers)
        if response.ok:
            queue = [QueueOkvendas(**t) for t in response.json()['fila']]
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
    except Exception as ex:
        logger.error(f'Erro ao realizar GET na api MPLACE {url}' + str(ex), exc_info=True)
        raise

    return queue


def put_protocol_order_okvendas(protocol: List[str]):
    url = ''
    try:
        token = src.client_data.get('token_api_integracao')
        url = src.client_data.get('url_api_principal') + '/pedido/fila'
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'access-token': token}
        json_protocolos = protocol
        if src.print_payloads:
            print(url, "\n", json_protocolos, "\n", headers)
        response = requests.put(url, json=json_protocolos, headers=headers)
        if response.ok:
            return True
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url} - {response.text}')
            return False
    except Exception as ex:
        logger.error(f'Erro ao protocolar pedidos na api OkVendas {url}' + str(ex), exc_info=True)
        return False


def get_order_okvendas(pedido_oking_id) -> OrderOkvendas:
    retorder = None
    if src.client_data['operacao'].lower().__contains__('b2c'):
        url = src.client_data.get('url_api_principal') + f'/pedido/{pedido_oking_id}'
    else:
        url = src.client_data.get('url_api_principal') + f'/pedidoB2B/{pedido_oking_id}'
    token = src.client_data.get('token_api_integracao')
    headers = {'Content-type': 'application/json',
               'Accept': 'application/json',
               'access-token': token}

    try:
        response = requests.get(url, headers=headers)
        if response.ok and response.status_code == 200:
            obj = jsonpickle.decode(response.content)
            retorder = OrderOkvendas(**obj)
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
    except Exception as ex:
        logger.error(f'Erro ao realizar GET na api okvendas {url} - {str(ex)}')
        raise ex

    return retorder


# def post_order_processing_okvendas(order_id):
#     token = src.client_data.get('token_api_integracao')
#     url = src.client_data.get('url_api_principal') + f'/api/Order/{order_id}/processing'
#     headers = {'Content-type': 'application/json',
#                'Accept': 'application/json',
#                'access-token': token}
#     try:
#         if src.print_payloads:
#             print(order_id)
#         response = requests.post(url, json=order_id, headers=headers)
#         if response.ok:
#             return True
#         else:
#             logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
#             return False
#     except Exception as ex:
#         logger.error(f'Erro ao colocar o pedido em processamento no Okvendas {url}' + str(ex), exc_info=True)
#         return False


def post_client_payment_plan(body: PlanoPagamentoCliente) -> (bool, dict):
    try:
        url = f'{src.client_data.get("url_api_principal")}/client/formapagamento'
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'access-token': src.client_data.get('token_api_integracao')}
        if body.formas_pagamento[0].__contains__(","):
            body.formas_pagamento = body.formas_pagamento[0].split(",")
        json_body = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(json_body)
        response = requests.post(url, headers=headers, json=json.loads(json_body))

        return response.ok, response.status_code, response.json()

    except Exception as e:
        logger.error(f'Erro ao realizar POST /client/formapagamento na api okvendas {str(e)}')


def post_product_tax(body: List[ImpostoProduto]) -> List[ProductTaxResponse]:
    try:
        url = f'{src.client_data.get("url_api_principal")}/catalogo/impostoNCM'
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'access-token': src.client_data.get('token_api_integracao')}
        json_body = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(json_body)
        response = requests.post(url, headers=headers, json=json.loads(json_body))
        result = [ProductTaxResponse(**t) for t in response.json()]
        return result
    except Exception as e:
        logger.error(f'Erro ao realizar POST /catalogo/impostoNCM na api okvendas {str(e)}')


def post_product_full_tax(df: pd.DataFrame):
    try:
        # Escreve o DataFrame para um arquivo CSV
        csv_string = df.to_csv(index=False)

        url = f'{src.client_data.get("url_api_principal")}/catalogo/impostoLoteNCM'
        headers = {
            'access-token': src.client_data.get('token_api_integracao')
        }

        # Criando objeto para o envio do arquivo
        files = {'file': ('imposto_produto_lote.csv', csv_string, 'text/csv')}
        # Upload do arquivo para uma API
        if src.print_payloads:
            print(files)
        response = requests.post(url, headers=headers, files=files)

        if response.ok:
            return response.json()
        else:
            if response.content is not None and response.content != '':
                return response.json()
    except Exception as e:
        logger.error(f'Erro ao realizar POST /catalogo/impostoLoteNCM na api okvendas {str(e)}')


def put_price_lists_products(price_list_code: str, body: str) -> bool:
    try:
        url = f'{src.client_data.get("url_api_principal")}/' \
              f'catalogo/listapreco/preco/lote?price_list_code={price_list_code}'
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'access-token': src.client_data.get('token_api_integracao')}
        json_body = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(json_body)
        response = requests.put(url, headers=headers, json=json.loads(json_body))
        return response.ok
    except Exception as e:
        logger.error(f'Erro ao realizar PUT /catalogo/listapreco/preco/lote na api okvendas {str(e)}')


def put_representative(body: List[Representante]):
    try:
        url = f'{src.client_data.get("url_api_principal")}/representante'
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'access-token': src.client_data.get('token_api_integracao')}
        json_body = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(json_body)
        response = requests.put(url, headers=headers, json=json.loads(json_body))
        if response.ok:
            # res = jsonpickle.decode(response.content)
            result = [RepresentativeResponse(**t) for t in response.json()]
            return result
    except Exception as e:
        logger.error(f'Erro ao realizar PUT /representante na api okvendas {str(e)}')


def get_approved_clients() -> ApprovedClientResponse:
    try:
        headers = {
            'access-token': src.client_data.get('token_api_integracao')
        }

        res = requests.get(f'{src.client_data.get("url_api_principal")}/cliente/pendente/parceiro?init=1&limit=100',
                           headers=headers)
        if res.ok and len(res.content) > 0:
            return ApprovedClientResponse(**res.json())

        res.raise_for_status()
    except Exception as e:
        logger.error(f'Erro ao consultar clientes aprovados {str(e)}')
        return ApprovedClientResponse()  # Retorna vazio em caso de erro


def put_client_erp_code(body) -> bool:
    try:
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'access-token': src.client_data.get('token_api_integracao')
        }

        json_client_erp_code = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(json_client_erp_code)

        response = requests.put(src.client_data.get('url_api_principal') + '/cliente/codigo',
                                headers=headers,
                                json=json.loads(json_client_erp_code))

        if response.ok:
            return True
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
            return False
    except Exception as ex:
        logger.error(f'Erro ao realizar GET na api okvendas {src.client_data.get("url_api_principal")}/cliente/codigo'
                     + str(ex), exc_info=True)
        return False


def post_clients(clients: List[Cliente]) -> List[ClientResponse]:
    url = f'{src.client_data.get("url_api_principal")}/cliente/clientes'
    headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json',
        'access-token': src.client_data.get('token_api_integracao')
    }

    try:
        payload = jsonpickle.encode(clients, unpicklable=False)
        if src.print_payloads:
            print(payload)
        response = requests.put(url, json=json.loads(payload), headers=headers)
        results = jsonpickle.decode(response.text)
        return [ClientResponse(**r) for r in results]

    except Exception as e:
        return [ClientResponse([c.cpf or c.cnpj for c in clients], 3, str(e))]


def send_associated_product(body):
    url = f'{src.client_data.get("url_api_principal")}/vitrine/produtoassociado'
    headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json',
        'access-token': src.client_data.get('token_api_integracao')
    }
    try:
        json_body = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(json_body)
        response = requests.post(url, json=json.loads(json_body), headers=headers)
        if response.ok:
            # results = jsonpickle.decode(response.text)
            return [OkvendasResponse(**r) for r in response.json()]
        else:
            logger.error(
                f'Erro ao realizar POST na api okvendas {src.client_data.get("url_api_principal")}'
                f'/vitrine/produtoassociado' + str(response.text), exc_info=True)
            return [OkvendasResponse(**r) for r in response.json()]
    except Exception as ex:
        logger.error(
            f'Erro ao realizar POST na api okvendas {src.client_data.get("url_api_principal")}/vitrine/produtoassociado'
            + str(ex), exc_info=True)
        return False


def send_product_launch(body):
    url = f'{src.client_data.get("url_api_principal")}/vitrine/lancamento'
    headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json',
        'access-token': src.client_data.get('token_api_integracao')
    }
    try:
        json_body = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(json_body)
        response = requests.post(url, headers=headers, json=json.loads(json_body))
        if response.ok:
            # results = jsonpickle.decode(response.text)
            return [OkvendasResponse(**r) for r in response.json()]
        else:
            logger.error(
                f'Erro ao realizar POST na api okvendas {src.client_data.get("url_api_principal")}/vitrine/lancamento'
                + str(response.text), exc_info=True)
            return [OkvendasResponse(**r) for r in response.json()]
    except Exception as ex:
        logger.error(
            f'Erro ao realizar POST na api okvendas {src.client_data.get("url_api_principal")}/vitrine/lancamento'
            + str(ex), exc_info=True)
        return False


def send_suggested_sale(body):
    url = f'{src.client_data.get("url_api_principal")}/vitrine/VendaSugerida'
    headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json',
        'access-token': src.client_data.get('token_api_integracao')
    }
    try:
        json_body = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(json_body)
        response = requests.post(url, headers=headers, json=json.loads(json_body))
        if response.ok:
            # results = jsonpickle.decode(response.text)
            return [OkvendasResponse(**r) for r in response.json()]
        else:
            logger.error(
                f'Erro ao realizar POST na api okvendas {src.client_data.get("url_api_principal")}'
                f'/vitrine/VendaSugerida' + str(response.json()), exc_info=True)
            return [OkvendasResponse(**r) for r in response.json()]
    except Exception as ex:
        logger.error(
            f'Erro ao realizar POST na api okvendas {src.client_data.get("url_api_principal")}/vitrine/VendaSugerida'
            + str(ex), exc_info=True)
        return False


def put_order_erp_code(order_id: int, order_erp_id: str) -> bool:
    url = src.client_data.get('url_api_principal') + '/pedido/integradoERP'
    token = src.client_data.get('token_api_integracao')
    try:
        if src.print_payloads:
            print({'id': order_id, 'codigo_erp': order_erp_id})
        response = requests.put(url, headers={'Accept': 'application/json', 'access-token': token},
                                params={'id': order_id, 'codigo_erp': order_erp_id})
        if response.ok:
            return True
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
            return False
    except Exception as ex:
        logger.error(f'Erro ao realizar GET na api okvendas {url}' + str(ex), exc_info=True)
        return False


def send_showcase_product(body):
    url = src.client_data.get('url_api_principal') + '/Vitrine/Produtos'
    header = {
        'Accept': 'application/json',
        'Content-type': 'application/json',
        'access-token': src.client_data.get('token_api_integracao')
    }
    try:
        if src.print_payloads:
            print(body)
        response = requests.post(url, headers=header, json=body)
        if response.ok:
            return [OkvendasResponse(**r) for r in response.json()]
        else:
            logger.error(
                f'Erro ao realizar POST na api okvendas {src.client_data.get("url_api_principal")}/Vitrine/Produtos'
                + str(response.json()), exc_info=True)
            return [OkvendasResponse(**r) for r in response.json()]
    except Exception as ex:
        logger.error(
            f'Erro ao realizar POST na api Okvendas {src.client_data.get("url_api_principal")}/Vitrine/Produtos'
            + str(ex), exc_info=True)
        return False


def post_sent_okvendas(body):
    url = src.client_data.get('url_api_principal') + '/pedido/encaminhar'
    header = {
        'Accept': 'application/json',
        'Content-type': 'application/json',
        'access-token': src.client_data.get('token_api_integracao')
    }
    try:
        logger.info("== Enviar para Entraga OkVendas")
        logger.info("== BODY Alterado via  jsonpickle.encode")
        json_body = jsonpickle.encode(body, unpicklable=False)

        if src.print_payloads:
            print(json_body)

        response = requests.post(url, headers=header, json=json_body)
        if response.ok:
            return None
        else:
            logger.error(
                f'Erro ao realizar POST na api okvendas {src.client_data.get("url_api_principal")}/pedido/encaminhar'
                + str(response.json()), exc_info=True)
            # return [OkvendasResponse(**r) for r in response.json()]
            return str(response.json())
    except Exception as ex:
        logger.error(
            f'Erro ao realizar POST na api Okvendas {src.client_data.get("url_api_principal")}/pedido/encaminhar'
            + str(ex), exc_info=True)
        return f'Erro ao realizar POST na api Okvendas /pedido/encaminhar {str(ex)}'


def post_deliver_okvendas(body):
    url = src.client_data.get('url_api_principal') + '/pedido/entregue'
    header = {
        'Accept': 'application/json',
        'Content-type': 'application/json',
        'access-token': src.client_data.get('token_api_integracao')
    }
    try:
        if src.print_payloads:
            print(body)
        response = requests.post(url, headers=header, json=body)
        if response.ok:
            # return [OkvendasResponse(**r) for r in response.json()]
            return None
        else:
            logger.error(
                f'Erro ao realizar POST na api okvendas {src.client_data.get("url_api_principal")}/pedido/entregue'
                + str(response.json()), exc_info=True)
            # return [OkvendasResponse(**r) for r in response.json()]
            return str(response.json())
    except Exception as ex:
        logger.error(
            f'Erro ao realizar POST na api Okvendas {src.client_data.get("url_api_principal")}/pedido/entregue'
            + str(ex), exc_info=True)
        return f'Erro ao realizar POST na api Okvendas /pedido/entregue {str(ex)}'


def post_colect_physical_shopping(body):
    url = src.client_data.get('url_api_terciario') + '/api/compraloja'
    header = {
        'Accept': 'application/json',
        'Content-type': 'application/json',
        'access-token': src.client_data.get('token_api_integracao')
    }
    try:
        if src.print_payloads:
            print(body)
        json_body = jsonpickle.encode(body, unpicklable=False)
        response = requests.post(url, headers=header, json=json.loads(json_body))
        result = jsonpickle.decode(response.content)
        if "sucesso" in result and result["sucesso"]:
            return None
        else:
            logger.error(
                f'Erro ao realizar POST na api okvendas {src.client_data.get("url_api_terciario")}api/compraloja'
                + str(response.json()), exc_info=True)
            # return [OkvendasResponse(**r) for r in response.json()]
            return str(response.json())
    except Exception as ex:
        logger.error(
            f'Erro ao realizar POST na api Okvendas {src.client_data.get("url_api_terciario")}/api/compraloja '
            + str(ex), exc_info=True)
        return f'Erro ao realizar POST na api Okvendas /api/compraloja {str(ex)}'


def post_send_order_to_okvenas(job_config_dict, body):
    url = src.client_data.get('url_api_principal') + '/pedido/insere'
    header = {
        'Accept': 'application/json',
        'Content-type': 'application/json',
        'access-token': src.client_data.get('token_api_integracao')
    }
    try:
        if src.print_payloads:
            print(body)
        json_body = jsonpickle.encode(body, unpicklable=False)
        response = requests.post(url, headers=header, json=json.loads(json_body))
        result = jsonpickle.decode(response.content)
        if src.print_payloads:
            print(result)
        if response.ok:
            return result
        elif response.status_code == 500 and result['Message'].__contains__("Pagamento"):
            send_log(
                job_config_dict.get('job_name'),
                job_config_dict.get('enviar_logs'),
                job_config_dict.get('enviar_logs_debug'),
                f'Pedido: {body["numero_pedido_externo"]}, Pagamento {body["identificador_pagamento"]} '
                f'não configurado no painel do OKVENDAS.',
                LogType.WARNING,
                body["numero_pedido_externo"]
            )
            # return [OkvendasResponse(**r) for r in response.json()]
            return result
        else:
            logger.error(
                f'Erro ao realizar POST na api okvendas {src.client_data.get("url_api_principal")}pedido/insere'
                + str(response.json()), exc_info=True)
            # return [OkvendasResponse(**r) for r in response.json()]
            return result

    except Exception as ex:
        logger.error(
            f'Erro ao realizar POST na api Okvendas {src.client_data.get("url_api_principal")}/pedido/insere '
            + str(ex), exc_info=True)
        return f'Erro ao realizar POST na api Okvendas /pedido/insere {str(ex)}'


def post_send_points_to_okvendas(body, job_config_dict):
    try:
        url = src.client_data.get('url_api_terciario') + '/api/saldoparceiro'
        header = {
            # 'Accept': 'application/json',
            # 'access-token': src.client_data.get('token_api_integracao'),
            'Content-type': 'application/json'
        }

        # json_body = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(body)
        response = requests.post(url, headers=header, json=body)
        response_json = response.content.decode('utf-8')
        response_data = json.loads('[' + response_json + ']')

        if response.ok:
            return True
        else:
            send_log(
                job_config_dict.get('job_name'),
                job_config_dict.get('enviar_logs'),
                job_config_dict.get('enviar_logs_debug'),
                f'Erro ao realizar POST na api okvendas {src.client_data.get("url_api_terciario")}/api/saldoparceiro '
                + response_data,
                LogType.ERROR,
                'PONTOS_PARA_OKVENDAS'
            )
            return False

    except Exception as e:
        send_log(
            job_config_dict.get('job_name'),
            job_config_dict.get('enviar_logs'),
            job_config_dict.get('enviar_logs_debug'),
            f'Erro {str(e)}',
            LogType.ERROR,
            'PONTOS_PARA_OKVENDAS'
        )
        return False


def post_send_distribution_center(body, job_config_dict):
    try:
        url = src.client_data.get('url_api_principal') + '/catalogo/unidadeDistribuicao'
        header = {
            'Accept': 'application/json',
            'access-token': src.client_data.get('token_api_integracao'),
            'Content-type': 'application/json'
        }

        json_body = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(json_body)
        response = requests.post(url, headers=header, json=json.loads(json_body))
        # result = jsonpickle.decode(response.content)

        if response.ok:
            return [OkvendasResponse(**r) for r in response.json()]
        else:
            send_log(
                job_config_dict.get('job_name'),
                job_config_dict.get('enviar_logs'),
                job_config_dict.get('enviar_logs_debug'),
                f'Erro ao realizar POST na api okvendas {src.client_data.get("url_api_principal")}'
                f'/catalogo/unidadeDistribuicao ' + str(response.json()),
                LogType.ERROR,
                'ENVIA_CENTRO_DISTRIBUICAO'
            )
            return False

    except Exception as e:
        send_log(
            job_config_dict.get('job_name'),
            job_config_dict.get('enviar_logs'),
            job_config_dict.get('enviar_logs_debug'),
            f'Erro {str(e)}',
            LogType.ERROR,
            'ENVIA_CENTRO_DISTRIBUICAO'
        )
        return False


def post_send_filial(body, job_config_dict):
    try:
        url = src.client_data.get('url_api_principal') + '/catalogo/filial'
        header = {
            'Accept': 'application/json',
            'access-token': src.client_data.get('token_api_integracao'),
            'Content-type': 'application/json'
        }

        json_body = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(json_body)
        response = requests.post(url, headers=header, json=json.loads(json_body))
        # result = jsonpickle.decode(response.content)

        if response.ok:
            return [OkvendasResponse(**r) for r in response.json()]
        else:
            send_log(
                job_config_dict.get('job_name'),
                job_config_dict.get('enviar_logs'),
                job_config_dict.get('enviar_logs_debug'),
                f'Erro ao realizar POST na api okvendas {src.client_data.get("url_api_terciario")}/catalogo/filial '
                + str(response.json()),
                LogType.ERROR,
                'ENVIA_FILIAL'
            )
            return False

    except Exception as e:
        send_log(
            job_config_dict.get('job_name'),
            job_config_dict.get('enviar_logs'),
            job_config_dict.get('enviar_logs_debug'),
            f'Erro {str(e)}',
            LogType.ERROR,
            'ENVIA_FILIAL')
        return False


def post_send_transportadora_parceiro(body, job_config_dict):
    try:
        url = src.client_data.get('url_api_terciario') + '/api/insert_transportadora_fob_parceiro'
        header = {
            'Accept': 'application/json',
            'Content-type': 'application/json'
        }

        response = requests.post(url, headers=header, json={"lista": body})
        # result = jsonpickle.decode(response.content)

        if response.ok:
            return [SbyResponse(**r) for r in response.json()]
        else:
            send_log(
                job_config_dict.get('job_name'),
                job_config_dict.get('enviar_logs'),
                job_config_dict.get('enviar_logs_debug'),
                f'Erro ao realizar POST na api okvendas {src.client_data.get("url_api_principal")}/'
                f'api/insert_transportadora_fob_parceiro ' + str(response.json()),
                LogType.ERROR,
                'TRANSPORTADORA_PARA_OKVENDAS'
            )
            return [SbyResponseError(**response.json())]

    except Exception as e:
        send_log(
            job_config_dict.get('job_name'),
            job_config_dict.get('enviar_logs'),
            job_config_dict.get('enviar_logs_debug'),
            f'Erro {str(e)}',
            LogType.ERROR,
            'TRANSPORTADORA_PARA_OKVENDAS'
        )
        return False
