from typing import List

import src


# region OKING-HUB - Conjunto de Classes - BUILDER
class Queue:
    def __init__(self, valor, status, data_pedido, valor_frete, pedido_canal, valor_desconto
                 , pedido_oking_id, pedido_venda_id, numero_pedido_externo, valor_total_sem_desconto
                 , protocolo, data_sync_cancelado_owner, data_sync_cancelado_erp
                 , valor_adicional_forma_pagamento, **kwargs
                 # , valor_adicional_forma_pagt
                 ):
        self.valor = valor
        self.status = status
        self.data_pedido = data_pedido
        self.valor_frete = valor_frete
        self.pedido_canal = pedido_canal
        self.valor_desconto = valor_desconto
        self.pedido_oking_id = pedido_oking_id
        self.pedido_venda_id = pedido_venda_id
        self.numero_pedido_externo = numero_pedido_externo
        self.valor_total_sem_desconto = valor_total_sem_desconto
        # self.valor_adicional_forma_pagt = valor_adicional_forma_pagt
        self.protocolo = protocolo
        self.data_sync_cancelado_owner = data_sync_cancelado_owner
        self.data_sync_cancelado_erp = data_sync_cancelado_erp
        self.valor_adicional_forma_pagamento = valor_adicional_forma_pagamento
        self.__dict__.update(kwargs)


class Order:
    def __init__(self, capa: dict, item: dict, entrega: dict, usuario: dict, adiconal: dict, pagamento: dict,
                 data_pagamento: str, registro_status: dict, endereco_entrega: dict,
                 data_sincronizacao: str, data_sincronizacao_nf: str, data_sincronizacao_rastreio: str,
                 protocolo: str, data_integracao_externa: str, **kwargs):
        self.data_sincronizacao = data_sincronizacao
        self.data_sincronizacao_nf = data_sincronizacao_nf
        self.data_sincronizacao_rastreio = data_sincronizacao_rastreio
        self.capa: OrderCapa = OrderCapa(**capa)
        self.item = item
        self.entrega: OrderEntrega = OrderEntrega(**entrega)
        self.usuario: OrderUsuario = OrderUsuario(**usuario)
        self.adiconal = adiconal
        self.pagamento = pagamento
        self.data_pagamento = data_pagamento
        self.registro_status: OrderStatus = OrderStatus(**registro_status)
        self.endereco_entrega = endereco_entrega
        self.protocolo = protocolo
        self.data_integracao_externa = data_integracao_externa
        self.__dict__.update(kwargs)
        # self.capa: OrderCapa = OrderCapa(**capa)
        # self.items: List[OrderItem] = [OrderItem(**i) for i in item]
        # self.entrega: OrderEntrega = OrderEntrega(**entrega)
        # self.usuario: OrderUsuario = OrderUsuario(**usuario)
        # self.additional_payment_amount: float = valor_adicional_forma_pagt

        # self.channel_id = canal_id
        # self.mediator_cnpj: str = cnpj_intermediador
        # self.payment_institution_cnpj: str = cnpj_instituicao_pagamento

        # payments: List[Payment] = [Payment(**p) for p in pagamento]
        # if len(payments) > 0:
        #    self.paid_date = payments[0].paid_date
        #    self.flag = payments[0].flag
        #    self.erp_payment_condition = payments[0].erp_payment_condition
        #    self.parcels = payments[0].parcels
        #    self.payment_type = payments[0].type
        #    self.purchase_code = payments[0].purchase_code
        #    self.erp_payment_option = payments[0].erp_payment_option
        #
        # try:
        #    partner_shipping_methods: List[PartnerShippingMethod] = [PartnerShippingMethod(**f) for f in
        #                                                             forma_envio_parceiro]
        # except Exception:
        #    partner_shipping_methods: List[PartnerShippingMethod] = [PartnerShippingMethod(**forma_envio_parceiro)]
        #
        # if len(partner_shipping_methods) > 0:
        #    self.shipping_mode = partner_shipping_methods[0].shipping_mode


