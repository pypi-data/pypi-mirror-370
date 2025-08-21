import os
import base64
import src
from src.api import oking
from src.api.entities.foto_sku import Foto_Produto_Sku
from src.jobs import stock_jobs, price_jobs, client_jobs, colect_job, product_jobs, photo_jobs, order_jobs, \
    representative_jobs, client_payment_plan_jobs, sent_jobs, deliver_jobs
import src.api.okvendas as api_okVendas
import datetime
import shutil


def get_config(job_name):
    modules: list = [oking.Module(**m) for m in src.client_data.get('modulos')]
    findjob = ''
    for module in modules:
        if module.job_name == job_name:
            findjob = module
            break
    return {
        'db_host': src.client_data.get('host'),
        'db_port': src.client_data.get('port'),
        'db_user': src.client_data.get('user'),
        'db_type': src.client_data.get('db_type'),
        'db_seller': src.client_data.get('loja_id'),
        'db_name': src.client_data.get('database'),
        'db_pwd': src.client_data.get('password'),
        'db_client': src.client_data.get('diretorio_client'),
        'send_logs': findjob.send_logs,
        'enviar_logs': findjob.send_logs,
        'job_name': findjob.job_name,
        'ativo': findjob.ativo,
        'executar_query_semaforo': findjob.executar_query_semaforo,
        'sql': findjob.sql,
        'semaforo_sql': findjob.exists_sql,
        'query_final': findjob.query_final,
        'ultima_execucao': findjob.ultima_execucao,
        'old_version': findjob.old_version
    }


