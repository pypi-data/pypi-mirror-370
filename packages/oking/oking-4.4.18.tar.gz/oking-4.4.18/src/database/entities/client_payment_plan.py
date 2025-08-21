from typing import List


class ClientPaymentPlan:
    def __init__(self, codigo_cliente, formas_pagamento, **kwargs):
        self.code_client: str = codigo_cliente
        self.payment_methods: List[str] = formas_pagamento
        self.__dict__.update(kwargs)
