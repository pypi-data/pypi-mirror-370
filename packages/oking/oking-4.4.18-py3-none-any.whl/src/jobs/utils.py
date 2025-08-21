import logging
import os
from datetime import datetime

import src
import src.database.connection as database
from src.log_types import LogType
from src.jobs.system_jobs import OnlineLogger

logger = logging.getLogger()
send_log = OnlineLogger.send_log


def executa_comando_sql(db_config, job_config):
    conexao = database.Connection(db_config)
    conn = conexao.get_conect()
    cursor = conn.cursor()
    if db_config.db_type.lower() == "firebird":
        semaforo_sql = db_config.semaforo_sql.replace("openk_semaforo.", "")
    else:
        semaforo_sql = db_config.semaforo_sql

    if src.print_payloads:
        print(semaforo_sql)

    try:
        logger.info(job_config.get("job_name") + " ===============================")
        logger.info(job_config.get("job_name") + " == Executando Query Semáforo ==")
        cursor.execute(semaforo_sql)
        logger.info(job_config.get("job_name") + " == Query Semáforo Executada  ==")
        logger.info(job_config.get("job_name") + " ===============================")

        # Fecha o Cursor e a Conexão
        cursor.close()
        conn.commit()
        conn.close()

    except Exception as ex:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f"Erro ao executar Comando SQL: {ex}",
            LogType.WARNING,
            job_config.get("job_name"),
        )


def setup_logger(job_name=""):
    # Defina o nome da pasta de logs e a subpasta com o nome do job
    log_dir = "logs"
    # job_log_dir = os.path.join(log_dir, job_name)
    if job_name == "":
        job_name = "oking"
    # Crie as pastas se não existirem
    os.makedirs(log_dir, exist_ok=True)

    # Defina o nome do arquivo com base no nome do job e na data/hora atuais
    file_name = f"log_{job_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    file_path = os.path.join(log_dir, file_name)

    # Crie um logger específico
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Remova handlers existentes para evitar duplicações
    if logger.hasHandlers():
        logger.handlers.clear()

    # Crie um handler para o arquivo de log
    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(logging.DEBUG)

    # Crie um handler para a saída padrão (console)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)

    # Defina o formato do log
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Adicione os handlers ao logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    # Mensagem inicial para indicar a criação do novo arquivo de log
    logger.info(
        f"Arquivo de log criado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    return logger