class OrderCapa:
    def __init__(self, pedido_oking_id: str, pedido_venda_id: str, numero_pedido_externo: str,
                 valor: float, status: str, data_pedido: str,
                 pedido_canal: str, valor_frete: float = 0.0, valor_desconto: float = 0.0,
                 valor_total_sem_desconto: float = 0.0, valor_adicional_forma_pagamento: float = 0.0, **kwargs):
        self.pedido_oking_id = pedido_oking_id
        self.pedido_venda_id = pedido_venda_id
        self.numero_pedido_externo = numero_pedido_externo
        self.valor = valor
        self.status = status
        self.data_pedido = data_pedido
        self.valor_frete = valor_frete
        self.pedido_canal = pedido_canal
        self.valor_desconto = valor_desconto
        self.valor_total_sem_desconto = valor_total_sem_desconto
        self.valor_adicional_forma_pagamento = valor_adicional_forma_pagamento
        self.__dict__.update(kwargs)

class OrderEntrega:
    def __init__(self, modo_envio: str, transportadora: str, codigo_rastreio: str, data_previsao_entrega: str, **kwargs):
        self.modo_envio = modo_envio
        self.transportadora = transportadora
        self.codigo_rastreio = codigo_rastreio
        self.data_previsao_entrega = data_previsao_entrega
        self.__dict__.update(kwargs)


class OrderStatus:
    def __init__(self, comprado_em: str, aprovado_em: str, enviado_em: str, entregue_em: str, faturado_em: str
                 , separado_em: str, cancelado_em: str, separacao_em: str, **kwargs):
        self.comprado_em = comprado_em
        self.aprovado_em = aprovado_em
        self.enviado_em = enviado_em
        self.entregue_em = entregue_em
        self.faturado_em = faturado_em
        self.separado_em = separado_em
        self.cancelado_em = cancelado_em
        self.separacao_em = separacao_em
        self.__dict__.update(kwargs)

class Payment:
    def __init__(self, opcao_pagamento: str, parcelas: int, bandeira: str, condicao_pagamento_erp: str,
                 tabela_financiamento_rsvarejo: str,
                 tipo_venda_rsvarejo: str, canal_venda_id: str, canal_venda: str, numero_cupom: str, valor_cupom: float,
                 codigo_compra: str,
                 codigo_pedido_canal: str, data_movimento: str, codigo_mercado: str, titulos, opcao_pagamento_erp: str, **kwargs):
        self.type: str = opcao_pagamento
        self.erp_payment_condition: str = condicao_pagamento_erp
        self.parcels: int = parcelas
        self.flag: str = bandeira
        self.paid_date: str = titulos[0]['data_pago']
        self.purchase_code: str = codigo_compra
        self.erp_payment_option: str = opcao_pagamento_erp
        self.__dict__.update(kwargs)


class OrderUsuario:
    def __init__(self, nome: str, usuario_id: str, cpf_cnpj: str, tipo_pessoa: str, razao_social: str, email: str,
                 data_nascimento_constituicao: str, rg: str, sexo: str, orgao: str, inscricao_estadual: str,
                 inscricao_municipal: str, codigo_representante: str, codigo_referencia_erp: str,
                 endereco_cobranca: dict,
                 telefone_residencial: str, telefone_celular: str = '', **kwargs):
        self.nome = nome
        self.usuario_id = usuario_id
        self.cpf_cnpj = cpf_cnpj
        self.tipo_pessoa = tipo_pessoa
        self.razao_social = razao_social
        self.email = email
        self.data_nascimento_constituicao = data_nascimento_constituicao
        self.rg = rg
        self.sexo = sexo
        self.orgao = orgao
        self.inscricao_estadual = inscricao_estadual
        self.inscricao_municipal = inscricao_municipal
        self.codigo_representante = codigo_representante
        self.codigo_referencia_erp = codigo_referencia_erp
        self.telefone_residencial = telefone_residencial
        self.telefone_celular = telefone_celular
        self.endereco_cobranca: OrderEndereco = OrderEndereco(**endereco_cobranca)
        self.__dict__.update(kwargs)