dict_all_jobs = {
    'envia_estoque_job': {
        'job_type': 'ESTOQUE',
        'job_function': stock_jobs.job_send_stocks,
        'job_category': 'catalogo',
        'job_description': 'Envia Estoque'},
    'envia_preco_job': {
        'job_type': 'PRECO',
        'job_function': price_jobs.job_send_prices,
        'job_category': 'catalogo',
        'job_description': 'Envia Preço'},
    'envia_produto_job': {
        'job_type': 'PRODUTO',
        'job_function': product_jobs.job_send_products,
        'job_category': 'catalogo',
        'job_description': 'Envia Produto'},
    'envia_cliente_job': {
        'job_type': 'CLIENTE',
        'job_function': client_jobs.job_send_clients,
        'job_category': 'auxiliar',
        'job_description': 'Envia Cliente'},
    'coleta_dados_cliente_job': {
        'job_type': 'COLETACLIENTE',
        'job_function': colect_job.job_send_clients_colect,
        'job_category': 'auxiliar',
        'job_description': 'Coleta Dados Cliente'},
    'coleta_dados_venda_job': {
        'job_type': 'COLETAVENDA',
        'job_function': colect_job.job_send_sales_colect,
        'job_category': 'auxiliar',
        'job_description': 'Coleta Dados Venda'},
    'internaliza_pedidos_job': {
        'job_type': 'PEDIDO',
        'job_function': order_jobs.define_job_start,
        'job_category': 'pedido',
        'job_description': 'Internaliza Pedidos'},
    'internaliza_pedidos_pagos_job': {
        'job_type': 'PEDIDOPAGO',
        'job_function': order_jobs.define_job_start,
        'job_category': 'pedido',
        'job_description': 'Internaliza Pedidos Pagos'},
    'envia_venda_sugerida_job': {
        'job_type': 'VENDASUGERIDA',
        'job_function': order_jobs.job_send_suggested_sale,
        'job_category': 'pedido',
        'job_description': 'Venda Sugerida'},
    'encaminhar_entrega_job': {
        'job_type': 'ENCAMINHA',
        'job_function': sent_jobs.job_sent,
        'job_category': 'pedido',
        'job_description': 'Encaminha Entrega'},
    'entregue_job': {
        'job_type': 'ENTREGUE',
        'job_function': deliver_jobs.job_delivered,
        'job_category': 'auxiliar',
        'job_description': 'Entregue'},
    'baixa_pagamento_job': {
        'job_type': 'PAGAMENTO',
        'job_function': None,
        'job_category': 'auxiliar',
        'job_description': 'Baixa Pagamento'},
    'envia_plano_pagamento_cliente_job': {
        'job_type': 'CLIENTEPLANOPGT',
        'job_function': client_payment_plan_jobs.job_client_payment_plan,
        'job_category': 'auxiliar',
        'job_description': 'Plano Pagamento Cliente'},
    'baixa_cancelamento_job': {
        'job_type': 'CANCELAMENTO',
        'job_function': None,
        'job_category': 'auxiliar',
        'job_description': 'Baixa Cancelamento'},
    'envia_notafiscal_job': {
        'job_type': 'NOTAFISCAL',
        'job_function': order_jobs.job_envia_notafiscal,
        'job_category': 'pedido',
        'job_description': 'Envia Nota Fiscal'},
    'envia_foto_job': {
        'job_type': 'FOTO',
        'job_function': photo_jobs.job_send_photo,
        'job_category': 'catalogo',
        'job_description': 'Envia Foto'},
    'envia_imposto_job': {
        'job_type': 'IMPOSTOPRODUTO',
        'job_function': product_jobs.job_product_tax,
        'job_category': 'auxiliar',
        'job_description': 'Envia Imposto'},
    'envia_imposto_lote_job': {
        'job_type': 'IMPOSTOLOTE',
        'job_function': product_jobs.job_product_tax_full,
        'job_category': 'auxiliar',
        'job_description': 'Envia Imposto Lote'},
    'lista_preco_job': {
        'job_type': 'LISTAPRECO',
        'job_function': price_jobs.job_prices_list,
        'job_category': 'auxiliar',
        'job_description': 'Lista Preço'},
    'produto_lista_preco_job': {
        'job_type': 'PRODUTOLISTAPRECO',
        'job_function': price_jobs.job_products_prices_list,
        'job_category': 'auxiliar',
        'job_description': 'Produto Lista Preço'},
    'integra_cliente_aprovado_job': {
        'job_type': 'CLIENTEAPROVADO',
        'job_function': client_jobs.job_send_approved_clients,
        'job_category': 'auxiliar',
        'job_description': 'Integra Cliente Aprovado'},
    'envia_representante_job': {
        'job_type': 'REPRESENTANTE',
        'job_function': representative_jobs.job_representative,
        'job_category': 'auxiliar',
        'job_description': 'Envia Representante'},
    'envia_notafiscal_semfila_job': {
        'job_type': 'NOTAFISCALSEMFILA',
        'job_function': order_jobs.job_envia_notafiscal_semfila,
        'job_category': 'pedido',
        'job_description': 'Envia Nota Fiscal sem fila'},
    'envia_produto_relacionado_job': {
        'job_type': 'PRODUTORELACIONADO',
        'job_function': product_jobs.job_send_related_product,
        'job_category': 'auxiliar',
        'job_description': 'Envia Produto Relacionado'},
    'envia_produto_crosselling_job': {
        'job_type': 'PRODUTOCROSSELLING',
        'job_function': product_jobs.job_send_crosselling_product,
        'job_category': 'auxiliar',
        'job_description': 'Envia Produto Crosselling'},
    'envia_produto_lancamento_job': {
        'job_type': 'PRODUTOLANCAMENTO',
        'job_function': product_jobs.job_send_product_launch,
        'job_category': 'auxiliar',
        'job_description': 'Envia Produto Lançamento'},
    'envia_produto_vitrine_job': {
        'job_type': 'PRODUTOVITRINE',
        'job_function': product_jobs.job_send_showcase_product,
        'job_category': 'auxiliar',
        'job_description': 'Envia Produto Vitrine'
    },
    'cancela_pedido_job': {
        'job_type': 'CANCELAPEDIDO',
        'job_function': None,
        'job_category': 'pedido',
        'job_description': 'Cancela Pedido'
    },
    'duplicar_pedido_internalizado_job': {
        'job_type': 'DUPLICARPEDIDO',
        'job_function': order_jobs.job_duplicate_internalized_order,
        'job_category': 'pedido',
        'job_description': 'Duplica Pedido Internalizado'
    },
    'forma_pagamento_job': {
        'job_type': 'FORMAPAGAMENTO',
        'job_function': None,
        'job_category': 'auxiliar',
        'job_description': 'Forma de Pagamento'
    },
    'coleta_compras_loja_fisica_job': {
        'job_type': 'COLETACOMPRAFISICA',
        'job_function': colect_job.job_send_colect_physical_shopping,
        'job_category': 'auxiliar',
        'job_description': 'Coleta Compra Loja Física'
    },
    'envia_pedido_to_okvendas_job': {
        'job_type': 'ENVIAPEDIDOOKVENDAS',
        'job_function': order_jobs.job_send_order_to_okvendas,
        'job_category': 'pedido',
        'job_description': 'Envia Pedido para Okvendas'
    },
    'envia_pontos_to_okvendas_job': {
        'job_type': 'PONTOSOKVENDAS',
        'job_function': client_jobs.job_send_points_to_okvendas,
        'job_category': 'auxiliar',
        'job_description': 'Envia Pontos para Okvendas'
    },
    'envia_centro_distribuicao_job': {
        'job_type': 'CENTRODISTRIBUICAO',
        'job_function': stock_jobs.job_send_distribution_center,
        'job_category': 'catalogo',
        'job_description': 'Envia Centro de Distribuição para Okvendas'
    },
    'envia_filial_job': {
        'job_type': 'FILIAL',
        'job_function': stock_jobs.job_send_filial,
        'job_category': 'catalogo',
        'job_description': 'Envia Filial para Okvendas'
    },
    'envia_tranportadora_fob_job': {
        'job_type': 'TRANSPORTADORA',
        'job_function': client_jobs.job_send_transportadora_to_okvendas,
        'job_category': 'auxiliar',
        'job_description': 'Envia Transportadora Parceiro para Okvendas'
    }
}


def send_photo(dir):
    try:
        processadas = 0
        fotos = os.listdir(dir)
        nome_pasta = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))\
            .replace('-', '').replace(' ', '').replace(':', '')
        os.makedirs(f'Processadas/{nome_pasta}')
        for f in fotos:
            with open(f"{dir}/{f}", "rb") as p:
                base64_foto = base64.b64encode(p.read()).decode()
            if '_' not in f:
                codigo_erp_sku = f[:f.index('.')]
                foto_padrao = True
            else:
                codigo_erp_sku = f[:f.index('_')]
                foto_padrao = True if f[f.index('_') + 1:f.index('.')] == '1' else False
            ordem = 1
            codigo_foto = f[:f.index('.')]
            photo_obj = Foto_Produto_Sku(base64_foto, codigo_erp_sku, codigo_foto, ordem, foto_padrao)
            response = api_okVendas.put_photos_sku([photo_obj])
            if response:
                processadas += 1
                antes = f"{dir}/{f}"
                depois = f'Processadas/{nome_pasta}/{f}'
                shutil.move(antes, depois)
        return processadas, nome_pasta
    except Exception as e:
        raise e
