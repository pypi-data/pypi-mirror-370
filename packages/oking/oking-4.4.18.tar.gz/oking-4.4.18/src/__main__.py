import threading
import src
from time import sleep
import schedule
import logging
from src import interface_grafica
from src.jobs import product_jobs, order_jobs, deliver_jobs, photo_jobs, client_payment_plan_jobs, \
    representative_jobs, colect_job
from src.jobs import system_jobs
from src.jobs import stock_jobs
from src.jobs import price_jobs
from src.jobs import sent_jobs
from src.api import oking
from src.jobs.config_jobs import enviar_criacao
from src.jobs.system_jobs import OnlineLogger
from src.jobs import client_jobs
from src.utils import get_config
from src.log_types import LogType
logger = logging.getLogger()
send_log = OnlineLogger.send_log
lock = threading.Lock


# region CLIENTES

def instantiate_send_cliente_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos clientes para a OKING HUB
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        client_jobs.job_send_clients(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_send_cliente_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos clientes para a OKING HUB
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_send_cliente_job, args=[job_config])
        # job_thread = threading.Thread(target=client_jobs.job_send_clients, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_colect_client_data_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos clientes para a OKING HUB
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        colect_job.job_send_clients_colect(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_colect_client_data_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos clientes para a OKING HUB
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_colect_client_data_job, args=[job_config])
        # job_thread = threading.Thread(target=colect_job.job_send_clients_colect, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_send_transportadora_to_okvendas_job(job_config: dict) -> None:
    """
    Instancia o job de envio das Transportadoras para a OKING HUB
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        client_jobs.job_send_transportadora_to_okvendas(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_job_send_transportadora(job_config: dict) -> None:
    """
    Instancia o job de envio das Transportadoras para a OKING HUB
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_send_transportadora_to_okvendas_job, args=[job_config])
        # job_thread = threading.Thread(target=client_jobs.job_send_transportadora_to_okvendas, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


# endregion CLIENTES

# region VENDAS
def instantiate_colect_venda_data_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos vendas para a OKING HUB
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        colect_job.job_send_sales_colect(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_colect_venda_data_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos clientes para a OKING HUB
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_colect_venda_data_job, args=[job_config])
        # job_thread = threading.Thread(target=colect_job.job_send_sales_colect, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


# endregion VENDAS

# region PRODUTOS
def instantiate_send_produto_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos produtos para a OKING HUB
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        product_jobs.job_send_products(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_send_produto_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos produtos para a OKING HUB
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_send_produto_job, args=[job_config])
        # job_thread = threading.Thread(target=product_jobs.job_send_products, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_send_related_product_job(job_config: dict) -> None:
    """
    Instancia o job de envio de produtos relacionados para o ERP
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        product_jobs.job_send_related_product(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_send_related_product_job(job_config: dict) -> None:
    """
    Instancia o job de envio de produtos relacionados para o ERP
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_send_related_product_job, args=[job_config])
        # job_thread = threading.Thread(target=product_jobs.job_send_related_product, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_send_crosselling_product_job(job_config: dict) -> None:
    """
    Instancia o job de envio de produtos crosselling para o ERP
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        product_jobs.job_send_crosselling_product(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_send_crosselling_product_job(job_config: dict) -> None:
    """
    Instancia o job de envio de produtos crosselling para o ERP
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_send_crosselling_product_job, args=[job_config])
        # job_thread = threading.Thread(target=product_jobs.job_send_crosselling_product, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_send_product_launch(job_config: dict) -> None:
    """
    Instancia o job de envio de produtos de lançamento para o ERP
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        product_jobs.job_send_product_launch(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_send_product_launch(job_config: dict) -> None:
    """
    Instancia o job de envio de produtos de lançamento para o ERP
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_send_product_launch, args=[job_config])
        # job_thread = threading.Thread(target=product_jobs.job_send_product_launch, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_send_showcase_product(job_config: dict) -> None:
    """
    Instancia o job de envio de vitrine de produtos para o ERP
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        product_jobs.job_send_showcase_product(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_send_showcase_product(job_config: dict) -> None:
    """
    Instancia o job de envio de vitrine de produtos para o ERP
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_send_showcase_product, args=[job_config])
        # job_thread = threading.Thread(target=product_jobs.job_send_showcase_product, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado
