class Produto_Mplace:
    def __init__(self, codigo_sku_principal: str = '', seller_id: int = 0, nome: str = '', descricao: str = '',  modelo: str = '', codigo_categoria_marketplace: int = 0, fabricante_codigo: str = '',
                 medida_sigla: str = '', medida_descricao: str = '', altura: int = 0, largura: int = 0, comprimento: int = 0, volume: int = 0, quantidade_minima: int = 0, quantidade_multipla: int = 0, quantidade_caixa: int = 0, quantidade_caixa_fabrica: int = 0,
                 multiplo: int = 0, cst_a: str = '', cst_b: str = '', cst_c: str = '', certificado_anatel: str = '', ncm: str = '', tempo_adicional_entrega: int = 0, meses_garantia: int = 0, ativo: bool = False,
                 ean_13_variacao: str = '', codigo_sku_variacao: str = '', quantidade: int = 0, deposito: str = '', codigo_referencia: str = '', sku_vendedor_id_preco: str = '',
                 preco_atual: int = 0, valor_lista: int = 0, variacao_opcao_id: int = 0, valor_st: int = 0, valor_ipi: int = 0, codigo_escopo_marketplace: str = '', id_atributo: int = 0, id_atributo_variacao: int = 0,
                 id_aba: int = 0, conteudo: str = '',
                 **kwargs):
        self.product_code = codigo_sku_principal
        self.seller_id = seller_id
        self.name = nome
        self.description = descricao
        self.model = modelo
        self.marketplace_category_code = codigo_categoria_marketplace
        self.bar_code = ean_13_variacao
        self.quantity = quantidade
        # manufacturer

        self.code = fabricante_codigo

        #
        self.sku_seller_id = codigo_sku_variacao
        # unit measure

        self.initials = medida_sigla
        self.description_measure = medida_descricao

        #

        # dimensions

        self.height = altura
        self.width = largura
        self.length = comprimento
        self.weight = volume

        #

        self.minimum_quantity = quantidade_minima
        self.multiple_quantity = quantidade_multipla
        self.multiple = multiplo
        self.package_quantity = quantidade_caixa
        self.manufacturer_package_quantity = quantidade_caixa_fabrica
        self.cst_a = cst_a
        self.cst_b = cst_b
        self.cst_c = cst_c
        self.anatel_certificate = certificado_anatel
        if ncm is None:
            self.ncm = ''
        else:
            self.ncm = ncm
        self.additional_delivery_time = tempo_adicional_entrega
        self.months_warranty = meses_garantia
        self.active = ativo

        # stock_attributes_distribution

        self.reference_code_stock = codigo_referencia

        #

        # stock_attributes_distribution_center

        self.dc_code = deposito
        self.reference_code_stock_center = codigo_referencia

        #

        # price_attributes

        self.sku_seller_id_price = sku_vendedor_id_preco
        self.current_price = preco_atual
        self.list_price = valor_lista
        self.variation_option_id = variacao_opcao_id

        #

        # list_price

        self.current_price_list = preco_atual
        self.st_value = valor_st
        self.ipi_value = valor_ipi
        self.variation_option_id = variacao_opcao_id
        self.marketplace_scope_code = codigo_escopo_marketplace

        #

        # attributes

        self.attribute_id = id_atributo
        self.attribute_option_id = id_atributo_variacao

        #

        # tabs

        self.tab_id = id_aba
        self.content = conteudo

        #

        # self.manufacturer: Fabricante = Fabricante(**manufacturer),
        # self.unit_measure: Unidade_Medida = Unidade_Medida(**unit_measure),
        # self.dimensions: Dimensoes = Dimensoes(**dimensions),

        # self.stock_attributes = [Estoque(**i) for i in estoque]
        # self.stock_attributes_distribution_center = [Centro_Distribuicao_Estoque(**i) for i in centro_distribuicao_estoque],
        # self.price_attributes = [Precos(**i) for i in precos]
        # self.list_price = [Lista_Precos(**i) for i in lista_precos]
        # self.attributes = [Atributos(**i) for i in atributos]
        # self.tabs = [Guias(**i) for i in guias]

        self.__dict__.update(kwargs)



