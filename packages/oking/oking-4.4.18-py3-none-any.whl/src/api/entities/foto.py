class Foto:
    def __init__(self, codigo_sku: str ='',
                 codigo_foto: str ='',
                 codigo_erp: str = '',
                 variacao_id: int = 0,
                 nome_foto: str ='',
                 link_foto: str ='',
                 data_alteracao: str = '',
                 existe: bool = False,
                 **kwargs):
        self.product_code = codigo_sku,
        self.code = codigo_foto,
        self.erp_code = codigo_erp,
        self.variation_option_id = variacao_id
        self.name = nome_foto,
        self.link = link_foto
        self.data_alteracao = data_alteracao
        self.existe = existe
        self.__dict__.update(kwargs)