class OrderEndereco:
    def __init__(self, cep: str, pais: str, bairro: str, cidade: str, estado: str, numero: str, endereco: str,
                 endereco_id: str, codigo_ibge: str, complemento: str, tipo_logradouro: str, telefone_contato: str,
                 descricao_endereco: str, referencia_entrega: str, **kwargs):
        self.cep = cep
        self.pais = pais
        self.bairro = bairro
        self.cidade = cidade
        self.estado = estado
        self.numero = numero
        self.endereco = endereco
        self.endereco_id = endereco_id
        self.codigo_ibge = codigo_ibge
        self.tipo_logradouro: str = tipo_logradouro or 'Rua'
        self.telefone_contato = telefone_contato
        self.descricao_endereco = descricao_endereco
        self.referencia_entrega = referencia_entrega
        self.complemento = complemento
        self.__dict__.update(kwargs)


class OrderItem:
    def __init__(self, codigo_sku: str, codigo_erp: str, quantidade: int,
                 filial_expedicao: str, cnpj_filial_venda: str, filial_faturamento: str,
                 ean: str, valor: int, valor_sem_desconto: float, valor_frete: float = 0.0, desconto: float = 0.0, **kwargs):
        self.codigo_sku = codigo_sku
        self.codigo_erp = codigo_erp
        self.quantidade = quantidade
        self.valor_frete = valor_frete
        self.filial_expedicao = filial_expedicao
        self.cnpj_filial_venda = cnpj_filial_venda
        self.filial_faturamento = filial_faturamento
        self.ean = ean
        self.valor = valor
        self.valor_sem_desconto = valor_sem_desconto
        self.desconto = desconto
        self.__dict__.update(kwargs)


# endregion

# region MPLACE -Conjunto de Classes para o Integração com o MPlace
class QueueMplace:
    def __init__(self, order_id, site_order_code, date, status_code, protocol, partner_order_code, get_datetime,
                 **kwargs):
        self.pedido_canal = site_order_code
        self.pedido_oking_id = order_id
        self.pedido_venda_id = order_id
        self.status = status_code
        self.data_pedido = date
        self.numero_pedido_externo = partner_order_code
        self.protocolo = protocol
        self.__dict__.update(kwargs)


class OrderMplace:
    def __init__(self, order_id, site_order_code, order_date, total_amount_undiscounted, discount_value,
                 total_amount, discount_list, freight_value, status_code, status_description, delivery_forecast,
                 tracking_code, affiliate_order, payment: dict, status_record: dict, items: list,
                 delivery_shedule: dict, customer: dict, delivery_address: dict, invoice: dict,
                 tracking: dict, partner_order_code, delivery_forecast_mplace, document_intermediator,
                 intermediate_registration_id, document_payment_institution, xped, note_observation, tax_engine,
                 **kwargs):
        self.order_id = order_id
        self.site_order_code = site_order_code
        self.order_date = order_date
        self.total_amount_undiscounted = total_amount_undiscounted
        self.discount_value = discount_value
        self.total_amount = total_amount
        self.discount_list = discount_list
        self.freight_value = freight_value
        self.status_code = status_code
        self.status_description = status_description
        self.delivery_forecast = delivery_forecast
        self.tracking_code = tracking_code
        self.affiliate_order = affiliate_order
        self.payment: PaymentMplace = PaymentMplace(**payment)
        self.status_record: StatusRecordMplace = StatusRecordMplace(**status_record)
        self.itempedido: list[ItemsMplace] = [ItemsMplace(**ite) for ite in items]
        self.delivery_shedule: list[DeliveryScheduleMplace] = [DeliveryScheduleMplace(**s) for s in delivery_shedule]
        self.customer: CustomerMplace = CustomerMplace(**customer)
        self.delivery_address: EnderecoMplace = EnderecoMplace(**delivery_address)
        if invoice is not None:
            self.invoice: InvoiceMplace = InvoiceMplace(**invoice)
        else:
            self.invoice: invoice
        if tracking is not None:
            self.tracking: TrackingMplace = TrackingMplace(**tracking)
        else:
            self.tracking: TrackingMplace = TrackingMplace(' ', ' ', ' ', ' ')
        self.partner_order_code = partner_order_code
        self.delivery_forecast_mplace = delivery_forecast_mplace
        self.document_intermediator = document_intermediator
        self.intermediate_registration_id = intermediate_registration_id
        self.document_payment_institution = document_payment_institution
        self.xped = xped
        self.note_observation = note_observation
        self.tax_engine = tax_engine
        self.__dict__.update(kwargs)