# endregion PRODUTOS


# region Estoques

def instantiate_send_stock_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos estoques para a api okVendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        stock_jobs.job_send_stocks(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_send_stock_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos estoques para a api okVendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_send_stock_job, args=[job_config])
        # job_thread = threading.Thread(target=stock_jobs.job_send_stocks, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_send_distribution_center_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos Centros de Distribuição para a api okVendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        stock_jobs.job_send_distribution_center(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_send_distribution_center_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos Centros de Distribuição para a api okVendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_send_distribution_center_job, args=[job_config])
        # job_thread = threading.Thread(target=stock_jobs.job_send_distribution_center, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_send_filial_job(job_config: dict) -> None:
    """
    Instancia o job de envio das Filiais para a api okVendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        stock_jobs.job_send_filial(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_send_filial_job(job_config: dict) -> None:
    """
    Instancia o job de envio das Filiais para a api okVendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_send_filial_job, args=[job_config])
        # job_thread = threading.Thread(target=stock_jobs.job_send_filial, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado

# endregion Estoques


# region Precos

def instantiate_send_price_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos preços para a api okVendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        price_jobs.job_send_prices(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_send_price_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos preços para a api okVendas

    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_send_price_job, args=[job_config])
        # job_thread = threading.Thread(target=price_jobs.job_send_prices, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_prices_list_job(job_config: dict) -> None:
    """
    Instancia o job de envio das listas de preço para o banco semáforo

    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        price_jobs.job_prices_list(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_prices_list_job(job_config: dict) -> None:
    """
    Instancia o job de envio das listas de preço para o banco semáforo

    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_prices_list_job, args=[job_config])
        # job_thread = threading.Thread(target=price_jobs.job_prices_list, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_product_prices_list_job(job_config: dict) -> None:
    """
    Instancia o job dos produtos das listas de preço
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        price_jobs.job_products_prices_list(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_product_prices_list_job(job_config: dict) -> None:
    """
    Instancia o job dos produtos das listas de preço
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_product_prices_list_job, args=[job_config])
        # job_thread = threading.Thread(target=price_jobs.job_products_prices_list, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


# endregion Precos

# region representante
def instantiate_representative_job(job_config: dict) -> None:
    """
    Instancia o job dos representantes
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        representative_jobs.job_representative(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_representative_job(job_config: dict) -> None:
    """
    Instancia o job dos representantes
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_representative_job, args=[job_config])
        # job_thread = threading.Thread(target=representative_jobs.job_representative, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


# endregion representante


# region PEDIDOS

