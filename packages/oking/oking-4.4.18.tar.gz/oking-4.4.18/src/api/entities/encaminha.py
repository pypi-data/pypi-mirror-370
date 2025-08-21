import src


class Encaminha:
    def __init__(self, pedido_oking_id: str = '', codigo_rastreio: str = '', link_rastreio: str = '',
                 previsao_entrega: str = '', transportadora: str = '', cnpj_transportadora: str = '', **kwargs):
        self.id = pedido_oking_id
        self.tracking_code = codigo_rastreio
        self.tracking_link = link_rastreio
        self.delivery_forecast = previsao_entrega
        self.carrier = transportadora
        self.carrier_document = cnpj_transportadora
        self.__dict__.update(kwargs)


class EncaminhaOkinghub:
    def __init__(self, pedido_oking_id: str = '', codigo_rastreio: str = '', link_rastreio: str = '',
                 previsao_entrega: str = '', transportadora: str = '', token: str = '', **kwargs):
        self.pedido_oking_id = pedido_oking_id
        self.codigo_rastreio = codigo_rastreio
        self.link_rastreio = link_rastreio
        self.previsao_entrega = previsao_entrega
        self.transportadora = transportadora
        self.token = src.client_data.get('token_oking')
        self.__dict__.update(kwargs)


class EncaminhaOkvendas:
    def __init__(self, id, codigorastreio, linkrastreio, data_previsao_entrega, observacao, codigo_erp, codigo_sku,
                 cnpj_transportadora, transportadora, codigo_transportadora, tipo_servico, quantidade, codigo_carga,
                 fullfilment):
        self.id = id
        self.codigoRastreio = codigorastreio
        self.linkRastreio = linkrastreio
        self.data_previsao_entrega = data_previsao_entrega
        self.observacao = observacao
        self.codigo_erp = codigo_erp
        self.codigo_sku = codigo_sku
        self.cnpj_transportadora = cnpj_transportadora
        self.transportadora = transportadora
        self.codigo_transportadora = codigo_transportadora
        self.tipo_servico = tipo_servico
        self.quantidade = quantidade
        self.codigo_carga = codigo_carga
        self.fullfilment = fullfilment
