class Entregue:
    def __init__ (self, pedido_oking_id, comprovante_base64: str ='', extensao_comprovante: str ='', **kwargs):
        self.id = pedido_oking_id
        self.base64_receipt = comprovante_base64
        self.file_extension = extensao_comprovante
        self.__dict__.update(kwargs)


class EntregueOkvendas:
    def __init__(self, id, codigoRastreio, linkRastreio, data_previsao_entrega, observacao,
                 data_Entrega, fullfilment):
        self.id = id
        self.codigoRastreio = codigoRastreio
        self.linkRastreio = linkRastreio
        self.data_previsao_entrega = data_previsao_entrega
        self.observacao = observacao
        self.data_Entrega = data_Entrega
        self.fullfilment = fullfilment
