class Representative:
    def __init__(self, codigo_externo, nome, telefone_celular, login,
                 password, supervisor, ativar_representante, email,
                 rv_nome, rv_codigo_externo, **kwargs):
        self.sku_code: str = codigo_externo
        self.name: str = nome
        self.mobile_phone: str = telefone_celular
        self.login: str = login
        self.password: str = password
        self.supervisor: bool = supervisor
        self.representative_active: bool = ativar_representante
        self.email: str = email
        self.rv_name: str = rv_nome
        self.rv_sku_code: float = rv_codigo_externo
        self.__dict__.update(kwargs)
