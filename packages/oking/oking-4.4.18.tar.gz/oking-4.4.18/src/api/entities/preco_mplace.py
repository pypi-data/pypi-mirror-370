class Preco_Mplace:
    def __init__(self,marketplace_scope_code
                     ,erp_code
                     ,variation_option_id
                     ,sale_price
                     ,list_price
                     ,st_value
                     ,ipi_value
                     ,**kwargs
                 ):
        self.marketplace_scope_code = marketplace_scope_code
        self.erp_code = erp_code
        self.variation_option_id = variation_option_id
        self.sale_price = sale_price
        self.list_price = list_price
        self.st_value = st_value
        self.ipi_value = ipi_value
        self.__dict__.update(kwargs)