def instantiate_orders_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos pedidos para o ERP, incluindo pedidos ainda não pagos
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        order_jobs.define_job_start(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_orders_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos pedidos para o ERP, incluindo pedidos ainda não pagos
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_orders_job, args=[job_config])
        # job_thread = threading.Thread(target=order_jobs.define_job_start, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_paid_orders_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos pedidos pagos para o ERP
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        order_jobs.define_job_start(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_paid_orders_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos pedidos pagos para o ERP
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_paid_orders_job, args=[job_config])
        # job_thread = threading.Thread(target=order_jobs.define_job_start, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_forward_to_delivery(job_config: dict) -> None:
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        sent_jobs.job_sent(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_forward_to_delivery(job_config: dict) -> None:
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_forward_to_delivery, args=[job_config])
        # job_thread = threading.Thread(target=sent_jobs.job_sent, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_deliver_job(job_config: dict) -> None:
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        deliver_jobs.job_delivered(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_deliver_job(job_config: dict) -> None:
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_deliver_job, args=[job_config])
        # job_thread = threading.Thread(target=deliver_jobs.job_delivered, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_b2b_orders_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos pedidos B2B para o ERP, incluindo pedidos ainda não pagos
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        order_jobs.define_job_start(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_b2b_orders_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos pedidos B2B para o ERP, incluindo pedidos ainda não pagos
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_b2b_orders_job, args=[job_config])
        # job_thread = threading.Thread(target=order_jobs.define_job_start, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_paid_b2b_orders_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos pedidos pagos B2B para o ERP
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        order_jobs.define_job_start(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_paid_b2b_orders_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos pedidos pagos B2B para o ERP
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_paid_b2b_orders_job, args=[job_config])
        # job_thread = threading.Thread(target=order_jobs.define_job_start, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_suggested_sale(job_config: dict) -> None:
    """
    Instancia o job de envio de venda sugerida para o ERP
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        order_jobs.job_send_suggested_sale(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_suggested_sale(job_config: dict) -> None:
    """
    Instancia o job de envio de venda sugerida para o ERP
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_suggested_sale, args=[job_config])
        # job_thread = threading.Thread(target=order_jobs.job_send_suggested_sale, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_duplicate_internalized_order(job_config: dict) -> None:
    """
    Instancia o job de duplicar pedido internalizado
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        order_jobs.job_duplicate_internalized_order(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_duplicate_internalized_order(job_config: dict) -> None:
    """
    Instancia o job de duplicar pedido internalizado
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_duplicate_internalized_order, args=[job_config])
        # job_thread = threading.Thread(target=order_jobs.job_duplicate_internalized_order, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_send_order_to_okvendas_job(job_config: dict) -> None:
    """
    Instancia o job de enviar pedido para okvendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        order_jobs.job_send_order_to_okvendas(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_send_order_to_okvendas_job(job_config: dict) -> None:
    """
    Instancia o job de enviar pedido para okvendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_send_order_to_okvendas_job, args=[job_config])
        # job_thread = threading.Thread(target=order_jobs.job_send_order_to_okvendas, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado

# endregion PEDIDOS


# region SystemJobs

def instantiate_periodic_execution_notification(job_config: dict) -> None:
    """
    Instancia o job que realiza a notificacao de execucao da integracao para a api okvendas
    Args:
        job_config: Configuração do job
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        system_jobs.send_execution_notification(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_periodic_execution_notification(job_config: dict) -> None:
    """
    Instancia o job que realiza a notificacao de execucao da integracao para a api okvendas
    Args:
        job_config: Configuração do job
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_periodic_execution_notification, args=[job_config])
        # job_thread = threading.Thread(target=system_jobs.send_execution_notification, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


# endregion SystemJobs


# region Nota Fiscal

def instantiate_envia_notafiscal_job(job_config: dict) -> None:
    """
    Instancia o job de envio das notas fiscais para a OKING HUB
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        order_jobs.job_envia_notafiscal(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_envia_notafiscal_job(job_config: dict) -> None:
    """
    Instancia o job de envio das notas fiscais para a OKING HUB
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_envia_notafiscal_job, args=[job_config])
        # job_thread = threading.Thread(target=order_jobs.job_envia_notafiscal, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_envia_notafiscal_semfila_job(job_config: dict) -> None:
    """
    Instancia o job de envio das notas fiscais sem fila para a OKING HUB
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        order_jobs.job_envia_notafiscal_semfila(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_envia_notafiscal_semfila_job(job_config: dict) -> None:
    """
    Instancia o job de envio das notas fiscais sem fila para a OKING HUB
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_envia_notafiscal_semfila_job, args=[job_config])
        # job_thread = threading.Thread(target=order_jobs.job_envia_notafiscal_semfila, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


# endregion Nota Fiscal


# region Tracking

def instantiate_delivered_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos produtos para a OKING HUB
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        deliver_jobs.job_delivered(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_delivered_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos produtos para a OKING HUB
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_delivered_job, args=[job_config])
        # job_thread = threading.Thread(target=deliver_jobs.job_delivered, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


# endregion Tracking


# region Foto

def instantiate_send_photo_job(job_config: dict) -> None:
    """
    Instancia o job de envio das fotos para a OKING HUB
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        photo_jobs.job_send_photo(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_send_photo_job(job_config: dict) -> None:
    """
    Instancia o job de envio das fotos para a OKING HUB
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_send_photo_job, args=[job_config])
        # job_thread = threading.Thread(target=photo_jobs.job_send_photo, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