class PaymentMplace:
    def __init__(self, flag: str, payment_options: str, plot_amount: int, **kwargs):
        self.flag = flag
        self.payment_options = payment_options
        self.plot_amount = plot_amount
        self.__dict__.update(kwargs)


class StatusRecordMplace:
    def __init__(self, purchased_at, approved_at, billed_at, separation_at, separated_at,
                 sent_at, delivery_date, canceled_at, **kwargs):
        self.purchased_at = purchased_at
        self.approved_at = approved_at
        self.billed_at = billed_at
        self.separation_at = separation_at
        self.separated_at = separated_at
        self.sent_at = sent_at
        self.delivery_date = delivery_date
        self.canceled_at = canceled_at
        self.__dict__.update(kwargs)


class ItemsMplace:
    def __init__(self, sku_seller_id: str, sku_partner_id: str, quantity: int, quantity_gift: int,
                 variation_option_id: int, sale_price_undiscounted: float, discount: float,
                 sale_price: float, discount_list: list, freight_value: float, **kwargs):
        self.sku_seller_id = sku_seller_id
        self.sku_partner_id = sku_partner_id
        self.quantity = quantity
        self.quantity_gift = quantity_gift
        self.sale_price_undiscounted = sale_price_undiscounted
        self.discount = discount
        self.sale_price = sale_price
        if discount_list is not None:
            self.discount_list: List[DiscountListMplace] = [DiscountListMplace(**d) for d in discount_list]
        else:
            self.discount_list = discount_list
        self.freight_value = freight_value
        self.variation_option_id = variation_option_id
        self.__dict__.update(kwargs)


class DiscountListMplace:
    def __init__(self, description, value, **kwargs):
        self.description = description
        self.value = value
        self.__dict__.update(kwargs)


class DeliveryScheduleMplace:
    def __init__(self, field_name, field_description, field_value, **kwargs):
        self.field_name = field_name
        self.field_description = field_description
        self.field_value = field_value
        self.__dict__.update(kwargs)


class CustomerMplace:
    def __init__(self, name, gender, type: str, document_number, identity_number, email, state_registration,
                 born_at, billing: dict, phones: dict, **kwargs):
        self.name = name
        self.gender = gender
        self.type = type
        self.document_number = document_number
        self.identity_number = identity_number
        self.email = email
        self.state_registration = state_registration
        self.born_at = born_at
        self.billing: EnderecoMplace = EnderecoMplace(**billing)
        self.phones: PhonesMplace = PhonesMplace(**phones)
        self.__dict__.update(kwargs)


class PhonesMplace:
    def __init__(self, office, mobile, **kwargs):
        self.office = office
        self.mobile = mobile
        self.__dict__.update(kwargs)


class EnderecoMplace:
    def __init__(self, postal_code, address, number, complement, city, city_ibge_code, neighborhood, reference,
                 country_id, state, **kwargs):
        self.postal_code = postal_code
        self.address = address
        self.number = number
        self.complement = complement
        self.city = city
        self.city_ibge_code = city_ibge_code
        self.neighborhood = neighborhood
        self.reference = reference
        self.country_id = country_id
        self.state = state
        self.__dict__.update(kwargs)


class InvoiceMplace:
    def __init__(self, number, serie, accessKey, linkDanfe, linkXml, issuedAt, **kwargs):
        self.number = number
        self.serie = serie
        self.accessKey = accessKey
        self.linkDanfe = linkDanfe
        self.linkXml = linkXml
        self.issuedAt = issuedAt
        self.__dict__.update(kwargs)


class TrackingMplace:
    def __init__(self, tracking_code, tracking_link, carrier, carrier_document, **kwargs):
        self.tracking_code = tracking_code
        self.tracking_link = tracking_link
        self.carrier = carrier
        self.carrier_document = carrier_document
        self.__dict__.update(kwargs)


