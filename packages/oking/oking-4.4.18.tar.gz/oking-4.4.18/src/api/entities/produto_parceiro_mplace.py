class Produto_Parceiro_Mplace:
    def __init__(self, codigo_sku_principal: str = '', nome: str = '', descricao: str = '', modelo: str = '', marca_descricao: str = '',
                 quantidade_minima: int = 0, multiplo: bool = True, quantidade_caixa: int = 0, quantidade_caixa_fabrica: int = 0, multiplo_quantidade: int = 0,
                 ncm: str = '', ean_13_variacao: str = '', codigo_sku_variacao: str = '', sku_parceiro: str = '', sku_codigo_referencia: str = '', tempo_adicional_entrega: str = '',
                 meses_garantia: str = '', ativo: bool = True, afiliado_id: str = '', cst_a: str = '', cst_b: str = '', cst_c: str = '', certificado_anatel: str = '',
                 medida_codigo: str = '', medida_descricao: str = '', medida_sigla: str = '', altura: int = 0, largura: int = 0, comprimento: int = 0, peso: int = 0,
                 fabricante_codigo: str = '', fabricante_descricao: str = '', codigo_caracteristica: str = '', nome_caracteristica: str = '', codigo_categoria_marketplace: int = 0,
                 codigo_caracteristica_variaccao: str = '', nome_caracteristica_variacao: str = '', codigo_categoria_n1: str = '', nome_categoria_n1: str = '', codigo_categoria_n2: str = '',
                 nome_categoria_n2: str = '', codigo_categoria_n3: str = '', nome_categoria_n3: str = '', codigo_categoria_n4: str = '', nome_categoria_n4: str = '',
                 hierarquia_categoria: str = '', **kwargs):
        self.product_code = codigo_sku_principal
        self.product_name = nome
        self.product_description = descricao
        self.product_reference_code = codigo_sku_principal
        self.product_model = modelo
        self.product_brand = marca_descricao
        self.product_minimum_quantity = quantidade_minima
        self.product_is_multiple = bool(multiplo)
        self.product_package_quantity = int(quantidade_caixa)
        self.product_manufacturer_package_quantity = quantidade_caixa_fabrica
        self.product_multiple_quantity = multiplo_quantidade
        if ncm is None:
            self.product_ncm = ''
        else:
            self.product_ncm = ncm
        self.product_ean = ean_13_variacao
        self.product_sku = codigo_sku_variacao
        self.product_sku_partner = sku_parceiro
        self.product_sku_reference_code = sku_codigo_referencia
        self.product_additional_delivery_time = tempo_adicional_entrega
        self.product_months_waranty = meses_garantia
        self.product_active = bool(ativo)
        self.product_affiliate_id = afiliado_id
        self.cst_a = cst_a
        self.cst_b = cst_b
        self.cst_c = cst_c
        self.anatel_certificate = certificado_anatel

        # anatel_certificate

        self.manufacturer_code = fabricante_codigo
        self.manufacturer_name = fabricante_descricao

        # product_measurements

        self.measurement_code = str(medida_codigo)
        self.measurement_unit = medida_sigla
        self.measurement_description = medida_descricao

        # product_dimensions

        self.height = altura
        self.length = comprimento
        self.width = largura
        self.weight = peso


        self.category_hierarchy = hierarquia_categoria

        self.product_category_hierarchy = []
        if nome_categoria_n1 is not None and len(nome_categoria_n1) > 0:
            self.product_category_hierarchy.append(
                HierarquiaCategoriaProduto(codigo_categoria_marketplace, nome_categoria_n1, codigo_categoria_n1, ''))

        if nome_categoria_n2 is not None and len(nome_categoria_n2) > 0:
            self.product_category_hierarchy.append(
                HierarquiaCategoriaProduto(codigo_categoria_marketplace, nome_categoria_n2, codigo_categoria_n2,
                                           codigo_categoria_n1))

        if nome_categoria_n3 is not None and len(nome_categoria_n3) > 0:
            self.product_category_hierarchy.append(
                HierarquiaCategoriaProduto(codigo_categoria_marketplace, nome_categoria_n3, codigo_categoria_n3,
                                           codigo_categoria_n2))

        if nome_categoria_n4 is not None and len(nome_categoria_n4) > 0:
            self.product_category_hierarchy.append(
                HierarquiaCategoriaProduto(codigo_categoria_marketplace, nome_categoria_n4, codigo_categoria_n4,
                                           codigo_categoria_n3))

        # product_characteristics

        self.characteristic_code = codigo_caracteristica
        self.characteristic_name = nome_caracteristica

        ## characteristic_options

        self.characteristic_option_code = codigo_caracteristica_variaccao
        self.characteristic_option_name = nome_caracteristica_variacao
        self.__dict__.update(kwargs)

class HierarquiaCategoriaProduto:
    def __init__(self, categoria_marketplace_id, nome, codigo, codigo_categoria_pai, **kwargs):
        self.category_marketplace_id = categoria_marketplace_id
        self.category_code = codigo
        self.category_name = nome
        self.category_parent_code = codigo_categoria_pai
        self.__dict__.update(kwargs)
