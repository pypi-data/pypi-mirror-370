import logging
import jsonpickle
import src
import requests
import json

from src.api.entities.estoque import Estoque
from src.api.entities.pedido import Queue, Order
from src.api.entities.preco import Preco
from src.api.entities.produto import Produto
from src.entities.invoice import Invoice
from src.entities.log import Log
from src.entities.response import GenericResponse

# from src.entities.orderb2b import OrderB2B
# from src.entities.orderb2c import OrderB2C

from typing import List

logger = logging.getLogger()


def send_stocks_hub(body: List[Estoque]) -> List[GenericResponse]:
    try:

        url = f'{src.client_data.get("url_api_principal")}/api/estoque'
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "access-token": src.client_data.get("token_oking"),
        }
        json_body = jsonpickle.encode(body, unpicklable=False)
        json_body = '{"lista":' + json_body + "}"

        if src.print_payloads:
            print(json_body)
        response = requests.post(url, json=json.loads(json_body), headers=headers)
        result = [GenericResponse(**t) for t in response.json()]
        return result
    except Exception as ex:
        logger.error(f"Erro ao realizar POST na API {str(ex)}")


###############################################################


def post_prices(body: List[Preco]) -> List[GenericResponse]:
    try:

        url = f'{src.client_data.get("url_api_principal")}/api/preco'
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            # 'access-token': src.client_data.get('token_api')
        }

        json_body = jsonpickle.encode(body, unpicklable=False)
        json_body = '{"lista":' + json_body + "}"

        if src.print_payloads:
            print(json_body)
        response = requests.post(url, headers=headers, json=json.loads(json_body))
        result = [GenericResponse(**t) for t in response.json()]
        return result
    # json_response = response.json()

    # if len(json_response) > 0:
    #    array_response = [json_response]
    #    result_dict = response_dict(json_response)
    # return result_dict
    except Exception as ex:
        logger.error(f"Erro ao realizar POST na API HUB/api/preco {str(ex)}")


def post_products(body: List[Produto]) -> List[GenericResponse]:
    try:
        url = f'{src.client_data.get("url_api_principal")}/api/produto'
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            # 'access-token': src.client_data.get('token_api')
        }

        json_body = jsonpickle.encode(body, unpicklable=False)
        json_body = '{"lista":' + json_body + "}"

        if src.print_payloads:
            print(json_body)
        response = requests.post(url, headers=headers, json=json.loads(json_body))
        result = [GenericResponse(**t) for t in response.json()]
        return result
    # json_response = response.json()

    # if len(json_response) > 0:
    #    array_response = [json_response]
    #    result_dict = response_dict(json_response)
    # return result_dict
    except Exception as ex:
        logger.error(f"Erro ao realizar POST na API HUB/api/produto {str(ex)}")


def post_clients(body: List):
    try:
        url = f'{src.client_data.get("url_api_principal")}/api/cliente'
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            # 'access-token': src.client_data.get('token_oking')
        }

        json_body = jsonpickle.encode(body, unpicklable=False)
        json_body = '{"lista":' + json_body + "}"

        if src.print_payloads:
            print(json_body)
        response = requests.post(url, headers=headers, json=json.loads(json_body))
        if response.ok:
            result = [GenericResponse(**t) for t in response.json()]
            return result
        else:
            logger.warning(f"Erro {response.status_code}, {response.json()['message']}")
            return {
                "error": response.status_code,
                "message": response.json()["message"],
            }
    # json_response = response.json()

    # if len(json_response) > 0:
    #    array_response = [json_response]
    #    result_dict = response_dict(json_response)
    # return result_dict
    except Exception as ex:
        logger.error(f"Erro ao realizar POST na API HUB/api/cliente {str(ex)}")
        raise ex


def post_vendas(body: List):
    try:
        url = f'{src.client_data.get("url_api_principal")}/api/venda'
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            # 'access-token': src.client_data.get('token_oking')
        }

        json_body = jsonpickle.encode(body, unpicklable=False)
        json_body = '{"lista":' + json_body + "}"

        if src.print_payloads:
            print(json_body)
        response = requests.post(url, headers=headers, json=json.loads(json_body))
        if response.ok:
            result = [GenericResponse(**t) for t in response.json()]
            return result
        else:
            logger.warning(f"Erro {response.status_code}, {response.json()['message']}")
            return {
                "error": response.status_code,
                "message": response.json()["message"],
            }
    except Exception as ex:
        logger.error(f"Erro ao realizar POST na API HUB/api/venda {str(ex)}")
        raise ex


def response_dict(resultado):
    lista = []
    for row in resultado:
        pdict = {
            "identificador": str(row["identificador"]),
            "sucesso": str(row["sucesso"]),
            "message": str(row["mensagem"]),
        }
        lista.append(pdict)

    return lista