# endregion

# region Okvendas

class QueueOkvendas:
    def __init__(self, pedido_id,
                 numero_pedido_externo, data_pedido, status, protocolo, data_fila, observacao, valor_total,
                 pedido_agrupado, pedido_venda_canal_id, canal_venda_id, **kwargs):
        self.pedido_oking_id = pedido_id
        self.numero_pedido_externo = numero_pedido_externo
        self.data_pedido = data_pedido
        self.status = status
        self.protocolo = protocolo
        self.data_fila = data_fila
        self.observacao = observacao
        self.valor_total = valor_total
        self.pedido_agrupado = pedido_agrupado
        self.pedido_venda_canal_id = pedido_venda_canal_id
        self.canal_venda_id = canal_venda_id
        self.__dict__.update(kwargs)


class OrderOkvendas:
    def __init__(self, id, pedido_venda_id, data_pedido, data_geracao, codigo_referencia, valor_total,
                 valor_forma_pagamento, valor_desconto, valor_frete, status, quantidade_titulos, previsao_entrega,
                 codigo_rastreio, canal_id, transportadora_id,transportadora, servico_id, servico,
                 transacao, usuario, pagamento, itens: list, itens_brinde: list, itens_personalizados,
                 forma_pagamento_parceiro, forma_envio_parceiro, pedido_nota_fiscal, cnpj_intermediador,
                 cnpj_instituicao_pagamento, protocolo, status_observation=None, tipo_frete=None, representante=None,
                 data_status=None, codigo_carga=None, canal_site=None, opcao_forma_entrega=None,
                 codigo_pedido_canal_alternativo=None, data_entrega=None, transportadora_fob=None,
                 identificador_vendedor=None, gateway_pre_definido_2=None, gateway_pre_definido_3=None,
                 gateway_pre_definido_4=None, gateway_pre_definido_5=None, gateway_pre_definido_6=None, valor_taxa_servico=None, **kwargs):
        self.id = id
        self.pedido_venda_id = pedido_venda_id
        self.data_pedido = data_pedido
        self.data_geracao = data_geracao
        self.codigo_referencia = codigo_referencia
        self.valor_total = valor_total
        self.valor_forma_pagamento = valor_forma_pagamento
        self.valor_desconto = valor_desconto
        self.valor_frete = valor_frete
        self.status = status
        self.quantidade_titulos = quantidade_titulos
        self.previsao_entrega = previsao_entrega
        self.data_status = data_status
        self.data_entrega = data_entrega
        self.codigo_rastreio = codigo_rastreio
        self.canal_id = canal_id
        self.transportadora_id = transportadora_id
        self.opcao_forma_entrega = opcao_forma_entrega
        self.transportadora = transportadora
        self.servico_id = servico_id
        self.servico = servico
        self.codigo_carga = codigo_carga
        self.canal_site = canal_site
        self.valor_taxa_servico = valor_taxa_servico
        self.codigo_pedido_canal_alternativo = codigo_pedido_canal_alternativo
        self.tipo_frete = tipo_frete
        self.representante = representante
        self.status_observacao = status_observation
        if transportadora_fob is not None:
            self.transportadora_fob: Transportadora_fob = Transportadora_fob(**transportadora_fob)
        else:
            self.transportadora_fob = transportadora_fob
        if transacao is not None:
            self.transacao: Transacao = Transacao(**transacao)
        else:
            self.transacao = transacao
        if usuario is not None:
            self.usuario: Usuario = Usuario(**usuario)
        else:
            self.usuario = usuario
        self.pagamento: list[Pagamento] = [Pagamento(**p) for p in pagamento]
        self.itens: list[Itens] = [Itens(**i) for i in itens]
        self.itens_brinde: list[Itens_brinde] = [Itens_brinde(**ib) for ib in itens_brinde]
        self.itens_personalizados: list[Itens_personalizados] = [Itens_personalizados(**ip) for ip in
                                                                 itens_personalizados]
        if src.client_data['operacao'].lower().__contains__('b2b'):
            self.forma_pagamento_parceiro: Forma_pagamento_parceiro = Forma_pagamento_parceiro(**forma_pagamento_parceiro)
        elif src.client_data['operacao'].lower().__contains__('b2c'):
            self.forma_pagamento_parceiro: list[Forma_pagamento_parceiro] = [Forma_pagamento_parceiro(**fp) for fp in forma_pagamento_parceiro]

        if src.client_data['operacao'].lower().__contains__('b2b'):
            self.forma_envio_parceiro: Forma_envio_parceiro = Forma_envio_parceiro(**forma_envio_parceiro)
        elif src.client_data['operacao'].lower().__contains__('b2c'):
            self.forma_envio_parceiro: list[Forma_envio_parceiro] = [Forma_envio_parceiro(**fe) for fe in forma_envio_parceiro]

        if pedido_nota_fiscal is not None:
            self.pedido_nota_fiscal: list[Pedido_nota_fiscal] = [Pedido_nota_fiscal(**pn) for pn in pedido_nota_fiscal]
        else:
            self.pedido_nota_fiscal = pedido_nota_fiscal
        self.cnpj_intermediador = cnpj_intermediador
        self.cnpj_instituicao_pagamento = cnpj_instituicao_pagamento
        self.protocolo = protocolo
        self.identificador_vendedor = identificador_vendedor
        self.descritor_pre_definido_2 = gateway_pre_definido_2
        self.descritor_pre_definido_3 = gateway_pre_definido_3
        self.descritor_pre_definido_4 = gateway_pre_definido_4
        self.descritor_pre_definido_5 = gateway_pre_definido_5
        self.descritor_pre_definido_6 = gateway_pre_definido_6
        self.__dict__.update(kwargs)


