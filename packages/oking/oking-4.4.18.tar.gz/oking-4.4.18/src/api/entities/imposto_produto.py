# Será criado uma lista
# com layot da http://api.gmimportacao.openk.com.br/ok/swagger/ui/index#!/Catalogo/impostoNCM
class ImpostoProduto:
    def __init__(self, codigo_sku, ncm, grupo_tributacao, grupo_cliente,
                 uf_origem, uf_destino,mva_iva, icms_intraestadual,
                  icms_interestadual, percentual_reducao_base_calcul, identificador, filial_codigo_externo, ipi, **kwargs):
        self.codigo_sku: str = codigo_sku
        self.ncm: str = ncm
        self.grupo_tributacao: str = grupo_tributacao
        self.grupo_cliente: str = grupo_cliente
        self.uf_origem: str = uf_origem
        self.uf_destino: str = uf_destino
        self.mva_iva: float = mva_iva
        self.icms_intraestadual: float = icms_intraestadual
        self.icms_interestadual: str = icms_interestadual
        self.percentual_reducao_base_calculo: float = percentual_reducao_base_calcul
        self.identificador: str = identificador
        self.filial_codigo_externo: str = filial_codigo_externo
        self.aliquota_ipi: str = ipi
        self.__dict__.update(kwargs)