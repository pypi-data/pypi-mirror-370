from typing import List


class PlanoPagamentoCliente:
    def __init__(self, codigo_cliente, formas_pagamento, **kwargs):
        self.codigo_cliente: str = codigo_cliente
        self.formas_pagamento: List[str] = formas_pagamento
        self.__dict__.update(kwargs)
