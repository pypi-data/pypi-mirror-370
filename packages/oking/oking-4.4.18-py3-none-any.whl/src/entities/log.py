
class Log:
    def __init__(self, mensagem: str,  identificador: str, nome_job: str, integracao_id: int, log_tipo: str,
                 seller: int):
        self.p_mensagem: str = mensagem[0:2000] if mensagem is not None else ''
        self.p_integracao_id: int = integracao_id
        self.p_identificador: str = identificador
        # self.data_hora: str = data_hora
        self.p_nomeJob: str = nome_job
        self.p_tipo: str = log_tipo  # Tipo: E-erro, V-validacao, I-informacao, X-execucao
        self.p_cliente_id:  int = seller
