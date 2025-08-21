class Preco_OkVendas:
    def __init__(self, sku, preco_por: float, preco_custo: float, preco_de: float,
                 lista_preco, **kwargs):
        self.codigo_erp = sku
        self.preco_atual = float(preco_por)
        self.preco_lista = float(preco_de)
        self.preco_custo = float(preco_custo)
        self.lista_preco = lista_preco
        self.__dict__.update(kwargs)
