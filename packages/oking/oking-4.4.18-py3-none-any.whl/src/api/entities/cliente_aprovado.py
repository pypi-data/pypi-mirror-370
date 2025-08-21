from typing import List, Dict
from datetime import datetime


class Address:
    zipcode: str
    phone: str
    description: str
    type: str
    address: str
    number: str
    complement: str
    reference: str
    neighbourhood: str
    city: str
    ibge_code: str
    state: str
    country: str
    id: int

    def __init__(self, cep: str, fone_contato: str, descricao_endereco: str, tipo_logradouro: str, endereco: str, numero: str, complemento: str, referencia_entrega: str, bairro: str, cidade: str, codigo_ibge: str,
                 estado: str, pais: str, id: int, **kwargs) -> None:
        self.zipcode = cep
        self.phone = fone_contato
        self.description = descricao_endereco
        self.type = tipo_logradouro
        self.address = endereco
        self.number = numero
        self.complement = complemento
        self.reference = referencia_entrega
        self.neighbourhood = bairro
        self.city = cidade
        self.ibge_code = codigo_ibge
        self.state = estado
        self.country = pais
        self.id = id
        self.__dict__.update(kwargs)


class ApprovedClient:
    id: int
    corporate_name: str
    person_type: str
    cpf: str
    cnpj: str
    municipal_registration: str
    state_registration: str
    mobile_phone: str
    home_phone: str
    erp_code: str
    deactivated_date: datetime
    buy_allowed: bool
    credit_limit: float
    requested_credit_limit: float
    activity_line: str
    representative_code: str
    segment: str
    login: str
    name: str
    sex: str
    email: str
    domain: str
    protocol: str
    addresses: List[Address]
    constitution_date: datetime
    updated_date: datetime
    register_date: datetime
    external_integration_date: datetime
    photo: str
    address_id: int

    def __init__(self, id: int, razao_social: str, tipo_pessoa: str, cpf: str, cnpj: str, inscricao_municipal: str, inscricao_estadual: str, fone_celular: str, fone_residencial: str,
                 codigo_referencia: str, data_desativacao: str, compra_liberada: bool, limite_credito: float, limite_credito_solicitado: float, ramo_atividade: str, codigo_representante: str,
                 segmento: str, login: str, nome: str, sexo: str, email: str, domain: str, protocolo: str, enderecos: List[Dict], data_constituicao: datetime, data_alteracao: str,
                 data_cadastro: str, data_integracao_externa: str, foto: str, endereco_id: int, origem_cadastro: str, **kwargs) -> None:
        self.id = id
        self.corporate_name = razao_social
        self.person_type = tipo_pessoa
        self.cpf = cpf.replace(" ", "") if cpf is not None else None
        self.cnpj = cnpj.replace(" ", "") if cnpj is not None else None
        self.municipal_registration = inscricao_municipal
        self.state_registration = inscricao_estadual
        self.mobile_phone = fone_celular
        self.home_phone = fone_residencial
        self.erp_code = codigo_referencia
        self.deactivated_date = data_desativacao if data_desativacao is None else datetime.strptime(data_desativacao.replace('T', ' '), '%Y-%m-%d %H:%M:%S')
        self.buy_allowed = compra_liberada
        self.credit_limit = limite_credito
        self.requested_credit_limit = limite_credito_solicitado
        self.activity_line = ramo_atividade
        self.representative_code = codigo_representante
        self.segment = segmento
        self.login = login
        self.name = nome
        self.sex = sexo
        self.email = email
        self.domain = domain
        self.protocol = protocolo
        self.addresses = [Address(**e) for e in enderecos] if enderecos is not None else []
        self.constitution_date = data_constituicao
        self.updated_date = data_alteracao if data_alteracao is None else datetime.strptime(data_alteracao.replace('T', ' '), '%Y-%m-%d %H:%M:%S')
        self.register_date = data_cadastro if data_cadastro is None else datetime.strptime(data_cadastro.replace('T', ' '), '%Y-%m-%d %H:%M:%S')
        self.external_integration_date = data_integracao_externa if data_integracao_externa is None else datetime.strptime(data_integracao_externa.replace('T', ' '), '%Y-%m-%d %H:%M:%S')
        self.photo = foto
        self.address_id = endereco_id
        self.registration_origin = origem_cadastro
        self.__dict__.update(kwargs)


class ApprovedClientResponse:
    total: int
    data: List[ApprovedClient]

    def __init__(self, total: int, data: List[Dict], **kwargs) -> None:
        self.total = total
        self.data = [ApprovedClient(**d) for d in data] if data is not None else []
        self.__dict__.update(kwargs)