class Transportadora_fob:
    def __init__(self, nome, razao_social, cnpj, **kwargs):
        self.nome = nome
        self.razao_social = razao_social
        self.cnpj = cnpj
        self.__dict__.update(kwargs)


class Transacao:
    def __init__(self, transacao_id, numero_autorizacao, nsu, mensagem_retorno, adicional_3=None, adicional_4=None,
                 **kwargs):
        self.transacao_id = transacao_id
        self.numero_autorizacao = numero_autorizacao
        self.nsu = nsu
        self.mensagem_retorno = mensagem_retorno
        self.adicional_3 = adicional_3
        self.adicional_4 = adicional_4
        self.__dict__.update(kwargs)


class Usuario:
    def __init__(self, codigo_referencia, nome, razao_social, cpf, rg, data_nascimento, cnpj, sexo, email, orgao,
                 RegistroEstadual, TelefoneResidencial, TelefoneCelular, Endereco: dict, EnderecoEntrega: dict,
                 origem_cadastro, id=None, **kwargs):
        self.codigo_referencia = codigo_referencia
        self.id = id
        self.nome = nome
        self.razao_social = razao_social
        self.cpf = cpf
        self.rg = rg
        self.data_nascimento = data_nascimento
        self.cnpj = cnpj
        self.sexo = sexo
        self.email = email
        self.orgao = orgao
        self.RegistroEstadual = RegistroEstadual
        self.TelefoneResidencial = TelefoneResidencial
        self.TelefoneCelular = TelefoneCelular
        self.origem_cadastro = origem_cadastro
        self.Endereco: Endereco = Endereco_Usuario(**Endereco)
        self.EnderecoEntrega: EnderecoEntrega = Endereco_Entrega(**EnderecoEntrega)
        self.__dict__.update(kwargs)


class Endereco_Usuario:
    def __init__(self, cep, logradouro, numero, complemento, bairro, cidade, codigo_ibge, estado, pais, referencia,
                 descricao, tipo_logradouro, **kwargs):
        self.cep = cep
        self.logradouro = logradouro
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.cidade = cidade
        self.codigo_ibge = codigo_ibge
        self.estado = estado
        self.pais = pais
        self.referencia = referencia
        self.descricao = descricao
        self.tipo_logradouro = tipo_logradouro
        self.__dict__.update(kwargs)


