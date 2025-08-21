import json


class Produto_Okvendas:
    def __init__(self, product_dict: dict):
        self.imagem_base64 = product_dict['imagem_base64']
        self.codigo_erp = product_dict['codigo_erp']
        self.parceiro = 1  # parceiro 1 = ERP
        self.codigo_referencia = product_dict['codigo_referencia']
        self.agrupador = product_dict['agrupador']
        self.nome = product_dict['nome']
        self.descricao = product_dict['descricao']
        self.quantidade_minima = product_dict['quantidade_minima']
        self.quantidade_maxima_compra = product_dict['quantidade_caixa']
        self.multiplo = product_dict['multiplo']
        self.metakeyword = product_dict['metakeyword']
        self.metadescription = product_dict['metadescription']
        self.meses_garantia = product_dict['meses_garantia']
        self.modelo = product_dict['modelo']
        self.tempo_adicional_entrega = product_dict['tempo_adicional_entrega']
        # self.ativo = bool(product_dict['ativo'])
        self.dimensoes = Dimensao(product_dict['peso'], product_dict['altura'], product_dict['largura'],
                                  product_dict['comprimento'], product_dict['volume'])
        self.unidade_medida = UnidadeMedida(product_dict['medida_sigla'], product_dict['medida_descricao'],
                                            product_dict['medida_codigo'])
        self.ipi = product_dict['ipi']
        self.ncm = product_dict['ncm']

        self.hierarquias_categoria = []
        if product_dict['nome_categoria_n1'] is not None:
            self.hierarquias_categoria.append(
                NivelCategoria(product_dict['nome_categoria_n1'], product_dict['codigo_categoria_n1'], None))

        if product_dict['nome_categoria_n2'] is not None:
            self.hierarquias_categoria.append(
                NivelCategoria(product_dict['nome_categoria_n2'], product_dict['codigo_categoria_n2'],
                               product_dict['codigo_categoria_n1']))

        if product_dict['nome_categoria_n3'] is not None:
            self.hierarquias_categoria.append(
                NivelCategoria(product_dict['nome_categoria_n3'], product_dict['codigo_categoria_n3'],
                               product_dict['codigo_categoria_n2']))

        if product_dict['nome_categoria_n4'] is not None:
            self.hierarquias_categoria.append(
                NivelCategoria(product_dict['nome_categoria_n4'], product_dict['codigo_categoria_n4'],
                               product_dict['codigo_categoria_n3']))

        self.fabricante = Fabricante(product_dict['fabricante_descricao'], product_dict['fabricante_link_imagem'],
                                     product_dict['fabricante_codigo'])
        self.marca = Marca(product_dict['marca_descricao'], product_dict['marca_link_imagem'],
                           product_dict['marca_codigo'])

        self.atributos_produto = []
        hierarquia_atributo = []
        attr = None
        if product_dict['variacao_opcao_1'] is not None and product_dict['variacao_opcao_valor_1'] is not None:
            if product_dict['variacao_opcao_2'] is not None and product_dict['variacao_opcao_valor_2'] is not None:
                if product_dict['variacao_opcao_3'] is not None and product_dict['variacao_opcao_valor_3'] is not None:
                    attr = Atributo(product_dict['variacao_opcao_1'], product_dict['variacao_opcao_1'],
                                    product_dict['variacao_opcao_valor_1'],
                                    Atributo(product_dict['variacao_opcao_2'], product_dict['variacao_opcao_2'],
                                             product_dict['variacao_opcao_valor_2'],
                                             Atributo(product_dict['variacao_opcao_3'],
                                                      product_dict['variacao_opcao_3'],
                                                      product_dict['variacao_opcao_valor_3'], None)))
                    # hierarquia_atributo.append(product_dict['VARIACAO_OPCAO_VALOR_3'])
                else:
                    attr = Atributo(product_dict['variacao_opcao_1'], product_dict['variacao_opcao_1'],
                                    product_dict['variacao_opcao_valor_1'],
                                    Atributo(product_dict['variacao_opcao_2'], product_dict['variacao_opcao_2'],
                                             product_dict['variacao_opcao_valor_2'], None))
                    # hierarquia_atributo.append(product_dict['VARIACAO_OPCAO_VALOR_2'])
            else:
                attr = Atributo(product_dict['variacao_opcao_1'], product_dict['variacao_opcao_1'],
                                product_dict['variacao_opcao_valor_1'], None)
                # hierarquia_atributo.append(product_dict['VARIACAO_OPCAO_VALOR_1'])

            if attr is not None:
                self.atributos_produto.append(attr)

        preco_atual = 0.0
        if 'preco_atual' in product_dict and product_dict['preco_atual'] is not None:
            preco_atual = float('{:.2f}'.format(product_dict['preco_atual']))

        preco_lista = 0.0
        if 'preco_lista' in product_dict and product_dict['preco_lista'] is not None:
            preco_lista = float('{:.2f}'.format(product_dict['preco_lista']))

        preco_custo = 0.0
        if 'preco_custo' in product_dict and product_dict['preco_custo'] is not None:
            preco_custo = float('{:.2f}'.format(product_dict['preco_custo']))

        self.preco_estoque = [PrecoEstoque(product_dict['codigo_erp_variacao'], product_dict['sku_variacao'],
                                           None, product_dict['ean_13_variacao'], product_dict['ean_14_variacao'],
                                           preco_atual, preco_lista, preco_custo, product_dict['quantidade'], self.dimensoes, hierarquia_atributo,
                                           bool(product_dict['ativo']))]

        self.outras_descricoes = []
        if product_dict['adiciona_descricao_1'] is not None and product_dict['adiciona_conteudo_1'] is not None:
            self.outras_descricoes.append(
                InfoDescricao(product_dict['adiciona_descricao_1'], product_dict['adiciona_conteudo_1'], 1))

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __repr__(self):
        return "<Produto id:%s, codigo_sku:%s>" % (self.id, self.codigo_sku)

    def __str__(self):
        return 'Produto id : %s, ' \
               'SKU : %s' % (self.id, self.codigo_sku)


