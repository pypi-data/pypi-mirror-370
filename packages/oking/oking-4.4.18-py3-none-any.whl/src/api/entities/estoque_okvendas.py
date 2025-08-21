class EstoqueOkvendas:
    def __init__(self, unidade_distribuicao: str, produto_id: str, codigo_erp: str, quantidade_total: int,
                 quantidade_reserva: int, protocolo: str, parceiro: int, **kwargs):
        self.unidade_distribuicao = unidade_distribuicao
        self.produto_id = produto_id
        self.codigo_erp = codigo_erp
        self.quantidade_total = quantidade_total
        self.quantidade_reserva = quantidade_reserva
        self.protocolo = protocolo
        self.parceiro = parceiro
        self.__dict__.update(kwargs)
