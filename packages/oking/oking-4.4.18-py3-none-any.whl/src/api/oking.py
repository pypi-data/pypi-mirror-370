from datetime import datetime

import requests as req
import jsonpickle
import logging

logger = logging.getLogger()


class Module:
    def __init__(self, executar_query_semaforo: str, job: str, comando_sql: str, unidade_tempo: str,
                 tempo_execucao: int, old_version='N', ultima_execucao: datetime = '', ativo: str = 'N',
                 query_final: str = 'S', semaforo_sql: str = 'N', enviar_logs_slack: bool = False,
                 enviar_logs_debug: bool = False, **kwargs):
        self.job_name = job
        self.ativo = ativo
        self.executar_query_semaforo = executar_query_semaforo
        self.sql = comando_sql
        self.time_unit = unidade_tempo
        self.time = tempo_execucao
        self.query_final = query_final
        self.exists_sql = semaforo_sql
        self.send_logs = enviar_logs_slack
        self.enviar_logs_debug = enviar_logs_debug
        self.ultima_execucao = ultima_execucao
        self.old_version = old_version
        self.__dict__.update(kwargs)


def get(url: str, params: dict = None):
    response = req.get(url, params)
    if str(response.status_code).startswith('2'):
        return jsonpickle.decode(response.content)
    else:
        logger.error(f'Erro ao executar GET: {url} | Code: {response.status_code} | {response.content}')

    return None
