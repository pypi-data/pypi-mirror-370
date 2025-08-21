from datetime import datetime


class Transportadora_Fob_Parceiro:
    def __init__(self, codigo_externo, nome, razao_social: str, cnpj: str, data_aprovacao: datetime, data_desativacao: datetime, **kwargs):
        self.codigo_externo: str = codigo_externo
        self.nome: str = nome
        self.razao_social: str = razao_social
        self.cnpj: str = cnpj
        self.data_aprovacao = data_aprovacao
        self.data_desativacao = data_desativacao
        self.__dict__.update(kwargs)



