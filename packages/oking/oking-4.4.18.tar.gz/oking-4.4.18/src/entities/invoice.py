import decimal
import src


class Invoice:
    def __init__(self, pedido_oking_id: int, chave_nf: str, serie_nf: str, numero_nf: str, valor_nf: decimal,
                 data_emissao_nf: str, quantidade_nf: int, link_nf: str, link_xml: str, xml_nf: str):
        self.pedido_oking_id: int = pedido_oking_id
        self.chave_nf: str = chave_nf
        self.serie_nf: str = serie_nf
        self.numero_nf: str = numero_nf
        self.valor_nf: decimal = valor_nf
        self.data_emissao_nf: str = data_emissao_nf
        self.link_danfe: str = link_nf
        self.link_xml: str = link_xml
        self.xml_nf: str = xml_nf
        self.token = src.client_data['token_oking']


class InvoiceMplace:
    def __init__(self, pedido_oking_id: str, numero_nf: str, serie_nf: str, chave_nf: str, valor_nf: float,
                 data_emissao_nf: str, link_danfe: str, link_xml: str, xml_nf: str, last_invoice: bool = True):
        self.pedido_oking_id = pedido_oking_id
        self.number = str(numero_nf)
        self.serie = serie_nf
        self.accessKey = chave_nf
        self.amount = valor_nf
        self.issuedAt = data_emissao_nf
        self.linkDanfe = link_danfe
        self.linkXml = link_xml
        self.xml = xml_nf
        self.last_invoice = bool(last_invoice)


#     def to_json(self):
#         return jsonpickle.dumps(self, unpicklable=False)
#
#
#
# import jsonpickle
# from decimal import Decimal
#
# jsonpickle.set_preferred_backend('simplejson')
# jsonpickle.set_encoder_options('simplejson', use_decimal=True)
#
#
# class DecimalHandler(jsonpickle.handlers.BaseHandler):
#
#     def flatten(self, obj, data):
#         return obj.__str__()  # Convert to json friendly format
#
#
# jsonpickle.handlers.registry.register(Decimal, BaseHandler)
#
#
# class MyClass():
#     def __init__(self, amount):
#         self.amount = amount
#
#     def to_json(self):
#         return jsonpickle.dumps(self, unpicklable=False)
#

class InvoiceOkvendas:
    def __init__(self, pedido_oking_id, numero_nf, serie_nf, chave_nf, valor_nf, data_emissao_nf, quantidade_nf,
                 link_nf, link_xml, xml_nf, fullfilment: bool = False):
        self.id = pedido_oking_id
        self.numero_nota = numero_nf
        self.numero_serie = serie_nf
        self.chave_acesso = chave_nf
        self.valor_total_nota = valor_nf
        self.data_emissao = data_emissao_nf
        self.quantidade_volume = quantidade_nf
        self.link_danfe = link_nf
        self.link_xml = link_xml
        self.xml = xml_nf
        self.fullfilment = fullfilment