###############################################################
def post_log(log: Log) -> bool:
    try:
        if not src.is_dev:
            url = f"https://{src.shortname_interface}.oking.openk.com.br/api/log_integracao"
            headers = {
                "Content-type": "application/json",
                "Accept": "application/json",
                "access-token": src.client_data.get("token_api"),
            }

            json_log = jsonpickle.encode(log, unpicklable=False)
            # if src.print_payloads:
            #    print(json_log)
            response = requests.post(url, json=json.loads(json_log), headers=headers)
            if response.ok:
                return True

            return False
        else:
            return True
    except Exception:
        return False


def get_order_queue(body: dict, stats) -> List[Queue]:
    retqueue = []
    try:
        url_api = body.get("url_api_secundaria") + "/api/consulta/pedido_fila/"
        token = body.get("token_oking")
        status = stats
        pagina = 0
        url = f"{url_api}filtros?token={token}&status={status}"
        response = requests.get(
            url,
            headers={"Accept": "application/json", "access-token": token},
            params={"pagina": pagina},
        )
        if response.text == "Retorno sem dados!":
            logger.warning(f"{response.text}")
        elif response.ok:
            retqueue = [Queue(**t) for t in response.json()]
        else:
            logger.warning(
                f"Retorno sem sucesso {response.status_code} - {response.url}"
            )
    except Exception as ex:
        logger.error(
            f"Erro ao realizar GET na api oking hub {url}" + str(ex), exc_info=True
        )
        raise

    return retqueue


def get_order(body: dict, pedido_oking_id) -> Order:
    retorder = None
    try:
        url_api = body.get("url_api_secundaria") + "/api/consulta/pedido/filtros"
        response = requests.get(
            url_api,
            headers={
                "Accept": "application/json",
                "access-token": body.get("token_api"),
            },
            params={
                "token": body.get("token_oking"),
                "pedido_oking_id": pedido_oking_id,
            },
        )
        if response.ok:
            obj = jsonpickle.decode(response.content)
            retorder = Order(**obj)
        else:
            logger.warning(
                f"Retorno sem sucesso {response.status_code} - {response.url}"
            )
    except Exception as ex:
        logger.error(f"Erro ao realizar GET na api oking hub {url_api} - {str(ex)}")
        raise

    return retorder


# def get_order_b2c(url: str, token: str, order_id: int) -> OrderB2C:
#     order = None
#     try:
#         response = requests.get(url.format(order_id), headers={'Accept': 'application/json', 'access-token': token})
#         if response.ok:
#             obj = jsonpickle.decode(response.content)
#             order = OrderB2C(**obj)
#         else:
#             logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
#     except Exception as ex:
#         logger.error(f'Erro ao realizar GET na api okvendas {url} - {str(ex)}')
#         raise
#
#     return order
# def get_order_b2b(url: str, token: str, order_id: int) -> OrderB2B:
#     order = None
#     try:
#         response = requests.get(url.format(order_id), headers={'Accept': 'application/json', 'access-token': token})
#         if response.ok:
#             obj = jsonpickle.decode(response.content)
#             order = OrderB2B(**obj)
#         else:
#             logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
#     except Exception as ex:
#         logger.error(f'Erro ao realizar GET na api okvendas {url} - {str(ex)}')
#         raise
#
#     return order


def post_order_erp_code(body) -> bool:
    url = src.client_data.get("url_api_principal") + "/api/pedido_integrado"
    token = src.client_data.get("token_api_integracao")
    try:
        if src.print_payloads:
            print(body)
        response = requests.post(
            url,
            json=body,
            headers={"Accept": "application/json", "access-token": token},
        )
        if response.ok:
            return True
        else:
            logger.warning(
                f"Retorno sem sucesso {response.status_code} - {response.url}"
            )
            return False
    except Exception as ex:
        logger.error(
            f"Erro ao realizar GET na api okinghub {url}" + str(ex), exc_info=True
        )
        return False


def put_client_erp_code(body: dict) -> bool:
    url = src.client_data.get("url_api_principal") + "/cliente/codigo"
    token = (src.client_data.get("token_api_integracao"),)
    try:
        data = jsonpickle.encode(body, unpicklable=False)
        if src.print_payloads:
            print(data)
        response = requests.put(
            url,
            data=json.loads(data),
            headers={"Accept": "application/json", "access-token": token},
        )
        if response.ok:
            return True
        else:
            logger.warning(
                f"Retorno sem sucesso {response.status_code} - {response.url}"
            )
            return False
    except Exception as ex:
        logger.error(
            f"Erro ao realizar GET na api okinghub {url}" + str(ex), exc_info=True
        )
        return False


def put_protocol_orders(protocolos: List[str]) -> bool:
    url = src.client_data.get("url_api_secundaria") + f"/pedido/fila"
    try:
        json_protocolos = jsonpickle.encode(protocolos)
        if src.print_payloads:
            print(json_protocolos)
        response = requests.put(
            url,
            json=json.loads(json_protocolos),
            headers={
                "Accept": "application/json",
                "access-token": src.client_data.get("token_api"),
            },
        )
        if response.ok:
            return True
        else:
            logger.warning(
                f"Retorno sem sucesso {response.status_code} - {response.url}"
            )
            return False
    except Exception as ex:
        logger.error(
            f"Erro ao protocolar pedidos na api oking hub {url}" + str(ex),
            exc_info=True,
        )
        return False


