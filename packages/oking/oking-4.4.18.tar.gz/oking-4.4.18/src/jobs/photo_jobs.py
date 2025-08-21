import logging
from typing import List

import PySimpleGUI as sg
from src.jobs.utils import executa_comando_sql

import src
import src.api.api_mplace as api_Mplace
import src.api.okvendas as api_okVendas
import src.database.connection as database
import src.database.utils as utils
from src.api.entities.foto import Foto
from src.api.entities.foto_sku import Foto_Sku, Foto_Produto_Sku
from src.database import queries
from src.database.queries import IntegrationType
from src.database.utils import DatabaseConfig
from src.jobs.system_jobs import OnlineLogger
from src.log_types import LogType
from threading import Lock
logger = logging.getLogger()
send_log = OnlineLogger.send_log
lock = Lock()


def job_send_photo(job_config: dict):
    with lock:
        db_config = utils.get_database_config(job_config)
        # Exibe mensagem monstrando que a Thread foi Iniciada
        logger.info(f'==== THREAD INICIADA -job: ' + job_config.get('job_name'))

        # LOG de Inicialização do Método - Para acompanhamento de execução
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Foto - Iniciado',
            LogType.EXEC,
            'FOTO')

        if db_config is None:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Comando sql para Fotos nao encontrado',
                LogType.WARNING,
                'FOTO')

        if job_config['executar_query_semaforo'] == 'S':
            executa_comando_sql(db_config, job_config)

        photos = query_photos_erp(job_config, db_config)
        api_photos = []
        try:
            for photo in photos:
                if api_photos.__len__() < 3:
                    if src.client_data['operacao'].lower().__contains__('okvendas'):
                        if photo.base64_foto is not None:
                            api_photos.append(photo)
                        continue
                    api_photos.append(photo)
                else:
                    if src.client_data['operacao'].lower().__contains__('mplace'):
                        response = api_Mplace.post_photo_mplace(api_photos, job_config, db_config)
                        api_photos = []
                    elif src.client_data['operacao'].lower().__contains__('okvendas'):
                        response = api_okVendas.put_photos_sku(api_photos)
                        api_photos = []
                    # if response is not None:
                    if response or response is None:
                        # validade_response_photos(response, db_config, job_config)
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Fotos enviadas com sucesso',
                            LogType.INFO,
                            'FOTO')
                        update_foto(db_config, photo.codigo_erp_sku)
                    else:
                        send_log(
                            job_config.get('job_name'),
                            job_config.get('enviar_logs'),
                            job_config.get('enviar_logs_debug'),
                            f'Falha ao enviar fotos para api okvendas: {response}',
                            LogType.ERROR,
                            'FOTO')
            if api_photos.__len__() > 0:
                if src.client_data['operacao'].lower().__contains__('mplace'):
                    response = api_Mplace.post_photo_mplace(api_photos, job_config, db_config)
                elif src.client_data['operacao'].lower().__contains__('okvendas'):
                    response = api_okVendas.put_photos_sku(api_photos)
                # if response is not None:
                if response or response is None:
                    # validade_response_photos(response, db_config, job_config)
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f'Fotos enviadas com sucesso',
                        LogType.INFO,
                        'FOTO')
                else:
                    send_log(
                        job_config.get('job_name'),
                        job_config.get('enviar_logs'),
                        job_config.get('enviar_logs_debug'),
                        f'Falha ao enviar fotos para api okvendas: {response}',
                        LogType.ERROR,
                        'FOTO')
        except Exception as e:
            send_log(
                job_config.get('job_name'),
                job_config.get('enviar_logs'),
                job_config.get('enviar_logs_debug'),
                f'Falha ao enviar fotos : {str(e)}',
                LogType.ERROR,
                'FOTO')


def query_photos_erp(job_config: dict, db_config: DatabaseConfig):
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    photo = []
    try:
        if db_config.is_oracle():
            conn.outputtypehandler = database.output_type_handler
        newsql = utils.final_query(db_config)
        conexao = database.Connection(db_config)
        conn = conexao.get_conect()
        if src.print_payloads:
            print(newsql)
        cursor.execute(newsql.replace(';', ''))
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        cursor.close()
        conn.close()
        if len(results) > 0:
            if src.client_data['operacao'].lower().__contains__('mplace'):
                photo = [Foto(**p) for p in results]
            elif src.client_data['operacao'].lower().__contains__('okvendas'):
                photo = [Foto_Produto_Sku(**p) for p in results]
    except Exception as ex:
        logger.error(f' ')
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Erro ao consultar pedidos enviados no banco: {str(ex)}',
            LogType.ERROR,
            'FOTO')

    return photo


def update_foto(db_config: DatabaseConfig, product_code: str):
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        cursor.execute(queries.update_foto_command(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type, [product_code]))
        cursor.close()
        conn.commit()
        conn.close()
    except Exception as ex:
        print(f'Erro {ex} ao atualizar a tabela do pedido {product_code}')
        raise ex


def validade_response_photos(identificador, identificador2, mensagem, db_config, job_config):

    conexao = database.Connection(db_config)
    conn = conexao.get_conect()
    cursor = conn.cursor()

    try:
        cursor.execute(queries.get_insert_update_semaphore_command(db_config.db_type),
                       queries.get_command_parameter(db_config.db_type, [identificador, identificador2,
                                                                         IntegrationType.FOTO.value,
                                                                         mensagem]))
        # atualizados.append(response['identificador'])
    except Exception as e:
        send_log(
            job_config.get('job_name'),
            job_config.get('enviar_logs'),
            job_config.get('enviar_logs_debug'),
            f'Erro inserir Foto: {identificador}, Erro: {str(e)}',
            LogType.ERROR,
            f'{identificador}-{identificador2}')

    cursor.close()
    conn.commit()
    conn.close()
