from datetime import datetime


class Foto_Sku:
    def __init__(self, codigo_sku, codigo_erp, base64_foto: str, codigo_erp_sku: str, codigo_foto: str, ordem: int,
                 foto_padrao: bool, data_alteracao: datetime, existe, **kwargs):
        self.codigo_sku: str = codigo_sku
        self.codigo_erp: str = codigo_erp
        self.base64_foto: str = base64_foto
        self.codigo_erp_sku: str = codigo_erp_sku
        self.codigo_foto: str = codigo_foto
        self.ordem: int = ordem
        self.foto_padrao: bool = foto_padrao
        self.data_alteracao = data_alteracao
        self.existe = existe
        self.__dict__.update(kwargs)


class Foto_Produto_Sku:
    def __init__(self, base64_foto: str, codigo_erp_sku: str, codigo_foto: str, ordem: int,
                 foto_padrao: bool, **kwargs):

        self.base64_foto: str = base64_foto
        self.codigo_erp_sku: str = codigo_erp_sku
        self.codigo_foto: str = codigo_foto
        self.ordem: int = ordem
        self.foto_padrao: bool = foto_padrao
        self.__dict__.update(kwargs)
