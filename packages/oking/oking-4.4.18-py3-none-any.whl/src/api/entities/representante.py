class RegiaoVenda:
    nome: str
    codigo_externo: str

    def __init__(self, rv_nome: str, rv_codigo_externo: str) -> None:
        self.nome = rv_nome
        self.codigo_externo = rv_codigo_externo

class Representante:
    def __init__(self, codigo_externo, nome, telefone_celular, login,
                 password, supervisor,ativar_representante, email, regiao_venda: RegiaoVenda):
        self.codigo_externo: str = codigo_externo
        self.nome: str = nome
        self.telefone_celular: str = telefone_celular
        self.login: str = login
        self.password: str = password
        self.supervisor: bool = supervisor
        self.ativar_representante: bool = ativar_representante
        self.email: str = email
        self.regiao_venda = regiao_venda