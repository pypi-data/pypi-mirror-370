from datetime import datetime
import logging
import src.api.okinghub as api_okinghub
from src.entities.log import Log
import src.api.slack as slack
import src
from src.log_types import LogType
from threading import Lock
logger = logging.getLogger()
lock = Lock()


class OnlineLogger:

    @staticmethod
    def send_log(job_name: str, send_slack: bool, enviar_log_debug: bool, message: str, log_type: LogType,
                 api_log_identifier: str = ''):

        # Tipos de log que sempre exigem envio para o oking
        # always_oking_types = {'INFO', 'WARNING', 'ERROR', 'EXEC'}

        always_oking_types = {LogType.INFO, LogType.WARNING, LogType.ERROR, LogType.EXEC}

        # Determina se deve enviar para o oking
        # [TODOS] - devem enviar. Somente DEBUG, que utilizara o parametro do Módulo
        envia_log_oking = enviar_log_debug or (log_type in always_oking_types)

        # print(f'=== log_type: {log_type}, type: {type(log_type)}')

        tipo_log = 'I'
        # log_type = log_type.upper()  # Converte para maiúsculas e sobrescreve
        if log_type == LogType.INFO:
            logger.info(f'{job_name} | {message}')
            tipo_log = 'I'  # INFORMAÇÃO
        elif log_type == LogType.WARNING:
            logger.warning(f'{job_name} | {message}')
            tipo_log = 'V'  # VALIDAÇÃO
        elif log_type == LogType.DEBUG:
            logger.warning(f'{job_name} | {message}')
            tipo_log = 'D'  # DEBUG - Logs para acompanhamento pelos Devesenvolvedores
        elif log_type == LogType.ERROR:
            logger.error(f'{job_name} | {message}')
            tipo_log = 'E'  # ERRO
        elif log_type == LogType.EXEC:
            logger.info(f'{job_name} | {message}')
            tipo_log = 'X'  # EXECUÇÃO - Monitora a execução de JOB mesmo quando não tem registros
        else:
            logger.warning(f'{job_name} | Tipo de log desconhecido: {log_type}')
            tipo_log = 'U'  # UNKNOWN

        # Sempre enviar para o Slack se for do Tipo ERRO
        # if log_type == LogType.ERROR:
        #        slack.post_message(f'{job_name} | {message} | Integracao {src.client_data.get("integracao_id")} | '
        #                           f'API {src.client_data.get("url_api")}')

        if envia_log_oking:
            api_okinghub.post_log(
                Log(
                    f'{message}',
                    api_log_identifier,
                    job_name,
                    src.client_data.get("integracao_id"),
                    tipo_log,
                    src.client_data.get("seller_id")
                )
            )

    # Log(f'Oking inicializando', '', 'INICIALIZACAO',f'{client_data.get("integracao_id")}', 'I',
    # F'{client_data.get("seller_id")}')


def send_execution_notification(job_config: dict) -> None:
    with lock:
        # Exibe mensagem monstrando que a Thread foi Iniciada
        logger.info(f'==== THREAD INICIADA -job: ' + job_config.get('job_name'))
        # Formata a data para Melhorar a Visualização
        data_desativacao_formatada = job_config.get("execution_start_time").replace('T', ' ')
        data_objeto = datetime.strptime(data_desativacao_formatada, '%d//%m/%Y %H:%M:%S')

        mensagem = f'Oking em execucao desde {data_objeto} com {job_config.get("job_qty")}' \
                   f' jobs para o cliente {src.client_data.get("integracao_nome")} - Versão {src.version}'
        api_okinghub.post_log(
            Log(mensagem,
                'OKING_EXECUCAO',
                'OKING_EXECUCAO',
                src.client_data.get("integracao_id"),
                'X',
                src.client_data.get("seller_id"))
                              )
# online_logger = OnlineLogger.send_log
# online_logger(job_config.get('job_name'), job_config.get('enviar_logs'), False, f'', LogType.WARNING, '')
# online_logger(job_config.get('job_name'), job_config.get('enviar_logs'), False, f'', LogType.INFO, '')
# online_logger(job_config.get('job_name'), job_config.get('enviar_logs'), False, f'', LogType.ERROR, '')
#
#