class Endereco_Entrega:
    def __init__(self, cep, logradouro, numero, complemento, bairro, cidade, codigo_ibge, estado, pais, referencia,
                 descricao, tipo_logradouro):
        self.cep = cep
        self.logradouro = logradouro
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.cidade = cidade
        self.codigo_ibge = codigo_ibge
        self.estado = estado
        self.pais = pais
        self.referencia = referencia
        self.descricao = descricao
        self.tipo_logradouro = tipo_logradouro


class Pagamento:
    def __init__(self, opcao_pagamento, opcao_pagamento_erp, condicao_pagamento_erp, parcelas, bandeira,
                 tabela_financiamento_rsvarejo, tipo_venda_rsvarejo, canal_venda_id, canal_venda, numero_cupom,
                 valor_cupom, codigo_compra, codigo_pedido_canal, data_movimento, codigo_mercado, titulos: list,
                 valor_pontos=None):
        self.opcao_pagamento = opcao_pagamento
        self.opcao_pagamento_erp = opcao_pagamento_erp
        self.condicao_pagamento_erp = condicao_pagamento_erp
        self.parcelas = parcelas
        self.bandeira = bandeira
        self.tabela_financiamento_rsvarejo = tabela_financiamento_rsvarejo
        self.tipo_venda_rsvarejo = tipo_venda_rsvarejo
        self.canal_venda_id = canal_venda_id
        self.canal_venda = canal_venda
        self.numero_cupom = numero_cupom
        self.valor_cupom = valor_cupom
        self.valor_pontos = valor_pontos
        self.codigo_compra = codigo_compra
        self.codigo_pedido_canal = codigo_pedido_canal
        self.data_movimento = data_movimento
        self.codigo_mercado = codigo_mercado
        self.titulos: list[Titulo] = [Titulo(**t) for t in titulos]


class Titulo:
    def __init__(self, parcela, valor, data_vencimento, data_baixa, data_pago, codigo_retorno, descricao_retorno,
                 valor_abatimento_concebido, desconto_concebido, valor_iof_recolhido, valor_creditado, valor_sacado,
                 outros_valores, outros_creditos):
        self.parcela = parcela
        self.valor = valor
        self.data_vencimento = data_vencimento
        self.data_baixa = data_baixa
        self.data_pago = data_pago
        self.codigo_retorno = codigo_retorno
        self.descricao_retorno = descricao_retorno
        self.valor_abatimento_concebido = valor_abatimento_concebido
        self.desconto_concebido = desconto_concebido
        self.valor_iof_recolhido = valor_iof_recolhido
        self.valor_creditado = valor_creditado
        self.valor_sacado = valor_sacado
        self.outros_valores = outros_valores
        self.outros_creditos = outros_creditos


class Itens:
    def __init__(self, sku_principal, sku_variacao, sku_reference, hierarquia_variacao, is_restock,
                 codigo_externo_restock, ean, unidade_medida, quantidade, value, valor_desconto, altura, comprimento,
                 largura, peso, volume, filial_expedicao, filial_faturamento, cnpj_filial_venda, valor_taxa_servico,
                 impostos = None, codigo_externo_filial=None, filial=None, name=None, name_variation=None, valor_frete=None,
                 percentual_comissao=None, valor_comissao=None, valor_comissao_frete=None, tipo_anuncio=None, **kwargs):
        self.sku_principal = sku_principal
        self.sku_variacao = sku_variacao
        self.sku_reference = sku_reference
        self.name = name
        self.name_variation = name_variation
        self.hierarquia_variacao = hierarquia_variacao
        self.is_restock = is_restock
        self.codigo_externo_restock = codigo_externo_restock
        self.ean = ean
        self.unidade_medida = unidade_medida
        self.quantidade = quantidade
        self.value = value
        self.valor_desconto = valor_desconto
        self.altura = altura
        self.comprimento = comprimento
        self.largura = largura
        self.peso = peso
        self.volume = volume
        self.filial_expedicao = filial_expedicao
        self.filial_faturamento = filial_faturamento
        self.cnpj_filial_venda = cnpj_filial_venda
        self.valor_taxa_servico = valor_taxa_servico
        self.codigo_externo_filial = codigo_externo_filial
        self.filial = filial
        self.valor_frete = valor_frete
        self.percentual_comissao = percentual_comissao
        self.valor_comissao = valor_comissao
        self.valor_comissao_frete = valor_comissao_frete
        self.tipo_anuncio = tipo_anuncio
        self.impostos = Impostos(**impostos)
        self.__dict__.update(kwargs)


