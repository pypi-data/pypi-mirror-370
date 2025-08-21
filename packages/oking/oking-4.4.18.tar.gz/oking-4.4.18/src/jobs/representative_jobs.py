import logging
import threading
from typing import List
import src
from src.jobs.utils import executa_comando_sql
import src.database.connection as database
from src.api.entities.representante import Representante, RegiaoVenda
from src.database import queries
from src.database.queries import IntegrationType
from src.database.utils import DatabaseConfig
import src.database.utils as utils
# from src.entities.product import Product
# from src.entities.photos_sku import PhotosSku
import src.api.okvendas as api_okvendas
from src.jobs.system_jobs import OnlineLogger
from src.database.entities.representative import Representative
from src.log_types import LogType
from threading import Lock

lock = Lock()
logger = logging.getLogger()
send_log = OnlineLogger.send_log


def job_representative(job_config: dict):
    with lock:
        """
        Job para inserir representantes do produto no banco semáforo
        Args:
            job_config_dict: Configuração do job
        """
        logger.info(job_config.get('job_name') + f' | Executando na Thread {threading.current_thread()}')
        db_config = utils.get_database_config(job_config)
        # LOG de Inicialização do Método - Para acompanhamento de execução
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Enviar Representante- Iniciado',
            LogType.EXEC,
            'REPRESENTANTE')
        if db_config.sql is None:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Comando sql para inserir os representantes no semaforo nao encontrado',
                LogType.WARNING,
                'REPRESENTANTE')
            return
        if job_config['executar_query_semaforo'] == 'S':
            executa_comando_sql(db_config, job_config)
        try:
            db_representative = query_list_representative(job_config, db_config)
            if not insert_update_semaphore_representative(job_config, db_config, db_representative):
                send_log(
                    job_config.get('job_name'),
                    job_config.get('enviar_logs'),
                    job_config.get('enviar_logs_debug'),
                    f'Nao foi possivel inserir os representantes no banco semaforo',
                    LogType.ERROR,
                    'REPRESENTANTE')
                return

            api_representative = [Representante(
                codigo_externo=r.sku_code,
                nome=r.name,
                telefone_celular=r.mobile_phone,
                login=r.login,
                password=r.password,
                supervisor=r.supervisor,
                ativar_representante=r.representative_active,
                email=r.email,
                regiao_venda=RegiaoVenda(r.rv_name, str(r.rv_sku_code))) for r in db_representative]

            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Enviando os representantes via api okvendas',
                LogType.INFO,
                'REPRESENTANTE')
            total = len(api_representative)
            page = 100
            limit = 100 if total > 100 else total
            offset = 0

            partial_representative = api_representative[offset:limit]
            while limit <= total:
                response = api_okvendas.put_representative(partial_representative)
                for res in response:
                    identificador =\
                        [i.codigo_externo for i in api_representative if i.codigo_externo == res.identifiers[0]][0]
                    if res.status == 1:
                        if protocol_semaphore_representative(job_config, db_config, identificador):
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'Representante {identificador} protocolado no banco semaforo',
                                LogType.INFO,
                                'REPRESENTANTE')
                        else:
                            send_log(
                                job_config.get('job_name'),
                                job_config.get('enviar_logs'),
                                job_config.get('enviar_logs_debug'),
                                f'Falha ao protocolar o representante {identificador}',
                                LogType.WARNING,
                                'REPRESENTANTE')

                limit = limit + page
                offset = offset + page
                partial_representative = api_representative[offset:limit]

        except Exception as ex:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Erro {str(ex)}',
                LogType.ERROR,
                'REPRESENTANTE')


def query_list_representative(job_config: dict, db_config: DatabaseConfig) -> List[Representative]:
    """
        Consultar no banco semáforo os representantes

        Args:
            job_config_dict: Configuração do job
            db_config: Configuração do banco de dados

        Returns:
        Lista de representantes
        """
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        if src.print_payloads:
            print(db_config.sql)
        cursor.execute(db_config.sql)
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        results = list(dict(zip(columns, row)) for row in rows)
        cursor.close()
        conn.close()
        if len(results) > 0:
            lists = [Representative(**p) for p in results]
            return lists

    except Exception as ex:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f' Erro ao consultar representantes no banco semaforo: {str(ex)}',
            LogType.ERROR,
            'REPRESENTANTE')

    return []


def insert_update_semaphore_representative(job_config: dict, db_config: DatabaseConfig,
                                           lists: List[Representative]) -> bool:
    """
    Insere os representantes no banco semáforo
    Args:
        job_config_dict: Configuração do job
        db_config: Configuracao do banco de dados
        lists: Lista de representantes

    Returns:
        Boleano indicando se foram inseridos 1 ou mais registros
    """
    params = [(li.sku_code, ' ', IntegrationType.REPRESENTANTE.value, 'SUCESSO') for li in lists]

    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        for p in params:
            cursor.execute(queries.get_insert_update_semaphore_command(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, list(p)))
        count = cursor.rowcount
        cursor.close()
        conn.commit()
        conn.close()
        return count > 0

    except Exception as ex:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f' Erro ao consultar representantes no banco semaforo: {str(ex)}',
            LogType.ERROR,
            'REPRESENTANTE')

    return False


def protocol_semaphore_representative(job_config: dict, db_config: DatabaseConfig, identifier: str) -> bool:
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        if identifier is not None:
            cursor.execute(queries.get_protocol_semaphore_id_command(db_config.db_type),
                           queries.get_command_parameter(db_config.db_type, ['SUCESSO', identifier]))
        count = cursor.rowcount
        cursor.close()
        conn.commit()
        conn.close()
        return count > 0

    except Exception as ex:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f' Erro ao protocolar representante no banco semaforo: {str(ex)}',
            LogType.ERROR,
            'REPRESENTANTE')
