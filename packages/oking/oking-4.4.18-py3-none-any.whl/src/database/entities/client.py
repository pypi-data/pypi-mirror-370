from datetime import datetime


class Client:
    def __init__(self, nome, razao_social, cpf, cnpj, email, telefone_residencial, telefone_celular, cep,
                 tipo_logradouro, logradouro, numero, complemento, bairro, cidade, estado, referencia,
                 cliente_erp, direcao, data_sincronizacao, codigo_ibge, inscricao_estadual, compra_liberada,
                 site_pertencente, data_bloqueio, tipo_pessoa, limite_credito, codigo_representante, **kwargs):
        self.belonging_site = site_pertencente
        self.blocked_date = data_bloqueio
        self.name: str = nome
        self.company_name: str = razao_social
        self.cpf: str = cpf.replace(" ", "") if cpf is not None else None
        self.cnpj: str = cnpj.replace(" ", "") if cnpj is not None else None
        self.email: str = email
        self.residential_phone: str = telefone_residencial
        self.mobile_phone: str = telefone_celular
        self.zipcode: str = cep
        self.address_type: str = tipo_logradouro
        self.address: str = logradouro
        self.number: str = numero
        self.complement: str = complemento
        self.neighbourhood: str = bairro
        self.city: str = cidade
        self.state: str = estado
        self.reference: str = referencia
        self.client_erp: str = cliente_erp
        self.direction: str = direcao
        self.sync_date: datetime = data_sincronizacao
        self.ibge_code: str = codigo_ibge
        self.state_registration: str = inscricao_estadual
        self.purchase_released: bool = compra_liberada
        self.person_type: str = tipo_pessoa
        self.credit_limit: str = limite_credito
        self.representative_code: str = codigo_representante
        self.__dict__.update(kwargs)