def post_faturar(invoice: Invoice) -> None | str | GenericResponse:
    """
    Enviar NF de um pedido para api okvendas
    Args:
        invoice: Objeto com os dados da NF

    Returns:
    None se o envio for sucesso. Caso falhe, um objeto contendo status e descrição do erro
    """
    try:
        # headers = {'Content-type': 'application/json',
        #            'Accept': 'application/json',
        #            'access-token': token}
        token = src.client_data.get("token_oking")
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization-token": "basic " + token,
        }

        url = src.client_data.get("url_api_principal") + "/api/pedido_faturar"

        jsonpickle.set_encoder_options("simplejson", use_decimal=True, sort_keys=True)
        json_invoice = jsonpickle.encode(invoice, unpicklable=False)
        # TODO ----> Melhorar solução para json_enconde com o campo amount em Decimal
        json_invoice = json_invoice.replace(
            '"valor_nf": null', f'"valor_nf":{invoice.valor_nf}'
        )
        if src.print_payloads:
            print(json_invoice)
        logger.info("LOG AUXILIAR - realizando post na Api /api/pedido_faturar")
        response = requests.post(url, json=json.loads(json_invoice), headers=headers)

        if response.ok:
            logger.info("LOG AUXILIAR - response ok, saindo")
            return None
        else:
            # jsonReturn = f'"text":{response.text}, "status_code":{response.status_code}'
            # err = jsonpickle.decode(response.content)
            # invoice_response = InvoiceResponse(**err)
            # result = [GenericResponse(**t) for t in response.json()]
            invoice_response = response.text
            if "_okvendas" in invoice_response or "_openkuget" in invoice_response:
                invoice_response = (
                    "Erro interno no servidor. Entre em contato com o suporte"
                )
            logger.info("LOG AUXILIAR - post mal sucedido, saindo")
            return invoice_response

    except Exception as ex:
        logger.error(f"Erro ao realizar POST na API {str(ex)}")


def post_sent_okinghub(sent):
    try:
        url = f'{src.client_data.get("url_api_principal")}/api/pedido_encaminhar'
        token = src.client_data.get("token_oking")
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization-token": "basic " + token,
        }
        json_sent = jsonpickle.encode(sent, unpicklable=False)
        if src.print_payloads:
            print(json_sent)
        response = requests.post(url, json=json.loads(json_sent), headers=headers)

        if response.ok:
            return None
        else:

            result = [GenericResponse(**t) for t in response.json()]
            invoice_response = response.text
            if "_okvendas" in invoice_response or "_openkuget" in invoice_response:
                invoice_response = (
                    "Erro interno no servidor. Entre em contato com o suporte"
                )
            return invoice_response

    except Exception as ex:
        logger.error(f"Erro ao realizar POST na API {str(ex)}")


def post_delivered_okinghub(delivered):
    url = f'{src.client_data.get("url_api_principal")}/api/pedido_entregue'
    token = src.client_data.get("token_oking")
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Authorization-token": "basic " + token,
    }
    jsonpickle.set_encoder_options("simplejson", use_decimal=True, sort_keys=True)
    json_delivered = jsonpickle.encode(delivered, unpicklable=False)
    if src.print_payloads:
        print(json_delivered)
    response = requests.post(url, json=json.loads(json_delivered), headers=headers)

    if response.ok:
        return None


def get_queue_order_to_duplicate():
    retorder = None
    try:
        url = f'{src.client_data.get("url_api_principal")}/api/consulta/pedido_fila_duplicar/filtros'
        token = src.client_data.get("token_oking")
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization-token": "basic " + token,
        }
        pagina = 0
        my_token = {"token": token, "pagina": pagina}
        if src.print_payloads:
            print(my_token)
        response = requests.get(url, params=my_token, headers=headers)
        if response.ok:
            retorder = [Queue(**t) for t in response.json()]
        else:
            logger.warning(
                f"Retorno sem sucesso {response.status_code} - {response.url}"
            )
    except Exception as ex:
        logger.error(f"Erro ao realizar GET na api oking hub {url} - {str(ex)}")
        raise

    return retorder


def post_protocol_duplicated_order(duplicated_order):
    url = src.client_data.get("url_api_secundaria") + f"/api/pedido_duplicado_integrado"
    try:
        json_protocolos = jsonpickle.encode(duplicated_order)
        if src.print_payloads:
            print(json_protocolos)
        response = requests.post(
            url,
            json=json.loads(json_protocolos),
            headers={
                "Accept": "application/json",
                "access-token": src.client_data.get("token_api"),
            },
        )
        if response.ok:
            return True
        else:
            logger.warning(
                f"Retorno sem sucesso {response.status_code} - {response.url}"
            )
            return False
    except Exception as ex:
        logger.error(
            f"Erro ao protocolar pedidos duplicados na api okvendas {url}" + str(ex),
            exc_info=True,
        )
        return False
