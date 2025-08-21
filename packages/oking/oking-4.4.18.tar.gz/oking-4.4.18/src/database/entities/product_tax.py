class ProductTax:
    def __init__(self, codigo_sku, ncm, grupo_tributacao, grupo_cliente,
                 uf_origem, uf_destino, percentual_reducao_base_calcul,
                 mva_iva, icms_intraestadual, icms_interestadual, identificador, filial_codigo_externo, ipi, **kwargs):
        self.sku_code: str = codigo_sku
        self.ncm: str = ncm
        self.taxation_group: str = grupo_tributacao
        self.customer_group: str = grupo_cliente
        self.origin_uf: str = uf_origem
        self.destination_uf: str = uf_destino
        self.percentage_reduction_base_calculation: float = percentual_reducao_base_calcul
        self.mva_iva: float = mva_iva
        self.intrastate_icms: float = icms_intraestadual
        self.interstate_icms: str = icms_interestadual
        self.identifier: str = identificador
        self.branch: str = filial_codigo_externo
        self.ipi: str = ipi
        self.__dict__.update(kwargs)