class Itens_brinde:
    def __init__(self, preco_atual, quantidade, desconto, produto_id, codigo_externo, identificador_produto,
                 codigo_referencia, nome_produto, unidade_produto, identificador_atributo,
                 identificador_opcao_atributo, filial_expedicao, filial_faturamento, **kwargs):
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
        self.__dict__.update(kwargs)


class Itens_personalizados:
    def __init__(self, id, preco_liquido, preco_bruto, texto, **kwargs):
        self.id = id
        self.preco_liquido = preco_liquido
        self.preco_bruto = preco_bruto
        self.texto = texto
        self.__dict__.update(kwargs)


class Forma_pagamento_parceiro:
    def __init__(self, tipo_pagamento, bandeira, codigo_autorizacao, codigo_status, codigo_transacao, data_criacao,
                 data_aprovacao, detalhe_status, status, valor_frete, valor_parcela, valor_pedido, valor_total_pago,
                 parcelas, descricao_condicao_pagamento_lojista=None, codigo_externo_condicao_pagamento_lojista=None, **kwargs):
        self.tipo_pagamento = tipo_pagamento
        self.bandeira = bandeira
        self.codigo_autorizacao = codigo_autorizacao
        self.codigo_status = codigo_status
        self.codigo_transacao = codigo_transacao
        self.data_criacao = data_criacao
        self.data_aprovacao = data_aprovacao
        self.detalhe_status = detalhe_status
        self.status = status
        self.valor_frete = valor_frete
        self.valor_parcela = valor_parcela
        self.valor_pedido = valor_pedido
        self.valor_total_pago = valor_total_pago
        self.parcelas = parcelas
        self.descricao_condicao_pagamento_lojista = descricao_condicao_pagamento_lojista
        self.codigo_externo_condicao_pagamento_lojista = codigo_externo_condicao_pagamento_lojista
        self.__dict__.update(kwargs)


class Forma_envio_parceiro:
    def __init__(self, codigo_rastreio, forma_envio, tipo_envio, status_envio, data_previsao_postagem, modo_envio, plp,
                 rota, mega_rota):
        self.codigo_rastreio = codigo_rastreio
        self.forma_envio = forma_envio
        self.tipo_envio = tipo_envio
        self.status_envio = status_envio
        self.data_previsao_postagem = data_previsao_postagem
        self.modo_envio = modo_envio
        self.plp = plp
        self.rota = rota
        self.mega_rota = mega_rota


class Pedido_nota_fiscal:
    def __init__(self, nota_fiscal_id, pedido_id, num_fiscal, num_serie, access_key, valor_total_nota, data_emissao,
                 dt_cadastro, xml, link_danfe, link_xml, quantidade_volume):
        self.nota_fiscal_id = nota_fiscal_id
        self.pedido_id = pedido_id
        self.num_fiscal = num_fiscal
        self.num_serie = num_serie
        self.access_key = access_key
        self.valor_total_nota = valor_total_nota
        self.data_emissao = data_emissao
        self.dt_cadastro = dt_cadastro
        self.xml = xml
        self.link_danfe = link_danfe
        self.link_xml = link_xml
        self.quantidade_volume = quantidade_volume

class Impostos:
    def __init__(self, valor_substituicao_tributaria = None, iva = None, icms_intraestadual = None, icms_interestadual = None, valor_icms_interestadual = None, percentual_ipi = None, valor_ipi = None, **kwargs):
        self.valor_substituicao_tributaria: float = valor_substituicao_tributaria
        self.iva: float = iva
        self.icms_intraestadual: float = icms_intraestadual
        self.icms_interestadual: float = icms_interestadual
        self.valor_icms_interestadual: float = valor_icms_interestadual
        self.percentual_ipi: float = percentual_ipi
        self.valor_ipi: float = valor_ipi
        self.__dict__.update(kwargs)

# endregion
