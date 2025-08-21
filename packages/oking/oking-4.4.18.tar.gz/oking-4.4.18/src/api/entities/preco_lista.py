from typing import List
from datetime import datetime


class Escopo:
    def __init__(self, tipo_escopo: int, codigos_escopo: List[str], **kwargs):
        self.tipo_escopo: int = tipo_escopo
        self.codigos_escopo: List[str] = codigos_escopo
        self.__dict__.update(kwargs)


class ListaPreco:
    def __init__(self, descricao_lista_preco: str, codigo_lista_preco: str, codigo_filial: str, data_inicial: datetime, data_final: datetime, ativo: bool, prioridade: int, escopo: Escopo, calcula_ipi: str, **kwargs):
        self.descricao_lista_preco: str = descricao_lista_preco
        self.codigo_lista_preco: str = codigo_lista_preco
        self.codigo_filial: str = codigo_filial
        self.data_inicial: datetime = data_inicial
        self.data_final: datetime = data_final
        self.ativo: bool = bool(ativo)
        self.prioridade: int = prioridade
        self.escopo: Escopo = escopo
        self.calcula_ipi: str = calcula_ipi
        self.__dict__.update(kwargs)