class PrecoEstoque:
    def __init__(self, codigo_erp_atributo: str, codigo_referencia_atributo: str, codigo_erp_restock: str,
                 codigo_ean: str, codigo_ean14: str, preco: float, preco_lista: float, preco_custo: float,
                 estoque: int, dimensoes, hierarquia_codigo_atributo, ativo: bool):
        self.codigo_erp_atributo = codigo_erp_atributo
        self.codigo_referencia_atributo = codigo_referencia_atributo
        self.codigo_erp_restock = codigo_erp_restock
        self.codigo_ean = codigo_ean
        self.codigo_ean14 = codigo_ean14
        self.preco = preco
        self.preco_lista = preco_lista
        self.preco_custo = preco_custo
        self.estoque = estoque
        self.dimensoes = dimensoes
        self.hierarquia_codigo_atributo = hierarquia_codigo_atributo
        self.ativo = ativo


class Dimensao:
    def __init__(self, peso, altura, largura, comprimento, volume):
        self.peso = peso
        self.altura = altura
        self.largura = largura
        self.comprimento = comprimento
        self.volume = volume


class ItemBrinde:
    def __init__(self, preco_atual, quantidade, desconto, produto_id,
                 codigo_externo, identificador_produto, codigo_referencia,
                 nome_produto, unidade_produto, identificador_atributo,
                 identificador_opcao_atributo, filial_expedicao,
                 filial_faturamento):
        self.preco_atual = preco_atual
        self.quantidade = quantidade
        self.desconto = desconto
        self.produto_id = produto_id
        self.codigo_externo = codigo_externo
        self.identificador_produto = identificador_produto
        self.codigo_referencia = codigo_referencia
        self.nome_produto = nome_produto
        self.unidade_produto = unidade_produto
        self.identificador_atributo = identificador_atributo
        self.identificador_opcao_atributo = identificador_opcao_atributo
        self.filial_expedicao = filial_expedicao
        self.filial_faturamento = filial_faturamento


class ItemPersonalizado:
    def __init__(self, id, preco_liquido, preco_bruto, texto):
        self.id = id
        self.preco_liquido = preco_liquido
        self.preco_bruto = preco_bruto
        self.texto = texto


def customProdutoDecoder(produtoDict):
    return Produto_Okvendas(**produtoDict)


class Medida:
    def __init__(self, volume, peso, altura, largura, comprimento):
        self.volume = volume
        self.peso = peso
        self.altura = altura
        self.largura = largura
        self.comprimento = comprimento


class UnidadeMedida:
    def __init__(self, sigla, descricao, codigo):
        self.sigla = sigla
        self.descricao = descricao
        self.codigo = codigo


class NivelCategoria:
    def __init__(self, nome, codigo, codigo_categoria_pai):
        self.nome = nome
        self.codigo = codigo
        self.codigo_categoria_pai = codigo_categoria_pai


class Fabricante:
    def __init__(self, nome, link_imagem, codigo):
        self.nome = nome
        self.link_imagem = link_imagem
        self.codigo = codigo


class Marca:
    def __init__(self, nome, link_imagem, codigo):
        self.nome = nome
        self.link_imagem = link_imagem
        self.codigo = codigo


class Atributo:
    def __init__(self, classificacao, opcao_descricao, opcao_codigo, atributo_pai):
        self.classificacao = classificacao
        self.opcao_descricao = opcao_descricao
        self.opcao_codigo = opcao_codigo
        self.atributo_pai = atributo_pai


class InfoDescricao:
    def __init__(self, descricao, conteudo, ordem):
        self.descricao = descricao
        self.conteudo = conteudo
        self.ordem = ordem


class InfoCaracteristica:
    def __init__(self, nome, valor):
        self.nome = nome
        self.valor = valor


class Estoque:
    def __init__(self, codigo_erp, quantidade):
        self.codigo_erp = codigo_erp
        self.quantidade = quantidade


class EstoqueUnidadeDistribuicao:
    def __init__(self, u_distribuicao, codigo_erp, produto_id,
                 total, reserva, protocolo, parceiro):
        self.unidade_distribuicao = u_distribuicao
        self.codigo_erp = codigo_erp
        self.produto_id = produto_id
        self.quantidade_total = total
        self.quantidade_reserva = reserva
        self.protocolo = protocolo
        self.parceiro = parceiro


class Preco:
    def __init__(self, codigo_erp_atributo, codigo_referencia_atributo,
                 codigo_erp_restock, codigo_ean, codigo_ean14, ativo,
                 preco, preco_lista, preco_custo, estoque):
        self.codigo_erp_atributo = codigo_erp_atributo
        self.codigo_referencia_atributo = codigo_referencia_atributo
        self.codigo_erp_restock = codigo_erp_restock
        self.codigo_ean = codigo_ean
        self.codigo_ean14 = codigo_ean14
        self.ativo = ativo
        self.preco = preco
        self.preco_lista = preco_lista
        self.preco_custo = preco_custo
        self.estoque = estoque
        self.dimensoes = None  # {Medida}
        self.hierarquia_codigo_atributo = []  # "string"