# endregion Foto


# region Forma de Pagamento

def instantiate_client_payment_plan_job(job_config: dict) -> None:
    """
    Instancia o job dos planos de pagamentos dos clientes
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        client_payment_plan_jobs.job_client_payment_plan(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_client_payment_plan_job(job_config: dict) -> None:
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_client_payment_plan_job, args=[job_config])
        # job_thread = threading.Thread(target=client_payment_plan_jobs.job_client_payment_plan, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


# endregion Forma de Pagamento


# region Imposto

def instantiate_product_tax_job(job_config: dict) -> None:
    """
    Instancia o job dos impostos dos produtos
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        product_jobs.job_product_tax(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_product_tax_job(job_config: dict) -> None:
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_product_tax_job, args=[job_config])
        # job_thread = threading.Thread(target=product_jobs.job_product_tax, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_product_tax_full_job(job_config: dict) -> None:
    """
    Instancia o job dos impostos em lote dos produtos
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        product_jobs.job_product_tax_full(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_product_tax_full_job(job_config: dict) -> None:
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_product_tax_full_job, args=[job_config])
        # job_thread = threading.Thread(target=product_jobs.job_product_tax_full, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


# endregion Imposto

def intantiate_send_approved_clients_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos clientes B2B aprovados para o ERP
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        client_jobs.job_send_approved_clients(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_intantiate_send_approved_clients_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos clientes B2B aprovados para o ERP
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=intantiate_send_approved_clients_job, args=[job_config])
        # job_thread = threading.Thread(target=client_jobs.job_send_approved_clients, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_send_colect_physical_shopping(job_config: dict) -> None:
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        colect_job.job_send_colect_physical_shopping(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_instantiate_send_colect_physical_shopping(job_config: dict) -> None:
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_send_colect_physical_shopping, args=[job_config])
        # job_thread = threading.Thread(target=colect_job.job_send_colect_physical_shopping, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def instantiate_send_points_to_okvendas_job(job_config: dict) -> None:
    try:
        logger.info(job_config.get('job_name') + ' | Iniciando execucao')
        client_jobs.job_send_points_to_okvendas(job_config)
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_send_points_to_okvendas(job_config: dict) -> None:
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=instantiate_send_points_to_okvendas_job, args=[job_config])
        # job_thread = threading.Thread(target=client_jobs.job_send_points_to_okvendas, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


def run_thread_verify_jobs_change(job_config: dict) -> None:
    """
    Args:
        job_config:

    Returns:
    """
    try:
        logger.info(f'Adicionando job {job_config.get("job_name")} na thread')
        # AGORA O TARGET É A FUNÇÃO QUE JÁ TEM O TRATAMENTO DE ERRO!
        job_thread = threading.Thread(target=verify_jobs_change, args=[job_config])
        job_thread.start()
    except Exception as e:
        logger.critical(f'Falha crítica no job: {str(e)}', exc_info=True)
        # Garantir que o job será reagendado


# region ConfigJobs

def schedule_job(job_config: dict, time_unit: str, time: int) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} ao schedule de {time} em {time} {time_unit}')
    func = get_thread_job_from_name(job_config.get('job_name'))
    if func is not None:
        if time_unit == 'M':  # Minutos
            schedule.every(time).minutes.do(func, job_config)
        elif time_unit == 'H':  # Horas
            schedule.every(time).hours.do(func, job_config)
        elif time_unit == 'D':  # Dias
            schedule.every(time).days.do(func, job_config)


def get_job_from_name(job_name: str):
    # Estoque
    if job_name == 'envia_estoque_job':
        return instantiate_send_stock_job

    # PRODUTO
    elif job_name == 'envia_produto_job':
        return instantiate_send_produto_job

    elif job_name == 'envia_produto_relacionado_job':
        return instantiate_send_related_product_job

    elif job_name == 'envia_produto_crosselling_job':
        return instantiate_send_crosselling_product_job

    elif job_name == 'envia_produto_lancamento_job':
        return instantiate_send_product_launch

    elif job_name == 'envia_produto_vitrine_job':
        return instantiate_send_showcase_product

    # Preco
    elif job_name == 'envia_preco_job':
        return instantiate_send_price_job

    elif job_name == 'lista_preco_job':
        return instantiate_prices_list_job

    elif job_name == 'produto_lista_preco_job':
        return instantiate_product_prices_list_job

    # Pedido
    elif job_name == 'internaliza_pedidos_job':
        return instantiate_orders_job

    elif job_name == 'encaminhar_entrega_job':
        return instantiate_forward_to_delivery

    elif job_name == 'internaliza_pedidos_pagos_job':
        return instantiate_paid_orders_job

    elif job_name == 'internaliza_pedidos_b2b_job':
        return instantiate_b2b_orders_job

    elif job_name == 'internaliza_pedidos_pagos_b2b_job':
        return instantiate_paid_b2b_orders_job

    elif job_name == 'envia_venda_sugerida_job':
        return instantiate_suggested_sale

    elif job_name == 'envia_pedido_to_okvendas_job':
        return instantiate_send_order_to_okvendas_job

    # CLIENTE
    elif job_name == 'envia_cliente_job':
        return instantiate_send_cliente_job

    elif job_name == 'coleta_dados_cliente_job':
        return instantiate_colect_client_data_job

    elif job_name == 'coleta_dados_venda_job':
        return instantiate_colect_venda_data_job

    elif job_name == 'envia_tranportadora_fob_job':
        return instantiate_send_transportadora_to_okvendas_job

    # ENTREGA

    # Notificacao
    elif job_name == 'periodic_execution_notification':
        return instantiate_periodic_execution_notification

    # Nota Fiscal
    elif job_name == 'envia_notafiscal_job':
        return instantiate_envia_notafiscal_job

    elif job_name == 'envia_notafiscal_semfila_job':
        return instantiate_envia_notafiscal_semfila_job

    # entregue_job
    elif job_name == 'entregue_job':
        return instantiate_delivered_job

    # Foto
    elif job_name == 'envia_foto_job':
        return instantiate_send_photo_job

    elif job_name == 'envia_plano_pagamento_cliente_job':
        return instantiate_client_payment_plan_job
    # Imposto
    elif job_name == 'envia_imposto_job':
        return instantiate_product_tax_job

    elif job_name == 'envia_imposto_lote_job':
        return instantiate_product_tax_full_job

    # Representante
    elif job_name == 'envia_representante_job':
        return instantiate_representative_job

    elif job_name == 'integra_cliente_aprovado_job':
        return intantiate_send_approved_clients_job

    elif job_name == 'duplicar_pedido_internalizado_job':
        return instantiate_duplicate_internalized_order

    elif job_name == 'coleta_compras_loja_fisica_job':
        return instantiate_send_colect_physical_shopping

    elif job_name == 'envia_pontos_to_okvendas_job':
        return instantiate_send_points_to_okvendas_job

    elif job_name == 'envia_centro_distribuicao_job':
        return instantiate_send_distribution_center_job

    elif job_name == 'envia_filial_job':
        return instantiate_send_filial_job


def get_thread_job_from_name(job_name: str):
    # Estoque
    if job_name == 'envia_estoque_job':
        return run_thread_instantiate_send_stock_job

    # PRODUTO
    elif job_name == 'envia_produto_job':
        return run_thread_instantiate_send_produto_job

    elif job_name == 'envia_produto_relacionado_job':
        return run_thread_instantiate_send_related_product_job

    elif job_name == 'envia_produto_crosselling_job':
        return run_thread_instantiate_send_crosselling_product_job

    elif job_name == 'envia_produto_lancamento_job':
        return run_thread_instantiate_send_product_launch

    elif job_name == 'envia_produto_vitrine_job':
        return run_thread_instantiate_send_showcase_product

    # Preco
    elif job_name == 'envia_preco_job':
        return run_thread_instantiate_send_price_job

    elif job_name == 'lista_preco_job':
        return run_thread_instantiate_prices_list_job

    elif job_name == 'produto_lista_preco_job':
        return run_thread_instantiate_product_prices_list_job

    # Pedido
    elif job_name == 'internaliza_pedidos_job':
        return run_thread_instantiate_orders_job

    elif job_name == 'encaminhar_entrega_job':
        return run_thread_instantiate_forward_to_delivery

    elif job_name == 'internaliza_pedidos_pagos_job':
        return run_thread_instantiate_paid_orders_job

    elif job_name == 'internaliza_pedidos_b2b_job':
        return run_thread_instantiate_b2b_orders_job

    elif job_name == 'internaliza_pedidos_pagos_b2b_job':
        return run_thread_instantiate_paid_b2b_orders_job

    elif job_name == 'envia_venda_sugerida_job':
        return run_thread_instantiate_suggested_sale

    elif job_name == 'envia_pedido_to_okvendas_job':
        return run_thread_instantiate_send_order_to_okvendas_job

    # CLIENTE
    elif job_name == 'envia_cliente_job':
        return run_thread_instantiate_send_cliente_job

    elif job_name == 'coleta_dados_cliente_job':
        return run_thread_instantiate_colect_client_data_job

    elif job_name == 'coleta_dados_venda_job':
        return run_thread_instantiate_colect_venda_data_job

    elif job_name == 'envia_tranportadora_fob_job':
        return run_thread_job_send_transportadora

    # ENTREGA

    # Notificacao
    elif job_name == 'periodic_execution_notification':
        return run_thread_instantiate_periodic_execution_notification

    # Nota Fiscal
    elif job_name == 'envia_notafiscal_job':
        return run_thread_instantiate_envia_notafiscal_job

    elif job_name == 'envia_notafiscal_semfila_job':
        return run_thread_instantiate_envia_notafiscal_semfila_job

    # entregue_job
    elif job_name == 'entregue_job':
        return run_thread_instantiate_delivered_job

    # Foto
    elif job_name == 'envia_foto_job':
        return run_thread_instantiate_send_photo_job

    elif job_name == 'envia_plano_pagamento_cliente_job':
        return run_thread_instantiate_client_payment_plan_job

    # Imposto
    elif job_name == 'envia_imposto_job':
        return run_thread_instantiate_product_tax_job

    elif job_name == 'envia_imposto_lote_job':
        return run_thread_instantiate_product_tax_full_job

    elif job_name == 'envia_representante_job':
        return run_thread_instantiate_representative_job

    elif job_name == 'integra_cliente_aprovado_job':
        return run_thread_intantiate_send_approved_clients_job

    elif job_name == 'verify_jobs_change':
        return run_thread_verify_jobs_change

    elif job_name == 'duplicar_pedido_internalizado_job':
        return run_thread_instantiate_duplicate_internalized_order

    elif job_name == 'coleta_compras_loja_fisica_job':
        return run_thread_instantiate_send_colect_physical_shopping

    elif job_name == 'envia_pontos_to_okvendas_job':
        return run_thread_send_points_to_okvendas

    elif job_name == 'envia_centro_distribuicao_job':
        return run_thread_send_distribution_center_job

    elif job_name == 'envia_filial_job':
        return run_thread_send_filial_job

# endregion ConfigJobs


token = ''


def activate_modules():
    src.jobs_qtd = 0
    modules: list = [oking.Module(**m) for m in src.client_data.get('modulos')]
    assert modules is not None,\
        'Nao foi possivel obter os modulos da integracao. Por favor, entre em contato com o suporte.'

    for module in modules:
        if module.time is None:
            module.time = 9999
        if module.ativo == 'S':
            src.jobs_qtd += 1
            schedule_job({
                'db_host': src.client_data.get('host'),
                'db_port': src.client_data.get('port'),
                'db_user': src.client_data.get('user'),
                'db_type': src.client_data.get('db_type'),
                'db_seller': src.client_data.get('loja_id'),
                'db_name': src.client_data.get('database'),
                'db_pwd': src.client_data.get('password'),
                'db_client': src.client_data.get('diretorio_client'),
                'operacao': src.client_data.get('operacao'),
                'send_logs': module.send_logs,
                'enviar_logs': module.send_logs,
                'enviar_logs_debug': module.enviar_logs_debug,
                'job_name': module.job_name,
                'executar_query_semaforo': module.executar_query_semaforo,
                'ativo': module.ativo,
                'sql': module.sql,
                'semaforo_sql': module.exists_sql,
                'query_final': module.query_final,
                'ultima_execucao': module.ultima_execucao,
                'old_version': module.old_version
            }, module.time_unit, module.time)

    # Job para notificar execucao periodica do Oking a cada 30 min
    schedule_job({
        'job_name': 'periodic_execution_notification',
        'execution_start_time': src.start_time,
        'job_qty': len(schedule.get_jobs()),
        'integration_id': src.client_data.get('integracao_id')
    }, 'M', 30)
    src.jobs_qtd += 1
    # Job para atualizar jobs durante a execução
    schedule_job({
        'job_name': 'verify_jobs_change',
        'execution_start_time': src.start_time,
        'job_qty': len(schedule.get_jobs()),
        'integration_id': src.client_data.get('integracao_id')
    }, 'M', 10)
    src.jobs_qtd += 1


def verify_jobs_change(job_config_dict: dict):
    qtd_schedule_jobs = len(schedule.get_jobs())
    logger.info('=== VERIFICANDO ATUALIZAÇÃO DE JOBS ===')
    logger.info(f"Quantidade de jobs do módulo: {src.jobs_qtd}")
    logger.info(f"Quantidade de Schedules ativos: {qtd_schedule_jobs}")
    if src.jobs_qtd != qtd_schedule_jobs:
        mensagem = f"Quantidade de Jobs do módulo {src.jobs_qtd}, quantidade de jobs no Schedule{qtd_schedule_jobs} " \
                   f"- Versão {src.version}"
        send_log(
            'EXECUCAO',
            src.client_data.get('enviar_logs'),
            True,
            mensagem,
            LogType.EXEC,
            src.client_data.get("seller_id")
        )
        schedule.clear()
        src.client_data = oking.get(f'https://{src.shortname_interface}.oking.openk.com.br/api/consulta/oking_hub/'
                                    f'filtros?token={src.token_interface}', None)

        activate_modules()
    else:
        logger.info('=== SEM JOBS PARA ATUALIZAR ===')


def main():
    logger.info('Iniciando oking __main__')
    logger.info('===========================================================================')
    logger.info('==== Iniciando OKING HUB __main__')
    logger.info(f'==== Exibir Interface grafica: {src.exibir_interface_grafica}')
    logger.info('===========================================================================')

    if src.exibir_interface_grafica:
        interface_grafica.exibir_interface()

    elif src.job_console:
        try:
            logger.info(f'Executando job {src.job_console}')
            execucao_job_unico = get_job_from_name(src.job_console)
            execucao_job_unico(get_config(src.job_console))
        except Exception as e:
            logger.error(f'Erro não tratado capturado: {str(e)}')

    elif src.createDatabase:
        try:
            enviar_criacao(src.client_data)
        except Exception as e:
            logger.error(f'Erro não tratado capturado: {str(e)}')

    else:
        activate_modules()

        if src.print_payloads:
            print("========================================")
            for x in schedule.get_jobs():
                print(x.job_func.__name__)
            logger.info(src.jobs_qtd)
            logger.info(len(schedule.get_jobs()))
            print("=== VALIDANDO OS JOBS ")
            print("========================================")

        while True:
            try:
                schedule.run_pending()
                sleep(5)
            except Exception as e:
                logger.error(f'Erro não tratado capturado: {str(e)}')
                send_log(
                    '__main__',
                    src.client_data.get('enviar_logs'),
                    True,
                    f'{str(e)}',
                    LogType.ERROR,
                    'MAIN'
                )


if __name__ == "__main__":
    main()
