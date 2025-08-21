class Preco:
    def __init__(self, sku, token, preco_de, preco_por, data_atualizacao, preco_lista, lista_preco, **kwargs):
        sku: str = sku
        token: str = token
        preco_de: float = preco_de
        preco_por: float = preco_por
        data_atualizacao: str = data_atualizacao
        preco_lista: str = preco_lista
        lista_preco: str = lista_preco
        self.__dict__.update(kwargs)