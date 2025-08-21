import datetime


class Produto:
    def __init__(self, nome: str, codigo_sku_variacao: str, codigo_erp: str, codigo_sku_principal: str
                 , codigo_erp_variacao: str, ean_13_variacao: str, ean_14_variacao: str, variacao_opcao_1: str
                 , variacao_opcao_valor_1: str, variacao_opcao_2: str, variacao_opcao_valor_2: str
                 , variacao_opcao_3: str, variacao_opcao_valor_3: str, palavra_chave: str, meta_descricao: str
                 , quantidade_minima: int, quantidade_caixa: int, multiplo: bool, ativo: bool, peso: float
                 , volume: float, largura: float, altura: float, comprimento: float, marca_codigo: str
                 , fabricante_codigo: str, fabricante_descricao: str, fabricante_link_imagem: str, medida_codigo: str
                 , medida_sigla: str, preco_custo: int, codigo_categoria_n1: str, nome_categoria_n1: str
                 , codigo_categoria_n2: str, nome_categoria_n2: str, codigo_categoria_n3: str, nome_categoria_n3: str
                 , codigo_categoria_n4: str, nome_categoria_n4: str, modelo: str, ncm: str
                 , ipi: int, estoque_minimo: int, token: str, medida_descricao: str, descricao: str = ''
                 , marca_descricao: str = '', meses_garantia: int = 0, agrupador: str = ''
                 , data_desativacao=None, data_alteracao=None, data_sincronizacao=None
                 , tempo_adicional_entrega: int = 0, adicional_descricao_1: str = ''
                 , adicional_conteudo_1: str = ''
                 ):
        nome
        codigo_sku_principal
        codigo_erp
        codigo_sku_variacao
        codigo_erp_variacao
        agrupador
        ean_13_variacao
        ean_14_variacao
        variacao_opcao_1
        variacao_opcao_valor_1
        variacao_opcao_2
        variacao_opcao_valor_2
        variacao_opcao_3
        variacao_opcao_valor_3
        descricao
        meta_descricao
        palavra_chave
        quantidade_minima
        quantidade_caixa
        multiplo
        ativo
        peso
        volume
        largura
        altura
        comprimento
        marca_codigo
        marca_descricao
        fabricante_codigo
        fabricante_descricao
        fabricante_link_imagem
        medida_descricao
        medida_codigo
        medida_sigla
        preco_custo
        codigo_categoria_n1
        nome_categoria_n1
        codigo_categoria_n2
        nome_categoria_n2
        codigo_categoria_n3
        nome_categoria_n3
        codigo_categoria_n4
        nome_categoria_n4
        modelo
        meses_garantia
        ncm
        ipi
        estoque_minimo
        data_desativacao
        data_alteracao
        data_sincronizacao
        tempo_adicional_entrega
        adicional_descricao_1
        adicional_conteudo_1
        token
