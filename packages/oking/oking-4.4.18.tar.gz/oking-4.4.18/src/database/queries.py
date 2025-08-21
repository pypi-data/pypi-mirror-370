from enum import IntEnum
# import fdb
# import firebirdsql

import src
from src.imports import import_package


class IntegrationType(IntEnum):
    PRODUTO = 1
    ESTOQUE = 2
    PRECO = 3
    FOTO = 4
    CLIENTE = 5
    PEDIDO = 6
    NOTA_FISCAL = 7
    CONDICAO_PAGAMENTO = 8
    REPRESENTANTE = 9
    IMPOSTO = 10
    LISTA_PRECO = 11
    LISTA_PRECO_PRODUTO = 12
    PLANO_PAGAMENTO_CLIENTE = 13
    COLETA_DADOS_CLIENTE = 14
    COLETA_DADOS_VENDA = 15
    PRODUTO_RELACIONADO = 16
    VENDA_SUGERIDA = 17
    PRODUTO_CROSSELLING = 18
    PRODUTO_LANCAMENTO = 19
    PRODUTO_VITRINE = 20
    COLETA_DADOS_COMPRA = 21
    PEDIDO_PARA_OKVENDAS = 22
    PONTO_FIDELIDADE = 23
    UNIDADE_DISTRIBUICAO = 24
    FILIAL = 25
    TRANSPORTADORA = 26


# Queries nao podem terminar com ponto e virgula
def get_command_parameter(connection_type: str, parameters: list):
    if connection_type.lower() == 'mysql':
        return tuple(parameters)
    elif connection_type.lower() == 'oracle':
        return parameters
    elif connection_type.lower() == 'sql':
        return parameters
    elif connection_type.lower() == 'firebird':
        return tuple(parameters)


def get_insert_update_semaphore_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return ''' insert into openk_semaforo.semaforo 
              (identificador, identificador2, tipo_id, data_alteracao, data_sincronizacao, mensagem) 
              values (%s, %s, %s, now(), null, %s) 
              on duplicate key 
              update data_alteracao = now(), mensagem = values(mensagem) '''
    elif connection_type.lower() == 'oracle':
        return '''
            MERGE INTO OPENK_SEMAFORO.SEMAFORO sem
            USING (
                SELECT
                    :1 AS IDENTIFICADOR,
                    cast(:2 AS varchar2(100)) AS IDENTIFICADOR2,
                    :3 AS tipo_id,
                    :4 AS mensagem
                FROM DUAL
            ) tmp ON (    tmp.identificador = sem.identificador 
                      AND tmp.identificador2 = sem.identificador2 
                      AND tmp.tipo_id = sem.tipo_id)
            
            WHEN MATCHED THEN
                UPDATE SET sem.DATA_ALTERACAO = SYSDATE , sem.MENSAGEM = tmp.mensagem
            
            WHEN NOT MATCHED THEN  
            INSERT (IDENTIFICADOR, IDENTIFICADOR2, TIPO_ID, DATA_ALTERACAO, DATA_SINCRONIZACAO, MENSAGEM)
            VALUES (tmp.identificador, tmp.identificador2, tmp.tipo_id, sysdate, null, tmp.mensagem)
            '''
    elif connection_type.lower() == 'sql':
        return '''
            MERGE INTO OPENK_SEMAFORO.SEMAFORO sem
            USING (
                SELECT
                    CAST(? AS NVARCHAR(MAX)) AS identificador,
                    ? AS identificador2,
                    ? AS tipo_id,
                    ? AS mensagem
            ) tmp ON (tmp.identificador = sem.identificador 
                  AND tmp.identificador2 = sem.identificador2 
                  AND tmp.tipo_id = sem.tipo_id)
            
            WHEN MATCHED THEN
                UPDATE SET sem.DATA_ALTERACAO = getdate(), sem.MENSAGEM = tmp.mensagem
            
            WHEN NOT MATCHED THEN
            INSERT (IDENTIFICADOR, IDENTIFICADOR2, TIPO_ID, DATA_ALTERACAO, DATA_SINCRONIZACAO, MENSAGEM)
            VALUES (tmp.identificador, tmp.identificador2, tmp.tipo_id, getdate(), null, tmp.mensagem);
            '''
    elif connection_type.lower() == 'firebird':
        return '''
                MERGE INTO SEMAFORO sem
                USING (
                    SELECT
                        CAST(? AS VARCHAR(100)) AS identificador,
                        CAST(? AS VARCHAR(100)) AS identificador2,
                        CAST(? AS INT) AS tipo_id,
                        CAST(? AS VARCHAR(150)) AS mensagem
                        from RDB$DATABASE
                ) tmp ON (tmp.identificador = sem.identificador AND
                         tmp.identificador2 = sem.identificador2 AND
                         tmp.tipo_id = sem.tipo_id)
    
                WHEN MATCHED THEN
                    UPDATE SET sem.DATA_ALTERACAO = CURRENT_TIMESTAMP, sem.MENSAGEM = tmp.mensagem
    
                WHEN NOT MATCHED THEN
                INSERT (IDENTIFICADOR, IDENTIFICADOR2, TIPO_ID, DATA_ALTERACAO, DATA_SINCRONIZACAO, MENSAGEM)
                VALUES (tmp.identificador, tmp.identificador2, tmp.tipo_id, CURRENT_TIMESTAMP, null, tmp.mensagem)
                '''


def get_protocol_semaphore_id_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'update openk_semaforo.semaforo set data_sincronizacao = now(), mensagem = %s where identificador = %s'
    elif connection_type.lower() == 'oracle':
        return 'update openk_semaforo.semaforo set data_sincronizacao = sysdate, mensagem = :1 where identificador = :2'
    elif connection_type.lower() == 'sql':
        return 'update openk_semaforo.semaforo set data_sincronizacao = getdate(), mensagem = ? where identificador = ?'
    elif connection_type.lower() == 'firebird':
        return 'update semaforo set data_sincronizacao = CURRENT_TIMESTAMP, mensagem = ? where identificador = ?'


def get_protocol_semaphore_id2_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''update openk_semaforo.semaforo 
                   set data_sincronizacao = now(), 
                       mensagem = %s 
                 where identificador = %s 
                   and identificador2 = %s'''
    elif connection_type.lower() == 'oracle':
        return '''update openk_semaforo.semaforo 
                     set data_sincronizacao = sysdate, 
                         mensagem = :1 
                   where identificador = :2 
                     and identificador2 = :3'''
    elif connection_type.lower() == 'sql':
        return '''update openk_semaforo.semaforo 
                     set data_sincronizacao = getdate(), 
                         mensagem = ? 
                   where identificador = ? 
                     and identificador2 = ?'''
    elif connection_type.lower() == 'firebird':
        return '''update semaforo 
                     set data_sincronizacao = CURRENT_TIMESTAMP, 
                         mensagem = ? 
                   where identificador = ? 
                     and identificador2 = ?'''


def get_semaphore_command_data_sincronizacao(connection_type: str):
    if connection_type.lower() == 'mysql':
        return ''' insert into openk_semaforo.semaforo 
              (identificador, identificador2, tipo_id, data_alteracao, data_sincronizacao, mensagem) 
              values (%s, %s, %s, now(), now(), %s) 
              on duplicate key 
              update data_sincronizacao = now(), mensagem = values(mensagem) '''
    elif connection_type.lower() == 'oracle':
        return '''
            MERGE INTO OPENK_SEMAFORO.SEMAFORO sem
            USING (
                SELECT
                    :1 AS IDENTIFICADOR,
                    cast(:2 AS varchar2(100)) AS IDENTIFICADOR2,
                    :3 AS tipo_id,
                    :4 AS mensagem
                FROM DUAL
            ) tmp ON (tmp.identificador = sem.identificador 
                  AND tmp.identificador2 = sem.identificador2 
                  AND tmp.tipo_id = sem.tipo_id)
    
            WHEN MATCHED THEN
                UPDATE SET sem.DATA_SINCRONIZACAO = SYSDATE , sem.MENSAGEM = tmp.mensagem
    
            WHEN NOT MATCHED THEN  
            INSERT (IDENTIFICADOR, IDENTIFICADOR2, TIPO_ID, DATA_ALTERACAO, DATA_SINCRONIZACAO, MENSAGEM)
            VALUES (tmp.identificador, tmp.identificador2, tmp.tipo_id, sysdate, sysdate, tmp.mensagem)
            '''
    elif connection_type.lower() == 'sql':
        return '''
            MERGE INTO OPENK_SEMAFORO.SEMAFORO sem
            USING (
                SELECT
                    ? AS identificador,
                    ? AS identificador2,
                    ? AS tipo_id,
                    ? AS mensagem
            ) tmp ON (tmp.identificador = sem.identificador 
                  AND tmp.identificador2 = sem.identificador2 
                  AND tmp.tipo_id = sem.tipo_id)
    
            WHEN MATCHED THEN
                UPDATE SET sem.DATA_SINCRONIZACAO = getdate(), sem.MENSAGEM = tmp.mensagem
    
            WHEN NOT MATCHED THEN
            INSERT (IDENTIFICADOR, IDENTIFICADOR2, TIPO_ID, DATA_ALTERACAO, DATA_SINCRONIZACAO, MENSAGEM)
            VALUES (tmp.identificador, tmp.identificador2, tmp.tipo_id, getdate(), getdate(), tmp.mensagem);
            '''
    elif connection_type.lower() == 'firebird':
        return '''
                MERGE INTO SEMAFORO sem
                USING (
                    SELECT
                        CAST(? AS VARCHAR(100)) AS identificador,
                        CAST(? AS VARCHAR(100)) AS identificador2,
                        CAST(? AS INT) AS tipo_id,
                        CAST(? AS VARCHAR(150)) AS mensagem
                        from RDB$DATABASE
                ) tmp ON (tmp.identificador = sem.identificador AND
                         tmp.identificador2 = sem.identificador2 AND
                         tmp.tipo_id = sem.tipo_id)
    
                WHEN MATCHED THEN
                    UPDATE SET sem.DATA_SINCRONIZACAO = CURRENT_TIMESTAMP, sem.MENSAGEM = tmp.mensagem
    
                WHEN NOT MATCHED THEN
                INSERT (IDENTIFICADOR, IDENTIFICADOR2, TIPO_ID, DATA_ALTERACAO, DATA_SINCRONIZACAO, MENSAGEM)
                VALUES (tmp.identificador, tmp.identificador2, tmp.tipo_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 
                        tmp.mensagem)
                '''


def create_database(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''create database openk_semaforo;

create table openk_semaforo.cliente
(
    id bigint(20) not null auto_increment primary key,
    nome varchar(255) default null,
    razao_social varchar(255) default null,
    tipo_pessoa varchar(1) default null,
    cpf_cnpj varchar(14) default null,
    email varchar(255) default null,
    rg varchar(15) default null,
    data_nascimento_constituicao datetime default null,
    sexo varchar(1) default null,
    orgao varchar(5) default null,
    
    telefone_residencial varchar(20) default null,
    telefone_celular varchar(20) default null,
    inscricao_estadual varchar(25) default null,
    inscricao_municipal varchar(25) default null,
    codigo_representante varchar(15) default null,
    codigo_referencia_erp varchar(20) default null comment 'Codigo do cliente no ERP',    
    end_principal_cep varchar(8) default null,
    end_principal_tipologradouro varchar(20) default null,
    end_principal_logradouro varchar(255) default null,
    end_principal_numero varchar(20) default null,
    end_principal_complemento varchar(255) default null,
    end_principal_bairro varchar(255) default null,
    end_principal_cidade varchar(255) default null,
    end_principal_estado varchar(2) default null,
    END_PRINCIPAL_REFERENCIA_ENT varchar(255) default null,
    end_principal_codigo_ibge varchar(15) default null,    
    direcao varchar(3) default 'OUT',
    data_sincronizacao datetime default null,
    data_alteracao datetime default null,
    data_cadastro datetime default null,
    origem_cadastro varchar(3) default null
);

create table openk_semaforo.pedido
(
    id bigint(20) not null auto_increment primary key,
    pedido_oking_id bigint(20) not null,
    pedido_venda_id varchar(50),
    pedido_canal varchar(50),
    numero_pedido_externo varchar(50),
    data_pedido datetime not null,
    status varchar(50),
    cliente_id bigint(20) not null,
    valor decimal(9, 2) not null,
    valor_desconto decimal(9, 2) default 0.0 not null,
    valor_frete decimal(9, 2) default 0.0 not null,
    valor_adicional_forma_pagt decimal(9, 2) default 0.0 not null,
    data_pagamento datetime default null,
    tipo_pagamento varchar(100) not null,
    bandeira varchar(100) not null,
    parcelas int default 1 not null,
    condicao_pagamento_erp varchar(50),
    opcao_pagamento_erp varchar(50),
    codigo_rastreio varchar(255) default null,
    data_previsao_entrega datetime default null,
    transportadora varchar(60) default null,
    opcao_forma_entrega varchar(150) default null,
    modo_envio varchar(50) default null,
    canal_id int not null,
    loja_id int default null,
    codigo_representante varchar(15) default null,
    cnpj_intermediador varchar(15) default null,
    identificador_vendedor varchar(100) default null,
    
    end_entrega_cep varchar(8) default null,
    end_entrega_tipo_logradouro varchar(20) default null,
    end_entrega_logradouro varchar(255) default null,
    end_entrega_numero varchar(20) default null,
    end_entrega_complemento varchar(255) default null,
    end_entrega_bairro varchar(255) default null,
    end_entrega_cidade varchar(255) default null,
    end_entrega_estado varchar(2) default null,
    end_entrega_referencia_ent varchar(255) default null,
    end_entrega_codigo_ibge varchar(15) default null,

    data_sincronizacao datetime default null,
    data_sincronizacao_nf datetime default null,
    data_sincronizacao_rastreio datetime default null,
    log_integracao varchar(4000) default null,
    status_observacao varchar(4000) default null,
    data_sincronizacao_entrega  datetime default null,
    modalidade_venda varchar(50) null,    
    descritor_pre_definido_2 varchar(100) default null,
    descritor_pre_definido_3 varchar(100) default null,
    descritor_pre_definido_4 varchar(100) default null,
    descritor_pre_definido_5 varchar(100) default null,
    descritor_pre_definido_6 varchar(100) default null,
    
    constraint fk_pedido_cliente foreign key (cliente_id)
        references openk_semaforo.cliente (id)
);

create table openk_semaforo.itens_pedido
(
    id bigint(20) auto_increment primary key,
    pedido_id bigint(20) not null,
    sku varchar(55) not null,
    codigo_erp varchar(55) not null,
    quantidade int not null,
    ean varchar(50) null,
    valor decimal(9,2) not null,
    valor_desconto decimal(9,2) default 0 not null,
    valor_frete	decimal(9,2) default 0.0 not null,
    filial_expedicao varchar(45) default null,
    filial_faturamento varchar(45) default null,
    cnpj_filial_venda varchar(14) default null,
    codigo_filial_erp varchar(255) default null,
    codigo_filial_expedicao_erp varchar(45) default null,
    codigo_filial_faturament_erp varchar(45) default null,
    valor_substituicao_tributaria decimal(9,2),
    iva decimal(9,2),
    icms_intraestadual decimal(9,2),
    icms_interestadual decimal(9,2),
    valor_icms_interestadual decimal(9,2),
    percentual_ipi decimal(9,2),
    valor_ipi decimal(9,2),

    
    constraint fk_itens_pedido_pedido foreign key (pedido_id)
        references openk_semaforo.pedido (id)
);

create table openk_semaforo.estoque_produto
(
    codigo_unidade_distribuicao varchar(45) not null,
    codigo_erp varchar(50) not null,
    quantidade int not null,
    data_atualizacao datetime not null,
    data_sincronizacao datetime default null,
    loja_id int default null,
    primary key (codigo_erp, codigo_unidade_distribuicao)
);

create table openk_semaforo.preco_produto
(
    codigo_erp varchar(50) not null primary key,
    preco_atual decimal(9,2) not null,
    preco_lista decimal(9,2) not null,
    preco_custo decimal(9,2) not null,
    data_atualizacao datetime not null,
    data_sincronizacao datetime default null,
    codigo_externo_campanha varchar(20) default null,
    loja_id int default null
);

create table openk_semaforo.produto
(
    codigo_erp varchar(50) not null primary key ,
    codigo_erp_sku varchar(50) not null,
    data_atualizacao datetime null,
    data_sincronizacao datetime null,
    data_envio_foto datetime null
);

create table openk_semaforo.tipo
(
    id int auto_increment primary key,
    nome varchar(50)
);

insert into openk_semaforo.tipo (id, nome) values (1, 'PRODUTO');
insert into openk_semaforo.tipo (id, nome) values (2, 'ESTOQUE');
insert into openk_semaforo.tipo (id, nome) values (3, 'PRECO');
insert into openk_semaforo.tipo (id, nome) values (4, 'FOTO');
insert into openk_semaforo.tipo (id, nome) values (5, 'CLIENTE');
insert into openk_semaforo.tipo (id, nome) values (6, 'PEDIDO');
insert into openk_semaforo.tipo (id, nome) values (7, 'NOTA_FISCAL');
insert into openk_semaforo.tipo (id, nome) values (8, 'CONDICAO_PAGAMENTO');
insert into openk_semaforo.tipo (id, nome) values (9, 'REPRESENTANTE');
insert into openk_semaforo.tipo (id, nome) values (10, 'IMPOSTO');
insert into openk_semaforo.tipo (id, nome) values (11, 'LISTA_PRECO');
insert into openk_semaforo.tipo (id, nome) values (12,'LISTA_PRECO_PRODUTO');
insert into openk_semaforo.tipo (id, nome) values (13,'PLANO_PAGAMENTO_CLIENTE');
insert into openk_semaforo.tipo (id, nome) values (14,'COLETA_DADOS_CLIENTE');
insert into openk_semaforo.tipo (id, nome) values (15,'COLETA_DADOS_VENDA');
insert into openk_semaforo.tipo (id, nome) values (16,'PRODUTO_RELACIONADO');
insert into openk_semaforo.tipo (id, nome) values (17,'VENDA_SUGERIDA');
insert into openk_semaforo.tipo (id, nome) values (18,'PRODUTO_CROSSELLING');
insert into openk_semaforo.tipo (id, nome) values (19,'PRODUTO_LANCAMENTO');
insert into openk_semaforo.tipo (id, nome) values (20,'PRODUTO_VITRINE');
insert into openk_semaforo.tipo (id, nome) values (21,'COLETA_DADOS_COMPRA');
insert into openk_semaforo.tipo (id, nome) values (22,'PEDIDO_PARA_OKVENDAS');
insert into openk_semaforo.tipo (id, nome) values (23, 'PONTO_FIDELIDADE');
insert into openk_semaforo.tipo (id, nome) values (24, 'UNIDADE_DISTRIBUICAO');
insert into openk_semaforo.tipo (id, nome) values (25, 'FILIAL');
insert into openk_semaforo.tipo (id, nome) values (26, 'TRANSPORTADORA');


create table openk_semaforo.semaforo
(
    identificador varchar(100) not null,
    identificador2 varchar(100) not null default '',
    tipo_id int,
    data_alteracao datetime default null comment 'Data da ultima alteracao',
    data_sincronizacao datetime default null comment 'Data da ultima sincronizacao',
    mensagem varchar(150) default null ,
    primary key (identificador, identificador2, tipo_id),
    constraint fk_semaforo_tipo foreign key (tipo_id) references openk_semaforo.tipo (id)
);'''
    elif connection_type.lower() == 'oracle':
        return '''CREATE USER OPENK_SEMAFORO
  IDENTIFIED BY openk
  DEFAULT TABLESPACE USERS
  TEMPORARY TABLESPACE TEMP
  PROFILE DEFAULT
  ACCOUNT UNLOCK'''

    elif connection_type.lower() == 'sql':
        return '''create schema openk_semaforo;
use openk_semaforo;
ALTER AUTHORIZATION ON DATABASE::[openk_semaforo] TO [openk];
create table cliente
(
    id bigint not null primary key identity,
    nome varchar(255) default null,
    razao_social varchar(255) default null,
    tipo_pessoa varchar(1) default null,
    cpf_cnpj varchar(14) default null,
    email varchar(255) default null,
    rg varchar(15) default null,
    data_nascimento_constituicao datetime default null,
    sexo varchar(1) default null,
    orgao varchar(5) default null,
    
    telefone_residencial varchar(20) default null,
    telefone_celular varchar(20) default null,
    inscricao_estadual varchar(25) default null,
    inscricao_municipal varchar(25) default null,
    codigo_representante varchar(15) default null,
    codigo_referencia_erp varchar(20) default null,   
    
    end_principal_cep varchar(8) default null,
    end_principal_tipologradouro varchar(20) default null,
    end_principal_logradouro varchar(255) default null,
    end_principal_numero varchar(20) default null,
    end_principal_complemento varchar(255) default null,
    end_principal_bairro varchar(255) default null,
    end_principal_cidade varchar(255) default null,
    end_principal_estado varchar(2) default null,
    END_PRINCIPAL_REFERENCIA_ENT varchar(255) default null,
    end_principal_codigo_ibge varchar(15) default null,     
    
    direcao varchar(3) default 'OUT',
    data_sincronizacao datetime default null,
    data_alteracao datetime default null,
    data_cadastro datetime default null,
    origem_cadastro varchar(3) default null
);

-- Adicionando o comentário à coluna
EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'Codigo do cliente no ERP', 
    @level0type = N'SCHEMA', @level0name = dbo, 
    @level1type = N'TABLE',  @level1name = cliente, 
    @level2type = N'COLUMN', @level2name = codigo_referencia_erp;

create table pedido
(
    id bigint not null primary key identity,
    pedido_oking_id bigint not null,
    pedido_venda_id varchar(50),
    pedido_canal varchar(50),
    numero_pedido_externo varchar(50),
    data_pedido datetime not null,
    status varchar(50),
    cliente_id bigint not null,
    valor decimal(9, 2) not null,
    valor_desconto decimal(9, 2) default 0.0 not null,
    valor_frete decimal(9, 2) default 0.0 not null,
    valor_adicional_forma_pagt decimal(9, 2) default 0.0 not null,
    data_pagamento datetime default null,
    tipo_pagamento varchar(100) not null,
    bandeira varchar(100) not null,
    parcelas int default 1 not null,
    condicao_pagamento_erp varchar(50),
    opcao_pagamento_erp varchar(50),
    codigo_rastreio varchar(255) default null,
    data_previsao_entrega datetime default null,
    transportadora varchar(60) default null,
    opcao_forma_entrega varchar(150) default null,
    modo_envio varchar(50) default null,
    canal_id int not null,
    loja_id int default null,
    codigo_representante varchar(15) default null,
    cnpj_intermediador varchar(15) default null,
    identificador_vendedor varchar(100) default null,
    
    end_entrega_cep varchar(8) default null,
    end_entrega_tipo_logradouro varchar(20) default null,
    end_entrega_logradouro varchar(255) default null,
    end_entrega_numero varchar(20) default null,
    end_entrega_complemento varchar(255) default null,
    end_entrega_bairro varchar(255) default null,
    end_entrega_cidade varchar(255) default null,
    end_entrega_estado varchar(2) default null,
    end_entrega_referencia_ent varchar(255) default null,
    end_entrega_codigo_ibge varchar(15) default null,

    data_sincronizacao datetime default null,
    data_sincronizacao_nf datetime default null,
    data_sincronizacao_rastreio datetime default null,
    log_integracao varchar(4000) default null,
    status_observacao varchar(4000) default null,
    data_sincronizacao_entrega  datetime default null,
    
    descritor_pre_definido_2 varchar(100) default null,
    descritor_pre_definido_3 varchar(100) default null,
    descritor_pre_definido_4 varchar(100) default null,
    descritor_pre_definido_5 varchar(100) default null,
    descritor_pre_definido_6 varchar(100) default null,
    
    constraint fk_pedido_cliente foreign key (cliente_id)
        references cliente (id)
);

create table itens_pedido
(
    id bigint primary key identity,
    pedido_id bigint not null,
    sku varchar(55) not null,
    codigo_erp varchar(55) not null,
    quantidade int not null,
    ean varchar(50) null,
    valor decimal(9,2) not null,
    valor_desconto decimal(9,2) default 0 not null,
    valor_frete	decimal(9,2) default 0.0 not null,
    filial_expedicao varchar(45) default null,
    filial_faturamento varchar(45) default null,
    cnpj_filial_venda varchar(14) default null,
    codigo_filial_erp varchar(255) default null,
    codigo_filial_expedicao_erp varchar(45) default null,
    codigo_filial_faturament_erp varchar(45) default null,
    constraint fk_itens_pedido_pedido foreign key (pedido_id)
        references pedido (id)
);

create table estoque_produto
(
    codigo_unidade_distribuicao varchar(45) not null,
    codigo_erp varchar(50) not null,
    quantidade int not null,
    data_atualizacao datetime not null,
    data_sincronizacao datetime default null,
    loja_id int default null,
    primary key (codigo_erp, codigo_unidade_distribuicao)
);

create table preco_produto
(
    codigo_erp varchar(50) not null primary key,
    preco_atual decimal(9,2) not null,
    preco_lista decimal(9,2) not null,
    preco_custo decimal(9,2) not null,
    data_atualizacao datetime not null,
    data_sincronizacao datetime default null,
    codigo_externo_campanha varchar(20) default null,
    loja_id int default null
);

create table produto
(
    codigo_erp varchar(50) not null primary key ,
    codigo_erp_sku varchar(50) not null,
    data_atualizacao datetime null,
    data_sincronizacao datetime null,
    data_envio_foto datetime null
);

create table tipo
(
    id int identity primary key,
    nome varchar(50)
);

insert into tipo ( nome) values ( 'PRODUTO');
insert into tipo ( nome) values ( 'ESTOQUE');
insert into tipo ( nome) values ( 'PRECO');
insert into tipo ( nome) values ( 'FOTO');
insert into tipo ( nome) values ( 'CLIENTE');
insert into tipo ( nome) values ( 'PEDIDO');
insert into tipo ( nome) values ( 'NOTA_FISCAL');
insert into tipo ( nome) values ( 'CONDICAO_PAGAMENTO');
insert into tipo ( nome) values ( 'REPRESENTANTE');
insert into tipo ( nome) values ( 'IMPOSTO');
insert into tipo ( nome) values ( 'LISTA_PRECO');
insert into tipo ( nome) values ('LISTA_PRECO_PRODUTO');
insert into tipo ( nome) values ('PLANO_PAGAMENTO_CLIENTE');
insert into tipo ( nome) values ('COLETA_DADOS_CLIENTE');
insert into tipo ( nome) values ('COLETA_DADOS_VENDA');
insert into tipo ( nome) values ('PRODUTO_RELACIONADO');
insert into tipo ( nome) values ('VENDA_SUGERIDA');
insert into tipo ( nome) values ('PRODUTO_CROSSELLING');
insert into tipo ( nome) values ('PRODUTO_LANCAMENTO');
insert into tipo ( nome) values ('PRODUTO_VITRINE');
insert into tipo ( nome) values ('COLETA_DADOS_COMPRA');
insert into tipo ( nome) values ('PEDIDO_PARA_OKVENDAS');
insert into tipo ( nome) values ('PONTO_FIDELIDADE');
insert into tipo ( nome) values ('UNIDADE_DISTRIBUICAO');
insert into tipo ( nome) values ('FILIAL');
insert into tipo ( nome) values ('TRANSPORTADORA');

create table semaforo
(
    identificador varchar(100) not null,
    identificador2 varchar(100) not null default '',
    tipo_id int,
    data_alteracao datetime default null,
    data_sincronizacao datetime default null,
    mensagem varchar(150) default null,
    primary key (identificador, identificador2, tipo_id),
    constraint fk_semaforo_tipo foreign key (tipo_id) references openk_semaforo.tipo (id)
);'''
    elif connection_type.lower() == 'firebird':
        package = import_package('firebirdsql')
        package.connect(user=src.client_data['user'], password=src.client_data['password'],
                        database=f'{src.client_data["diretorio_client"]}/{src.client_data["database"]}.fdb',
                        host=src.client_data['host'])


def comandos_oracle(seq: int):
    if seq == 1:
        return 'GRANT DBA TO OPENK_SEMAFORO'
    elif seq == 2:
        return 'ALTER USER OPENK_SEMAFORO DEFAULT ROLE ALL'
    elif seq == 3:
        return 'GRANT ALL PRIVILEGES TO OPENK_SEMAFORO'
    elif seq == 4:
        return '''CREATE TABLE OPENK_SEMAFORO.CLIENTE
(
    ID INTEGER NOT NULL PRIMARY KEY,
    NOME VARCHAR(255) DEFAULT NULL,
    RAZAO_SOCIAL VARCHAR(255) DEFAULT NULL,
    TIPO_PESSOA VARCHAR(1) DEFAULT NULL,
    CPF_CNPJ VARCHAR(14) DEFAULT NULL,
    EMAIL VARCHAR(255) DEFAULT NULL,
    RG VARCHAR(15) DEFAULT NULL,
    DATA_NASCIMENTO_CONSTITUICAO DATE DEFAULT NULL,
    SEXO VARCHAR(1) DEFAULT NULL,
    ORGAO VARCHAR(5) DEFAULT NULL,
        
    TELEFONE_RESIDENCIAL VARCHAR(20) DEFAULT NULL,
    TELEFONE_CELULAR VARCHAR(20) DEFAULT NULL,
    INSCRICAO_ESTADUAL VARCHAR(25) DEFAULT NULL,
    INSCRICAO_MUNICIPAL VARCHAR(25) DEFAULT NULL,
    CODIGO_REPRESENTANTE VARCHAR(15) DEFAULT NULL,
    CODIGO_REFERENCIA_ERP VARCHAR(20) DEFAULT NULL,    
    
    END_PRINCIPAL_CEP VARCHAR(8) DEFAULT NULL,
    end_principal_tipologradouro VARCHAR(20) DEFAULT NULL,
    END_PRINCIPAL_LOGRADOURO VARCHAR(255) DEFAULT NULL,
    END_PRINCIPAL_NUMERO VARCHAR(20) DEFAULT NULL,
    END_PRINCIPAL_COMPLEMENTO VARCHAR(255) DEFAULT NULL,
    END_PRINCIPAL_BAIRRO VARCHAR(255) DEFAULT NULL,
    END_PRINCIPAL_CIDADE VARCHAR(255) DEFAULT NULL,
    END_PRINCIPAL_ESTADO VARCHAR(2) DEFAULT NULL,
    END_PRINCIPAL_REFERENCIA_ENT VARCHAR(255) DEFAULT NULL,
    END_PRINCIPAL_CODIGO_IBGE VARCHAR(15) DEFAULT NULL,    
    
    DIRECAO VARCHAR(3) DEFAULT 'OUT',
    DATA_ALTERACAO DATE DEFAULT NULL,
    DATA_SINCRONIZACAO DATE DEFAULT NULL,
    DATA_CADASTRO DATETIME DEFAULT NULL,
    ORIGEM_CADASTRO VARCHAR(3) DEFAULT NULL
    
)'''
    elif seq == 5:
        return 'CREATE SEQUENCE CLIENTE_SEQ START WITH 1'
    elif seq == 6:
        return '''CREATE OR REPLACE TRIGGER CLIENTE_BIR
                    BEFORE INSERT ON OPENK_SEMAFORO.CLIENTE
                    FOR EACH ROW
                    BEGIN
                        SELECT CLIENTE_SEQ.NEXTVAL INTO :new.ID FROM dual;
                    END;'''
    elif seq == 7:
        return '''create table OPENK_SEMAFORO.PEDIDO
(
    ID                              NUMBER not null primary key,
    PEDIDO_OKING_ID                 NUMBER NOT NULL,
    PEDIDO_VENDA_ID                 VARCHAR2(50),
    PEDIDO_CANAL                    VARCHAR2(50),
    NUMERO_PEDIDO_EXTERNO           VARCHAR2(50),
    DATA_PEDIDO                     DATE NOT NULL,
    STATUS                          VARCHAR2(50),
    CLIENTE_ID                      NUMBER not null,
    VALOR                           NUMBER(9, 2) not null,
    VALOR_DESCONTO                  NUMBER(9, 2) default 0   not null,
    VALOR_FRETE                     NUMBER(9, 2) default 0.0 not null,
    VALOR_ADICIONAL_FORMA_PAGT NUMBER(9, 2) default 0.0 not null,
    DATA_PAGAMENTO                  DATE default NULL,
    TIPO_PAGAMENTO                  VARCHAR2(100) not null,
    BANDEIRA                        VARCHAR2(100) not null,
    PARCELAS                        NUMBER default 1 not null,
    CONDICAO_PAGAMENTO_ERP          VARCHAR2(50),
    OPCAO_PAGAMENTO_ERP             VARCHAR2(50),
    CODIGO_RASTREIO                 VARCHAR2(255) default NULL,
    DATA_PREVISAO_ENTREGA           DATE default NULL,
    TRANSPORTADORA                  VARCHAR2(60) default NULL,
    OPCAO_FORMA_ENTREGA             VARCHAR(150) default NULL,
    MODO_ENVIO                      VARCHAR2(50) default NULL,    
    CANAL_ID                        INTEGER not null,
    LOJA_ID                         NUMBER default NULL,
    CODIGO_REPRESENTANTE 	        VARCHAR2(15) default NULL,
    CNPJ_INTERMEDIADOR 		        VARCHAR2(15) default NULL,
    IDENTIFICADOR_VENDEDOR          VARCHAR2(100) default NULL,
    
    END_ENTREGA_CEP 		        VARCHAR2(8) default NULL,
    END_ENTREGA_TIPO_LOGRADOURO     VARCHAR2(20) default NULL,
    END_ENTREGA_LOGRADOURO 	        VARCHAR2(255) default NULL,
    END_ENTREGA_NUMERO 		        VARCHAR2(20) default NULL,
    END_ENTREGA_COMPLEMENTO         VARCHAR2(255) default NULL,
    END_ENTREGA_BAIRRO     		    VARCHAR2(255) default NULL,
    END_ENTREGA_CIDADE 		        VARCHAR(255) default NULL,
    END_ENTREGA_ESTADO 		        VARCHAR2(2) default NULL,
    END_ENTREGA_REFERENCIA_ENT      VARCHAR2(255) default NULL,
    END_ENTREGA_CODIGO_IBGE         VARCHAR2(15) default NULL,
    
    DATA_SINCRONIZACAO              DATE default NULL,
    DATA_SINCRONIZACAO_NF           DATE default NULL,
    DATA_SINCRONIZACAO_RASTREIO     DATE default NULL,
    LOG_INTEGRACAO                  VARCHAR2(4000) default NULL,
    STATUS_OBSERVACAO               VARCHAR2(4000) default NULL,
    DATA_SINCRONIZACAO_ENTREGA      DATE default null 
    
    DESCRITOR_PRE_DEFINIDO_2 VARCHAR(100) default NULL,
    DESCRITOR_PRE_DEFINIDO_3 VARCHAR(100) default NULL,
    DESCRITOR_PRE_DEFINIDO_4 VARCHAR(100) default NULL,
    DESCRITOR_PRE_DEFINIDO_5 VARCHAR(100) default NULL,
    DESCRITOR_PRE_DEFINIDO_6 VARCHAR(100) default NULL,
    
)'''
    elif seq == 8:
        return 'CREATE SEQUENCE PEDIDO_SEQ START WITH 1'
    elif seq == 9:
        return '''CREATE OR REPLACE TRIGGER PEDIDO_BIR
                    BEFORE INSERT ON OPENK_SEMAFORO.PEDIDO
                    FOR EACH ROW
                    BEGIN
                        SELECT PEDIDO_SEQ.NEXTVAL INTO :new.ID FROM dual;
                    END;'''
    elif seq == 10:
        return '''CREATE TABLE OPENK_SEMAFORO.ITENS_PEDIDO
(
    ID                              INTEGER PRIMARY KEY,
    PEDIDO_ID                       INTEGER NOT NULL,
    SKU                             VARCHAR2(55) NOT NULL,
    CODIGO_ERP                      VARCHAR2(55) NOT NULL,
    QUANTIDADE                      INTEGER NOT NULL,
    EAN                             VARCHAR2(50) default NULL,
    VALOR                           NUMBER(9,2) NOT NULL,
    VALOR_DESCONTO                  NUMBER(9,2) default 0 NOT NULL,
    VALOR_FRETE	                    NUMBER(9,2) default 0.0 NOT NULL,
    FILIAL_EXPEDICAO                VARCHAR2(45) default NULL,
    FILIAL_FATURAMENTO              VARCHAR2(45) default NULL,
    CNPJ_FILIAL_VENDA               VARCHAR2(14) default NULL,
    CODIGO_FILIAL_ERP               VARCHAR(255) default NULL,
    CODIGO_FILIAL_EXPEDICAO_ERP     VARCHAR(45) default NULL,
    CODIGO_FILIAL_FATURAMENT_ERP    VARCHAR(45) default NULL
)'''
    elif seq == 11:
        return '''CREATE SEQUENCE ITENS_PEDIDO_SEQ START WITH 1'''
    elif seq == 12:
        return '''CREATE OR REPLACE TRIGGER ITENS_PEDIDO_BIR
                    BEFORE INSERT ON OPENK_SEMAFORO.ITENS_PEDIDO
                    FOR EACH ROW
                    BEGIN
                        SELECT ITENS_PEDIDO_SEQ.NEXTVAL INTO :new.ID FROM dual;
                    END;'''
    elif seq == 13:
        return '''CREATE TABLE OPENK_SEMAFORO.ESTOQUE_PRODUTO
(
    CODIGO_UNIDADE_DISTRIBUICAO     VARCHAR2(45 BYTE) NOT NULL,
    CODIGO_ERP                      VARCHAR2(50 BYTE) NOT NULL,
    QUANTIDADE                      FLOAT(11) NOT NULL,
    DATA_ATUALIZACAO                DATE     NOT NULL,
    DATA_SINCRONIZACAO              DATE     DEFAULT NULL,
    LOJA_ID                         NUMBER DEFAULT NULL
)'''
    elif seq == 14:
        return '''ALTER TABLE OPENK_SEMAFORO.ESTOQUE_PRODUTO ADD (
                  PRIMARY KEY
                  (CODIGO_UNIDADE_DISTRIBUICAO, CODIGO_ERP)
                  USING INDEX
                    TABLESPACE USERS
                    PCTFREE    10
                    INITRANS   2
                    MAXTRANS   255
                    STORAGE    (
                                INITIAL          64K
                                NEXT             1M
                                MINEXTENTS       1
                                MAXEXTENTS       UNLIMITED
                                PCTINCREASE      0
                                BUFFER_POOL      DEFAULT
                                FLASH_CACHE      DEFAULT
                                CELL_FLASH_CACHE DEFAULT
                               )
                  ENABLE VALIDATE)'''
    elif seq == 15:
        return '''create table OPENK_SEMAFORO.PRECO_PRODUTO
(
    CODIGO_ERP                      VARCHAR2(15) not null,
    PRECO_ATUAL                     FLOAT        not null,
    PRECO_LISTA                     FLOAT        not null,
    PRECO_CUSTO                     FLOAT        not null,
    DATA_ATUALIZACAO                DATE         not null,
    DATA_SINCRONIZACAO              DATE         default NULL,
    CODIGO_EXTERNO_CAMPANHA         VARCHAR2(20) default null,
    LOJA_ID                         NUMBER DEFAULT NULL
)'''
    elif seq == 16:
        return '''ALTER TABLE OPENK_SEMAFORO.PRECO_PRODUTO ADD (
                  PRIMARY KEY
                  (CODIGO_ERP)
                  USING INDEX
                    TABLESPACE USERS
                    PCTFREE    10
                    INITRANS   2
                    MAXTRANS   255
                    STORAGE    (
                                INITIAL          64K
                                NEXT             1M
                                MINEXTENTS       1
                                MAXEXTENTS       UNLIMITED
                                PCTINCREASE      0
                                BUFFER_POOL      DEFAULT
                                FLASH_CACHE      DEFAULT
                                CELL_FLASH_CACHE DEFAULT
                               )
                  ENABLE VALIDATE)'''
    elif seq == 17:
        return '''CREATE TABLE OPENK_SEMAFORO.PRODUTO
(
    CODIGO_ERP                      VARCHAR(50) NOT NULL,
    CODIGO_ERP_SKU                  VARCHAR(50) NOT NULL,
    DATA_ATUALIZACAO                DATE NULL,
    DATA_SINCRONIZACAO              DATE NULL,
    DATA_ENVIO_FOTO                 DATE null
)'''
    elif seq == 18:
        return '''ALTER TABLE OPENK_SEMAFORO.PRODUTO ADD (
                  PRIMARY KEY
                  (CODIGO_ERP, CODIGO_ERP_SKU)
                  USING INDEX
                    TABLESPACE USERS
                    PCTFREE    10
                    INITRANS   2
                    MAXTRANS   255
                    STORAGE    (
                                INITIAL          64K
                                NEXT             1M
                                MINEXTENTS       1
                                MAXEXTENTS       UNLIMITED
                                PCTINCREASE      0
                                BUFFER_POOL      DEFAULT
                                FLASH_CACHE      DEFAULT
                                CELL_FLASH_CACHE DEFAULT
                               )
                  ENABLE VALIDATE)'''
    elif seq == 19:
        return '''create table openk_semaforo.tipo
(
    ID                              INTEGER primary key,
    NOME                            VARCHAR2(50)
)'''
    elif seq == 20:
        return '''insert into openk_semaforo.tipo (id, nome) values (1, 'PRODUTO')'''
    elif seq == 21:
        return '''insert into openk_semaforo.tipo (id, nome) values (2, 'ESTOQUE')'''
    elif seq == 22:
        return '''insert into openk_semaforo.tipo (id, nome) values (3, 'PRECO')'''
    elif seq == 23:
        return '''insert into openk_semaforo.tipo (id, nome) values (4, 'FOTO')'''
    elif seq == 24:
        return '''insert into openk_semaforo.tipo (id, nome) values (5, 'CLIENTE')'''
    elif seq == 25:
        return '''insert into openk_semaforo.tipo (id, nome) values (6, 'PEDIDO')'''
    elif seq == 26:
        return '''insert into openk_semaforo.tipo (id, nome) values (7, 'NOTA_FISCAL')'''
    elif seq == 27:
        return '''insert into openk_semaforo.tipo (id, nome) values (8, 'CONDICAO_PAGAMENTO')'''
    elif seq == 28:
        return '''insert into openk_semaforo.tipo (id, nome) values (9, 'REPRESENTANTE')'''
    elif seq == 29:
        return '''insert into openk_semaforo.tipo (id, nome) values (10, 'IMPOSTO')'''
    elif seq == 30:
        return '''insert into openk_semaforo.tipo (id, nome) values (11, 'LISTA_PRECO')'''
    elif seq == 31:
        return '''insert into openk_semaforo.tipo (id, nome) values (12, 'LISTA_PRECO_PRODUTO')'''
    elif seq == 32:
        return '''insert into openk_semaforo.tipo (id, nome) values (13, 'PLANO_PAGAMENTO_CLIENTE')'''
    elif seq == 33:
        return '''insert into openk_semaforo.tipo (id, nome) values (14,'COLETA_DADOS_CLIENTE')'''
    elif seq == 34:
        return '''insert into openk_semaforo.tipo (id, nome) values (15,'COLETA_DADOS_VENDA')'''
    elif seq == 35:
        return '''insert into openk_semaforo.tipo (id, nome) values (16,'PRODUTO_RELACIONADO')'''
    elif seq == 36:
        return '''insert into openk_semaforo.tipo (id, nome) values (17,'VENDA_SUGERIDA')'''
    elif seq == 37:
        return '''insert into openk_semaforo.tipo (id, nome) values (18,'PRODUTO_CROSSELLING')'''
    elif seq == 38:
        return '''insert into openk_semaforo.tipo (id, nome) values (19,'PRODUTO_LANCAMENTO')'''
    elif seq == 39:
        return '''insert into openk_semaforo.tipo (id, nome) values (20,'PRODUTO_VITRINE')'''
    elif seq == 40:
        return '''insert into openk_semaforo.tipo (id, nome) values (21,'COLETA_DADOS_COMPRA')'''
    elif seq == 41:
        return '''insert into openk_semaforo.tipo (id, nome) values (22,'PEDIDO_PARA_OKVENDAS')'''
    elif seq == 42:
        return '''insert into openk_semaforo.tipo (id, nome) values (23, 'PONTO_FIDELIDADE')'''
    elif seq == 43:
        return '''insert into openk_semaforo.tipo (id, nome) values (24, 'UNIDADE_DISTRIBUICAO')'''
    elif seq == 44:
        return '''insert into openk_semaforo.tipo (id, nome) values (25, 'FILIAL')'''
    elif seq == 45:
        return '''create table openk_semaforo.semaforo
                (
                    IDENTIFICADOR                   VARCHAR2(100) NOT NULL,
                    IDENTIFICADOR2                  VARCHAR2(100) DEFAULT '' NOT NULL,
                    TIPO_ID                         INT,
                    DATA_ALTERACAO                  DATE DEFAULT NULL,
                    DATA_SINCRONIZACAO              DATE DEFAULT NULL,
                    MENSAGEM                        VARCHAR2(150) DEFAULT NULL,
                    PRIMARY KEY (IDENTIFICADOR, IDENTIFICADOR2, TIPO_ID),
                    CONSTRAINT FK_SEMAFORO_TIPO FOREIGN KEY (TIPO_ID) REFERENCES OPENK_SEMAFORO.TIPO (ID)
                )'''
    elif seq == 46:
        return '''insert into openk_semaforo.tipo (id, nome) values (26, 'TRANSPORTADORA')'''


def comandos_firebird(seq: int):
    if seq == 1:
        '''create table semaforo_cliente
        (
            id bigint not null primary key,
            nome varchar(255) default null,
            razao_social varchar(255) default null,
            tipo_pessoa varchar(1) default null,
            cpf_cnpj varchar(14) default null,
            email varchar(255) default null,
            rg varchar(15) default null,
            data_nascimento_constituicao timestamp default null,
            sexo varchar(1) default null,
            orgao varchar(5) default null,
            telefone_residencial varchar(20) default null,
            telefone_celular varchar(20) default null,
            inscricao_estadual varchar(25) default null,
            inscricao_municipal varchar(25) default null,
            codigo_representante varchar(15) default null,
            codigo_referencia_erp varchar(20) default null,
            end_principal_cep varchar(8) default null,
            end_principal_tipologradouro varchar(20) default null,
            end_principal_logradouro varchar(255) default null,
            end_principal_numero varchar(20) default null,
            end_principal_complemento varchar(255) default null,
            end_principal_bairro varchar(255) default null,
            end_principal_cidade varchar(255) default null,
            end_principal_estado varchar(2) default null,
            END_PRINCIPAL_REFERENCIA_ENT varchar(255) default null,
            end_principal_codigo_ibge varchar(15) default null,
            direcao varchar(3) default 'OUT',
            data_sincronizacao timestamp default null,
            data_alteracao timestamp default null,
            data_cadastro datetime default null,
            origem_cadastro varchar(3) default null
        );'''
    elif seq == 2:
        '''CREATE GENERATOR semaforo_cliente_generator;'''
    elif seq == 3:
        '''CREATE TRIGGER semaforo_inc_cliente for semaforo_cliente
            BEFORE INSERT position 0
            AS
            BEGIN
            new.id = gen_id(semaforo_cliente_generator,1);
            END;'''
    elif seq == 4:
        '''create table semaforo_pedido
        (
            id bigint not null primary key,
            pedido_oking_id bigint not null,
            pedido_venda_id varchar(50),
            pedido_canal varchar(50),
            numero_pedido_externo varchar(50),
            data_pedido timestamp not null,
            status varchar(50),
            cliente_id bigint not null,
            valor decimal(9, 2) not null,
            valor_desconto decimal(9, 2) default 0.0 not null,
            valor_frete decimal(9, 2) default 0.0 not null,
            valor_adicional_forma_pagt decimal(9, 2) default 0.0 not null,
            data_pagamento timestamp default null,
            tipo_pagamento varchar(100) not null,
            bandeira varchar(100) not null,
            parcelas int default 1 not null,
            condicao_pagamento_erp varchar(50),
            opcao_pagamento_erp varchar(50),
            codigo_rastreio varchar(255) default null,
            data_previsao_entrega timestamp default null,
            transportadora varchar(60) default null,
            opcao_forma_entrega varchar(150) default null,
            modo_envio varchar(50) default null,
            canal_id int not null,
            loja_id int default null,
            codigo_representante varchar(15) default null,
            cnpj_intermediador varchar(15) default null,
            identificador_vendedor varchar(100) default null,
            end_entrega_cep varchar(8) default null,
            end_entrega_tipo_logradouro varchar(20) default null,
            end_entrega_logradouro varchar(255) default null,
            end_entrega_numero varchar(20) default null,
            end_entrega_complemento varchar(255) default null,
            end_entrega_bairro varchar(255) default null,
            end_entrega_cidade varchar(255) default null,
            end_entrega_estado varchar(2) default null,
            end_entrega_referencia_ent varchar(255) default null,
            end_entrega_codigo_ibge varchar(15) default null,
            data_sincronizacao timestamp default null,
            data_sincronizacao_nf timestamp default null,
            data_sincronizacao_rastreio timestamp default null,
            log_integracao varchar(4000) default null,
            status_observacao varchar(4000) default null,
            data_sincronizacao_entrega  timestamp default null, 
            
            descritor_pre_definido_2 varchar(100) default null,
            descritor_pre_definido_3 varchar(100) default null,
            descritor_pre_definido_4 varchar(100) default null,
            descritor_pre_definido_5 varchar(100) default null,
            descritor_pre_definido_6 varchar(100) default null,
            constraint fk_semaforo_pedido_cliente foreign key (cliente_id)
                references semaforo_cliente (id)
        );'''
    elif seq == 5:
        '''CREATE GENERATOR semaforo_pedido_generator;'''
    elif seq == 6:
        '''CREATE TRIGGER semaforo_inc_pedido for semaforo_pedido
            BEFORE INSERT position 0
            AS
            BEGIN
            new.id = gen_id(semaforo_pedido_generator,1);
            END;'''
    elif seq == 7:
        '''create table semaforo_itens_pedido
        (
            id bigint primary key,
            pedido_id bigint not null,
            sku varchar(55) not null,
            codigo_erp varchar(55) not null,
            quantidade int not null,
            ean varchar(50) DEFAULT null,
            valor decimal(9,2) not null,
            valor_desconto decimal(9,2) default 0 not null,
            valor_frete	decimal(9,2) default 0.0 not null,
            filial_expedicao varchar(45) default null,
            filial_faturamento varchar(45) default null,
            cnpj_filial_venda varchar(14) default null,
            codigo_filial_erp varchar(255) default null,
            codigo_filial_expedicao_erp varchar(45) default null,
            codigo_filial_faturament_erp varchar(45) default null,
        
            
            constraint fk_semaforo_itens_pedido_pedido foreign key (pedido_id)
                references semaforo_pedido (id)
        );'''
    elif seq == 8:
        '''CREATE GENERATOR semaforo_itens_pedido_generator;'''
    elif seq == 9:
        '''CREATE TRIGGER semaforo_inc_itens_pedido for semaforo_itens_pedido
            BEFORE INSERT position 0
            AS
            BEGIN
            new.id = gen_id(semaforo_itens_pedido_generator,1);
            END;'''
    elif seq == 10:
        '''create table semaforo_estoque_produto
        (
            codigo_unidade_distribuicao varchar(45) not null,
            codigo_erp varchar(50) not null,
            quantidade int not null,
            data_atualizacao timestamp not null,
            data_sincronizacao timestamp default null,
            loja_id int default null,
            primary key (codigo_erp, codigo_unidade_distribuicao)
        );'''
    elif seq == 11:
        '''create table semaforo_preco_produto
        (
            codigo_erp varchar(50) not null primary key,
            preco_atual decimal(9,2) not null,
            preco_lista decimal(9,2) not null,
            preco_custo decimal(9,2) not null,
            data_atualizacao timestamp not null,
            data_sincronizacao timestamp default null,
            codigo_externo_campanha varchar(20) default null,
            loja_id int default null
        );'''
    elif seq == 12:
        '''create table semaforo_produto
        (
            codigo_erp varchar(50) not null primary key ,
            codigo_erp_sku varchar(50) not null,
            data_atualizacao timestamp DEFAULT null,
            data_sincronizacao timestamp DEFAULT null,
            data_envio_foto timestamp DEFAULT null
        );'''
    elif seq == 13:
        '''create table semaforo_tipo
        (
            id int primary key,
            nome varchar(50)
        );'''
    elif seq == 14:
        '''CREATE GENERATOR semaforo_tipo_generator;'''
    elif seq == 15:
        '''CREATE TRIGGER semaforo_inc_tipo for semaforo_tipo
            BEFORE INSERT position 0
            AS
            BEGIN
            new.id = gen_id(semaforo_tipo_generator,1);
            END;'''
    elif seq == 16:
        '''insert into semaforo_tipo (id, nome) values (1, 'PRODUTO');'''
    elif seq == 17:
        '''insert into semaforo_tipo (id, nome) values (2, 'ESTOQUE');'''
    elif seq == 18:
        '''insert into semaforo_tipo (id, nome) values (3, 'PRECO');'''
    elif seq == 19:
        '''insert into semaforo_tipo (id, nome) values (4, 'FOTO');'''
    elif seq == 20:
        '''insert into semaforo_tipo (id, nome) values (5, 'CLIENTE');'''
    elif seq == 21:
        '''insert into semaforo_tipo (id, nome) values (6, 'PEDIDO');'''
    elif seq == 22:
        '''insert into semaforo_tipo (id, nome) values (7, 'NOTA_FISCAL');'''
    elif seq == 23:
        '''insert into semaforo_tipo (id, nome) values (8, 'CONDICAO_PAGAMENTO');'''
    elif seq == 24:
        '''insert into semaforo_tipo (id, nome) values (9, 'REPRESENTANTE');'''
    elif seq == 25:
        '''insert into semaforo_tipo (id, nome) values (10, 'IMPOSTO');'''
    elif seq == 26:
        '''insert into semaforo_tipo (id, nome) values (11, 'LISTA_PRECO');'''
    elif seq == 27:
        '''insert into semaforo_tipo (id, nome) values (12,'LISTA_PRECO_PRODUTO');'''
    elif seq == 28:
        '''insert into semaforo_tipo (id, nome) values (13,'PLANO_PAGAMENTO_CLIENTE');'''
    elif seq == 29:
        '''insert into semaforo_tipo (id, nome) values (14,'COLETA_DADOS_CLIENTE');'''
    elif seq == 30:
        '''insert into semaforo_tipo (id, nome) values (15,'COLETA_DADOS_VENDA');'''
    elif seq == 31:
        '''insert into semaforo_tipo (id, nome) values (16,'PRODUTO_RELACIONADO');'''
    elif seq == 32:
        '''insert into semaforo_tipo (id, nome) values (17,'VENDA_SUGERIDA');'''
    elif seq == 33:
        '''insert into semaforo_tipo (id, nome) values (18,'PRODUTO_CROSSELLING');'''
    elif seq == 34:
        '''insert into semaforo_tipo (id, nome) values (19,'PRODUTO_LANCAMENTO');'''
    elif seq == 35:
        '''insert into semaforo_tipo (id, nome) values (20,'PRODUTO_VITRINE');'''
    elif seq == 36:
        '''insert into semaforo_tipo (id, nome) values (21,'COLETA_DADOS_COMPRA');'''
    elif seq == 37:
        '''insert into semaforo_tipo (id, nome) values (22,'PEDIDO_PARA_OKVENDAS');'''
    elif seq == 38:
        '''insert into semaforo_tipo (id, nome) values (23,'PONTO_FIDELIDADE');'''
    elif seq == 39:
        '''insert into semaforo_tipo (id, nome) values (24,'UNIDADE_DISTRIBUICAO');'''
    elif seq == 40:
        '''insert into semaforo_tipo (id, nome) values (25,'FILIAL');'''
    elif seq == 41:
        '''create table semaforo
        (
            identificador varchar(100) not null,
            identificador2 varchar(100) default '',
            tipo_id int,
            data_alteracao timestamp default null,
            data_sincronizacao timestamp default null,
            mensagem varchar(150) default null ,
            primary key (identificador, identificador2, tipo_id),
            constraint fk_semaforo_tipo foreign key (tipo_id) references semaforo_tipo (id)
        );'''
    elif seq == 42:
        '''insert into semaforo_tipo (id, nome) values (26,'TRANSPORTADORA');'''


def get_query_client_erp(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'select id from openk_semaforo.cliente where codigo_referencia_erp = %s'
    elif connection_type.lower() == 'oracle':
        return 'SELECT ID FROM OPENK_SEMAFORO.CLIENTE WHERE CODIGO_REFERENCIA_ERP = :1 '
    elif connection_type.lower() == 'sql':
        return 'select id from openk_semaforo.cliente where codigo_referencia_erp = ?'
    elif connection_type.lower() == 'firebird':
        return 'select id from semaforo_cliente where codigo_referencia_erp = ?'


# def get_query_cliente_cpfcnpj(connection_type: str):
#     if connection_type.lower() == 'mysql':
#         return 'select id from openk_semaforo.cliente where cpf_cnpj =  %s'
#     elif connection_type.lower() == 'oracle':
#         return 'SELECT ID FROM OPENK_SEMAFORO.CLIENTE WHERE CPF_CNPJ = :1 '
#     elif connection_type.lower() == 'sql':
#         return 'select id from openk_semaforo.cliente where cpf_cnpj = ?'
#     elif connection_type.lower() == 'firebird':
#         return 'select id from semaforo_cliente where cpf_cnpj = ?'
def get_query_cliente_cpfcnpj(connection_type: str, for_update: bool = False):
    base_query = {
        'mysql': 'SELECT id FROM openk_semaforo.cliente WHERE cpf_cnpj = %s',
        'oracle': 'SELECT ID FROM OPENK_SEMAFORO.CLIENTE WHERE CPF_CNPJ = :1',
        'sql': 'SELECT id FROM openk_semaforo.cliente WHERE cpf_cnpj = ?',
        'firebird': 'SELECT id FROM semaforo_cliente WHERE cpf_cnpj = ?'
    }
    
    lock_clause = " WITH (UPDLOCK, ROWLOCK) " if for_update else ""
    
    query = base_query.get(connection_type.lower(), base_query['mysql'])

    if connection_type.lower() == 'sql':
        query = query.format(lock_clause=lock_clause)  # SQL Server
    elif for_update and connection_type.lower() in ('mysql', 'oracle'):
        query += " FOR UPDATE"    # MySql, Oracle
    elif for_update and connection_type.lower() in 'firebird':
        query += "  WITH LOCK"  # Firebird
    
    return query    


def get_query_cpfcnpj_cliente_ByID(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'select cpf_cnpj from openk_semaforo.cliente where id =  %s'
    elif connection_type.lower() == 'oracle':
        return 'SELECT CPF_CNPJ FROM OPENK_SEMAFORO.CLIENTE WHERE ID = :1 '
    elif connection_type.lower() == 'sql':
        return 'select cpf_cnpj from openk_semaforo.cliente where id = ?'
    elif connection_type.lower() == 'firebird':
        return 'select cpf_cnpj from semaforo_cliente where  id = ?'


def get_insert_client_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''insert into openk_semaforo.cliente 
                  (nome, razao_social, tipo_pessoa, cpf_cnpj, sexo, email, rg, orgao, data_nascimento_constituicao
                  , telefone_residencial, telefone_celular, inscricao_estadual, inscricao_municipal
                  , codigo_referencia_erp, codigo_representante, end_principal_cep, end_principal_tipologradouro
                  , end_principal_logradouro, end_principal_numero, end_principal_complemento, end_principal_bairro
                  , end_principal_cidade, end_principal_estado, END_PRINCIPAL_REFERENCIA_ENT
                  , end_principal_codigo_ibge, direcao, origem_cadastro, DATA_CADASTRO )
          values ( %s,  %s,  %s,  %s,  %s,  %s,  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                  , %s, %s, %s, %s, %s, now())  '''
    elif connection_type.lower() == 'oracle':
        return '''INSERT INTO OPENK_SEMAFORO.CLIENTE 
                  (NOME, RAZAO_SOCIAL, TIPO_PESSOA, CPF_CNPJ, SEXO, EMAIL, RG, ORGAO, DATA_NASCIMENTO_CONSTITUICAO
                  , TELEFONE_RESIDENCIAL, TELEFONE_CELULAR, INSCRICAO_ESTADUAL, INSCRICAO_MUNICIPAL
                  , CODIGO_REFERENCIA_ERP, CODIGO_REPRESENTANTE, END_PRINCIPAL_CEP, end_principal_tipologradouro
                  , END_PRINCIPAL_LOGRADOURO, END_PRINCIPAL_NUMERO, END_PRINCIPAL_COMPLEMENTO, END_PRINCIPAL_BAIRRO
                  , END_PRINCIPAL_CIDADE, END_PRINCIPAL_ESTADO, END_PRINCIPAL_REFERENCIA_ENT
                  , END_PRINCIPAL_CODIGO_IBGE, DIRECAO, ORIGEM_CADASTRO, DATA_CADASTRO ) 
            VALUES (:1, :2, :3, :4, :5, :6, :7, :8, TO_DATE(:9, 'YYYY-MM-DD HH24:MI:SS'), :10, :11, :12, :13, :14, :15
                    , :16, :17, :18, :19, :20
                    , :21, :22, :23, :24, :25, :26, :27, SYSDATE )'''
    elif connection_type.lower() == 'sql':
        return '''insert into openk_semaforo.cliente 
                 (nome, razao_social, tipo_pessoa, cpf_cnpj, sexo, email, rg, orgao
                  , data_nascimento_constituicao, telefone_residencial, telefone_celular, inscricao_estadual
                  , inscricao_municipal, codigo_referencia_erp, codigo_representante, end_principal_cep
                  , end_principal_tipologradouro, end_principal_logradouro, end_principal_numero
                  , end_principal_complemento, end_principal_bairro, end_principal_cidade, end_principal_estado
                  , end_principal_referencia_ent, end_principal_codigo_ibge, direcao, origem_cadastro, data_cadastro )
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate() ) '''
    elif connection_type.lower() == 'firebird':
        return '''insert into semaforo_cliente 
                         (nome, razao_social, tipo_pessoa, cpf_cnpj, sexo, email, rg, orgao
                          , data_nascimento_constituicao, telefone_residencial, telefone_celular, inscricao_estadual
                          , inscricao_municipal, codigo_referencia_erp, codigo_representante, end_principal_cep
                          , end_principal_tipologradouro, end_principal_logradouro, end_principal_numero
                          , end_principal_complemento, end_principal_bairro, end_principal_cidade, end_principal_estado
                          , end_principal_referencia_ent, end_principal_codigo_ibge, direcao, origem_cadastro, 
                          data_cadastro )
                    values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                          CURRENT_TIMESTAMP ) '''


def get_update_client_sql(connection_type: str):
    if connection_type.lower() == 'mysql':
        newsql = '''update openk_semaforo.cliente
                    SET nome = %s
                      , razao_social = %s
                      , sexo = %s
                      , email = %s
                      , rg = %s
                      , orgao = %s
                      , data_nascimento_constituicao = %s
                      , telefone_residencial = %s
                      , telefone_celular = %s
                      , inscricao_estadual = %s
                      , inscricao_municipal = %s
                      , codigo_representante = %s
                      , end_principal_cep = %s
                      , end_principal_tipologradouro = %s
                      , end_principal_logradouro = %s
                      , end_principal_numero = %s
                      , end_principal_complemento = %s
                      , end_principal_bairro = %s
                      , end_principal_cidade = %s
                      , end_principal_estado = %s
                      , end_principal_referencia_ent = %s
                      , end_principal_codigo_ibge = %s
                      , data_alteracao = now()
                 WHERE id = %s
                '''

        return newsql

    elif connection_type.lower() == 'oracle':
        return '''UPDATE OPENK_SEMAFORO.CLIENTE
                     SET nome = :1
                      , razao_social = :2
                      , sexo = :3
                      , email = :4
                      , rg = :5
                      , orgao = :6
                      , data_nascimento_constituicao = TO_DATE(:7, 'YYYY-MM-DD HH24:MI:SS')
                      , telefone_residencial = :8
                      , telefone_celular = :9
                      , inscricao_estadual = :10
                      , inscricao_municipal = :11
                      , codigo_representante = :12
                      , end_principal_cep = :13
                      , end_principal_tipologradouro = :14
                      , end_principal_logradouro = :15
                      , end_principal_numero = :16
                      , end_principal_complemento = :17
                      , end_principal_bairro = :18
                      , end_principal_cidade = :19
                      , end_principal_estado = :20
                      , END_PRINCIPAL_REFERENCIA_ENT = :21
                      , end_principal_codigo_ibge = :22
                      , data_alteracao = SYSDATE
                 WHERE ID = :23 '''
    elif connection_type.lower() == 'sql':
        return '''update openk_semaforo.cliente
                    SET nome = ?
                      , razao_social = ?
                      , sexo = ?
                      , email = ?
                      , rg = ?
                      , orgao = ?
                      , data_nascimento_constituicao = ?
                      , telefone_residencial = ?
                      , telefone_celular = ?
                      , inscricao_estadual = ?
                      , inscricao_municipal = ?
                      , codigo_representante = ?
                      , end_principal_cep = ?
                      , end_principal_tipologradouro = ?
                      , end_principal_logradouro = ?
                      , end_principal_numero = ?
                      , end_principal_complemento = ?
                      , end_principal_bairro = ?
                      , end_principal_cidade = ?
                      , end_principal_estado = ?
                      , END_PRINCIPAL_REFERENCIA_ENT = ?
                      , end_principal_codigo_ibge = ?
                      , data_alteracao = getdate()
                    WHERE id = ? '''
    elif connection_type.lower() == 'firebird':
        return '''update semaforo_cliente
                            SET nome = ?
                              , razao_social = ?
                              , sexo = ?
                              , email = ?
                              , rg = ?
                              , orgao = ?
                              , data_nascimento_constituicao = ?
                              , telefone_residencial = ?
                              , telefone_celular = ?
                              , inscricao_estadual = ?
                              , inscricao_municipal = ?
                              , codigo_representante = ?
                              , end_principal_cep = ?
                              , end_principal_tipologradouro = ?
                              , end_principal_logradouro = ?
                              , end_principal_numero = ?
                              , end_principal_complemento = ?
                              , end_principal_bairro = ?
                              , end_principal_cidade = ?
                              , end_principal_estado = ?
                              , END_PRINCIPAL_REFERENCIA_ENT = ?
                              , end_principal_codigo_ibge = ?
                              , data_alteracao = CURRENT_TIMESTAMP
                            WHERE id = ? '''


def get_query_client_id(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'select id from openk_semaforo.cliente where email = %s'
    elif connection_type.lower() == 'oracle':
        return 'SELECT ID FROM OPENK_SEMAFORO.CLIENTE WHERE EMAIL = :email'
    elif connection_type.lower() == 'sql':
        return 'select id from openk_semaforo.cliente where email = ?'
    elif connection_type.lower() == 'firebird':
        return 'select id from semaforo_cliente where email = ?'


def get_insert_order_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''insert into openk_semaforo.pedido 
                         (pedido_oking_id, pedido_venda_id, pedido_canal, data_pedido, status, cliente_id, valor
                         , valor_desconto
                         , valor_frete, valor_adicional_forma_pagt, data_pagamento, tipo_pagamento, bandeira
                         , parcelas, condicao_pagamento_erp, opcao_pagamento_erp, codigo_rastreio
                         , data_previsao_entrega, transportadora, modo_envio, canal_id, loja_id
                         , codigo_representante, cnpj_intermediador, end_entrega_cep, end_entrega_tipo_logradouro
                         , end_entrega_logradouro, end_entrega_numero, end_entrega_complemento, end_entrega_bairro
                         , end_entrega_cidade, end_entrega_estado, end_entrega_referencia_ent
                         , end_entrega_codigo_ibge)
                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                          , %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  '''
    elif connection_type.lower() == 'oracle':
        return '''INSERT INTO OPENK_SEMAFORO.PEDIDO 
                        (pedido_oking_id, pedido_venda_id, pedido_canal, data_pedido, status, cliente_id, valor
                         , valor_desconto
                         , valor_frete, valor_adicional_forma_pagt, data_pagamento, tipo_pagamento, bandeira
                         , parcelas, condicao_pagamento_erp, opcao_pagamento_erp, codigo_rastreio
                         , data_previsao_entrega, transportadora, modo_envio, canal_id, loja_id
                         , codigo_representante, cnpj_intermediador, end_entrega_cep, end_entrega_tipo_logradouro
                         , end_entrega_logradouro, end_entrega_numero, end_entrega_complemento, end_entrega_bairro
                         , end_entrega_cidade, end_entrega_estado, end_entrega_referencia_ent
                         , end_entrega_codigo_ibge)
                VALUES (:1, :2, :3, TO_DATE(:4, 'YYYY-MM-DD HH24:MI:SS'), :5, :6, :7, :8, :9, :10
                       , TO_DATE(:11, 'YYYY-MM-DD HH24:MI:SS'), :12, :13, :14, :15, :16, :17
                       , TO_DATE(:18, 'YYYY-MM-DD HH24:MI:SS'), :19, :20, :21, :22, :23, :24, :25, :26, :27, :28
                       , :29, :30, :31, :32, :33, :34) '''
    elif connection_type.lower() == 'sql':
        return '''insert into openk_semaforo.pedido 
                        (pedido_oking_id, pedido_venda_id, pedido_canal, data_pedido, status, cliente_id, valor
                         , valor_desconto
                         , valor_frete, valor_adicional_forma_pagt, data_pagamento, tipo_pagamento, bandeira
                         , parcelas, condicao_pagamento_erp, opcao_pagamento_erp, codigo_rastreio
                         , data_previsao_entrega, transportadora, modo_envio, canal_id, loja_id
                         , codigo_representante, cnpj_intermediador, end_entrega_cep, end_entrega_tipo_logradouro
                         , end_entrega_logradouro, end_entrega_numero, end_entrega_complemento, end_entrega_bairro
                         , end_entrega_cidade, end_entrega_estado, end_entrega_referencia_ent
                         , end_entrega_codigo_ibge)
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                         , ?, ?, ? , ?) '''
    elif connection_type.lower() == 'firebird':
        return '''insert into semaforo_pedido 
                                (pedido_oking_id, pedido_venda_id, pedido_canal, data_pedido, status, cliente_id, valor
                                 , valor_desconto
                                 , valor_frete, valor_adicional_forma_pagt, data_pagamento, tipo_pagamento, bandeira
                                 , parcelas, condicao_pagamento_erp, opcao_pagamento_erp, codigo_rastreio
                                 , data_previsao_entrega, transportadora, modo_envio, canal_id, loja_id
                                 , codigo_representante, cnpj_intermediador, end_entrega_cep
                                 , end_entrega_tipo_logradouro
                                 , end_entrega_logradouro, end_entrega_numero, end_entrega_complemento
                                 , end_entrega_bairro
                                 , end_entrega_cidade, end_entrega_estado, end_entrega_referencia_ent
                                 , end_entrega_codigo_ibge)
                        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                                 , ?, ?, ? , ?) '''


def get_query_order(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'select id from openk_semaforo.pedido where pedido_oking_id = %s'
    elif connection_type.lower() == 'oracle':
        return 'SELECT ID FROM OPENK_SEMAFORO.PEDIDO WHERE PEDIDO_OKING_ID = :1'
    elif connection_type.lower() == 'sql':
        return 'select id from openk_semaforo.pedido where pedido_oking_id = ?'
    elif connection_type.lower() == 'firebird':
        return 'select id from semaforo_pedido where pedido_oking_id = ?'


def get_insert_order_items_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''insert into openk_semaforo.itens_pedido 
                       (pedido_id, sku, codigo_erp, quantidade, ean, valor, valor_desconto, valor_frete, valor_substituicao_tributaria, iva, icms_intraestadual, icms_interestadual, valor_icms_interestadual, percentual_ipi, valor_ipi) 
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '''
    elif connection_type.lower() == 'oracle':
        return '''INSERT INTO OPENK_SEMAFORO.ITENS_PEDIDO 
                       (PEDIDO_ID, SKU, CODIGO_ERP, QUANTIDADE, EAN, VALOR, VALOR_DESCONTO, VALOR_FRETE, VALOR_SUBSTITUICAO_TRIBUTARIA, IVA, ICSM_INTRAESTADUAL, ICMS_INTERESTADUAL, VALOR_ICMS_INTERESTADUAL, PERCENTUAL_IPI, VALOR_IPI)
                VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15)'''
    elif connection_type.lower() == 'sql':
        return '''insert into openk_semaforo.itens_pedido 
                       (pedido_id, sku, codigo_erp, quantidade, ean, valor, valor_desconto, valor_frete, valor_substituicao_tributaria, iva, icms_intraestadual, icms_interestadual, valor_icms_interestadual, percentual_ipi, valor_ipi) 
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''
    elif connection_type.lower() == 'firebird':
        return '''insert into semaforo_itens_pedido 
                               (pedido_id, sku, codigo_erp, quantidade, ean, valor, valor_desconto, valor_frete, valor_substituicao_tributaria, iva, icms_intraestadual, icms_interestadual, valor_icms_interestadual, percentual_ipi, valor_ipi) 
                        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''


def get_query_non_integrated_order(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'select id from openk_semaforo.pedido where pedido_oking_id = %s and data_sincronizacao is null'
    elif connection_type.lower() == 'oracle':
        return 'SELECT ID FROM OPENK_SEMAFORO.PEDIDO WHERE PEDIDO_OKING_ID = :1 AND DATA_SINCRONIZACAO IS NULL'
    elif connection_type.lower() == 'sql':
        return 'select id from openk_semaforo.pedido where pedido_oking_id = ? and data_sincronizacao is null'
    elif connection_type.lower() == 'firebird':
        return 'select id from semaforo_pedido where pedido_oking_id = ? and data_sincronizacao is null'


def get_insert_b2b_order_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''insert into openk_semaforo.pedido 
                 (pedido_oking_id, pedido_venda_id, pedido_canal, numero_pedido_externo, data_pedido, status, cliente_id
                  , valor, valor_desconto, valor_frete, valor_adicional_forma_pagt, data_pagamento, tipo_pagamento
                  , bandeira, parcelas, condicao_pagamento_erp, opcao_pagamento_erp, codigo_rastreio
                  , data_previsao_entrega, transportadora, opcao_forma_entrega, modo_envio, canal_id, loja_id
                  , codigo_representante
                  , cnpj_intermediador, identificador_vendedor, end_entrega_cep, end_entrega_tipo_logradouro
                  , end_entrega_logradouro, end_entrega_numero, end_entrega_complemento, end_entrega_bairro
                  , end_entrega_cidade, end_entrega_estado, end_entrega_referencia_ent, end_entrega_codigo_ibge
                  , descritor_pre_definido_2, descritor_pre_definido_3, descritor_pre_definido_4
                  , descritor_pre_definido_5
                  , descritor_pre_definido_6)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                  , %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  '''
    elif connection_type.lower() == 'oracle':
        return '''INSERT INTO OPENK_SEMAFORO.PEDIDO 
                (pedido_oking_id, pedido_venda_id, pedido_canal, numero_pedido_externo, data_pedido, status, cliente_id
                  , valor, valor_desconto, valor_frete, valor_adicional_forma_pagt, data_pagamento, tipo_pagamento
                  , bandeira, parcelas, condicao_pagamento_erp, opcao_pagamento_erp, codigo_rastreio
                  , data_previsao_entrega, transportadora, opcao_forma_entrega, modo_envio, canal_id, loja_id
                  , codigo_representante
                  , cnpj_intermediador, identificador_vendedor, end_entrega_cep, end_entrega_tipo_logradouro
                  , end_entrega_logradouro, end_entrega_numero, end_entrega_complemento, end_entrega_bairro
                  , end_entrega_cidade, end_entrega_estado, end_entrega_referencia_ent, end_entrega_codigo_ibge
                  , descritor_pre_definido_2, descritor_pre_definido_3, descritor_pre_definido_4
                  , descritor_pre_definido_5
                  , descritor_pre_definido_6)
            VALUES (:1, :2, :3, :4, TO_DATE(:5, 'YYYY-MM-DD HH24:MI:SS'), :6, :7 , :8, :9, :10, :11
                    , TO_DATE(:12, 'YYYY-MM-DD HH24:MI:SS'), :13 , :14, :15, :16, :17, :18 
                    , TO_DATE(:19, 'YYYY-MM-DD HH24:MI:SS'), :20, :21, :22, :23, :24 , :25, :26, :27, :28
                    , :29, :30, :31, :32 , :33, :34, :35, :36, :37, :38, :39, :40, :41, SUBSTR( :42 , 0, 100)) '''
    elif connection_type.lower() == 'sql':
        return '''insert into openk_semaforo.pedido 
                    (pedido_oking_id, pedido_venda_id, pedido_canal, numero_pedido_externo, data_pedido, status
                  , cliente_id, valor, valor_desconto, valor_frete, valor_adicional_forma_pagt, data_pagamento
                  , tipo_pagamento, bandeira, parcelas, condicao_pagamento_erp, opcao_pagamento_erp, codigo_rastreio
                  , data_previsao_entrega, transportadora, opcao_forma_entrega, modo_envio, canal_id, loja_id
                  , codigo_representante
                  , cnpj_intermediador, identificador_vendedor, end_entrega_cep, end_entrega_tipo_logradouro
                  , end_entrega_logradouro, end_entrega_numero, end_entrega_complemento, end_entrega_bairro
                  , end_entrega_cidade, end_entrega_estado, end_entrega_referencia_ent, end_entrega_codigo_ibge
                  , descritor_pre_definido_2, descritor_pre_definido_3, descritor_pre_definido_4
                  , descritor_pre_definido_5
                  , descritor_pre_definido_6)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                  , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''
    elif connection_type.lower() == 'firebird':
        return '''insert into semaforo_pedido 
                            (pedido_oking_id, pedido_venda_id, pedido_canal, numero_pedido_externo, data_pedido
                          , status, cliente_id, valor, valor_desconto, valor_frete, valor_adicional_forma_pagt
                          , data_pagamento, tipo_pagamento, bandeira, parcelas, condicao_pagamento_erp
                          , opcao_pagamento_erp, codigo_rastreio, data_previsao_entrega, transportadora
                          , opcao_forma_entrega, modo_envio
                          , canal_id, loja_id, codigo_representante, cnpj_intermediador, identificador_vendedor
                          , end_entrega_cep, end_entrega_tipo_logradouro, end_entrega_logradouro, end_entrega_numero
                          , end_entrega_complemento, end_entrega_bairro, end_entrega_cidade, end_entrega_estado
                          , end_entrega_referencia_ent, end_entrega_codigo_ibge
                          , descritor_pre_definido_2, descritor_pre_definido_3, descritor_pre_definido_4
                          , descritor_pre_definido_5
                          , descritor_pre_definido_6)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                  , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''


def get_insert_okvendas_order_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''insert into openk_semaforo.pedido 
                 (pedido_oking_id, pedido_venda_id, pedido_canal, numero_pedido_externo, data_pedido, status, cliente_id
                  , valor, valor_desconto, valor_frete, valor_adicional_forma_pagt, data_pagamento, tipo_pagamento
                  , bandeira, parcelas, condicao_pagamento_erp, opcao_pagamento_erp, codigo_rastreio
                  , data_previsao_entrega, transportadora, opcao_forma_entrega, modo_envio, canal_id, loja_id
                  , codigo_representante
                  , cnpj_intermediador, identificador_vendedor, end_entrega_cep, end_entrega_tipo_logradouro
                  , end_entrega_logradouro, end_entrega_numero, end_entrega_complemento, end_entrega_bairro
                  , end_entrega_cidade, end_entrega_estado, end_entrega_referencia_ent, end_entrega_codigo_ibge
                  , descritor_pre_definido_2, descritor_pre_definido_3, descritor_pre_definido_4
                  , descritor_pre_definido_5
                  , descritor_pre_definido_6, modalidade_venda, valor_taxa_servico)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                  , %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  '''
    elif connection_type.lower() == 'oracle':
        return '''INSERT INTO OPENK_SEMAFORO.PEDIDO 
                (pedido_oking_id, pedido_venda_id, pedido_canal, numero_pedido_externo, data_pedido, status, cliente_id
                  , valor, valor_desconto, valor_frete, valor_adicional_forma_pagt, data_pagamento, tipo_pagamento
                  , bandeira, parcelas, condicao_pagamento_erp, opcao_pagamento_erp, codigo_rastreio
                  , data_previsao_entrega, transportadora, opcao_forma_entrega, modo_envio, canal_id, loja_id
                  , codigo_representante
                  , cnpj_intermediador, identificador_vendedor, end_entrega_cep, end_entrega_tipo_logradouro
                  , end_entrega_logradouro, end_entrega_numero, end_entrega_complemento, end_entrega_bairro
                  , end_entrega_cidade, end_entrega_estado, end_entrega_referencia_ent, end_entrega_codigo_ibge
                  , descritor_pre_definido_2, descritor_pre_definido_3, descritor_pre_definido_4
                  , descritor_pre_definido_5
                  , descritor_pre_definido_6, modalidade_venda, valor_taxa_servico)
            VALUES (:1, :2, :3, :4, TO_DATE(:5, 'YYYY-MM-DD HH24:MI:SS'), :6, :7 , :8, :9, :10, :11
                    , TO_DATE(:12, 'YYYY-MM-DD HH24:MI:SS'), :13 , :14, :15, :16, :17, :18 
                    , TO_DATE(:19, 'YYYY-MM-DD HH24:MI:SS'), :20, :21, :22, :23, :24 , :25, :26, :27, :28
                    , :29, :30, :31, :32 , :33, :34, :35, :36, :37, :38, :39, :40, :41, SUBSTR( :42 , 0, 100)
                    , :43, :44) '''
    elif connection_type.lower() == 'sql':
        return '''insert into openk_semaforo.pedido 
                    (pedido_oking_id, pedido_venda_id, pedido_canal, numero_pedido_externo, data_pedido, status
                  , cliente_id, valor, valor_desconto, valor_frete, valor_adicional_forma_pagt, data_pagamento
                  , tipo_pagamento, bandeira, parcelas, condicao_pagamento_erp, opcao_pagamento_erp, codigo_rastreio
                  , data_previsao_entrega, transportadora, opcao_forma_entrega, modo_envio, canal_id, loja_id
                  , codigo_representante
                  , cnpj_intermediador, identificador_vendedor, end_entrega_cep, end_entrega_tipo_logradouro
                  , end_entrega_logradouro, end_entrega_numero, end_entrega_complemento, end_entrega_bairro
                  , end_entrega_cidade, end_entrega_estado, end_entrega_referencia_ent, end_entrega_codigo_ibge
                  , descritor_pre_definido_2, descritor_pre_definido_3, descritor_pre_definido_4
                  , descritor_pre_definido_5
                  , descritor_pre_definido_6, modalidade_venda, valor_taxa_servico)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                  , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''
    elif connection_type.lower() == 'firebird':
        return '''insert into semaforo_pedido 
                            (pedido_oking_id, pedido_venda_id, pedido_canal, numero_pedido_externo, data_pedido
                          , status, cliente_id, valor, valor_desconto, valor_frete, valor_adicional_forma_pagt
                          , data_pagamento, tipo_pagamento, bandeira, parcelas, condicao_pagamento_erp
                          , opcao_pagamento_erp, codigo_rastreio, data_previsao_entrega, transportadora
                          , opcao_forma_entrega, modo_envio
                          , canal_id, loja_id, codigo_representante, cnpj_intermediador, identificador_vendedor
                          , end_entrega_cep, end_entrega_tipo_logradouro, end_entrega_logradouro, end_entrega_numero
                          , end_entrega_complemento, end_entrega_bairro, end_entrega_cidade, end_entrega_estado
                          , end_entrega_referencia_ent, end_entrega_codigo_ibge
                          , descritor_pre_definido_2, descritor_pre_definido_3, descritor_pre_definido_4
                          , descritor_pre_definido_5
                          , descritor_pre_definido_6, modalidade_venda, valor_taxa_servico)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                  , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''


def get_insert_b2b_order_items_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''insert into openk_semaforo.itens_pedido 
                    (pedido_id, sku, codigo_erp, quantidade, ean, valor, valor_desconto, valor_frete, filial_expedicao
                    , filial_faturamento, cnpj_filial_venda, valor_taxa_servico) 
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '''
    elif connection_type.lower() == 'oracle':
        return '''INSERT INTO OPENK_SEMAFORO.ITENS_PEDIDO 
                    (pedido_id, sku, codigo_erp, quantidade, ean, valor, valor_desconto, valor_frete, filial_expedicao
                    , filial_faturamento, cnpj_filial_venda, valor_taxa_servico) 
                VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12)'''
    elif connection_type.lower() == 'sql':
        return '''insert into openk_semaforo.itens_pedido 
                    (pedido_id, sku, codigo_erp, quantidade, ean, valor, valor_desconto, valor_frete, filial_expedicao
                    , filial_faturamento, cnpj_filial_venda, valor_taxa_servico) 
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''
    elif connection_type.lower() == 'firebird':
        return '''insert into semaforo_itens_pedido 
                            (pedido_id, sku, codigo_erp, quantidade, ean, valor, valor_desconto, valor_frete
                            , filial_expedicao
                            , filial_faturamento, cnpj_filial_venda, valor_taxa_servico) 
                        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''


def get_client_protocol_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''update openk_semaforo.cliente 
                set codigo_referencia_erp = %s 
              where id = (select cliente_id from openk_semaforo.pedido where pedido_oking_id = %s)'''
    elif connection_type.lower() == 'oracle':
        return '''UPDATE OPENK_SEMAFORO.CLIENTE C
                     SET CODIGO_REFERENCIA_ERP = :1 
                  WHERE ID = (SELECT CLIENTE_ID FROM OPENK_SEMAFORO.PEDIDO WHERE PEDIDO_OKING_ID = :2)'''
    elif connection_type.lower() == 'sql':
        return '''update openk_semaforo.cliente 
                    set CODIGO_REFERENCIA_ERP = ? 
                  where id = (select cliente_id from openk_semaforo.pedido where pedido_oking_id = ?)'''
    elif connection_type.lower() == 'firebird':
        return '''update semaforo_cliente 
                            set CODIGO_REFERENCIA_ERP = ? 
                          where id = (select FIRST 1 cliente_id from semaforo_pedido where pedido_oking_id = ?)'''


def get_order_protocol_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''update openk_semaforo.pedido 
                     set data_sincronizacao    = now()
                       , numero_pedido_externo = %s
                   where pedido_oking_id = %s'''
    elif connection_type.lower() == 'oracle':
        return '''UPDATE OPENK_SEMAFORO.PEDIDO 
                     SET DATA_SINCRONIZACAO    = SYSDATE
                       , NUMERO_PEDIDO_EXTERNO = :1 
                   WHERE PEDIDO_OKING_ID = :2'''
    elif connection_type.lower() == 'sql':
        return '''update openk_semaforo.pedido 
                     set data_sincronizacao    = getdate()
                       , NUMERO_PEDIDO_EXTERNO = ?
                   where pedido_oking_id = ?'''
    elif connection_type.lower() == 'firebird':
        return '''update semaforo_pedido 
                     set data_sincronizacao    = CURRENT_TIMESTAMP
                       , NUMERO_PEDIDO_EXTERNO = ?
                   where pedido_oking_id = ?'''


def update_encaminha_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''update openk_semaforo.pedido 
                    set status                      = 'ENCAMINHADO_ENTREGA'
                      , data_sincronizacao_rastreio = now() 
                  where pedido_oking_id = %s'''
    elif connection_type.lower() == 'oracle':
        return '''UPDATE OPENK_SEMAFORO.PEDIDO 
                     SET STATUS                      = 'ENCAMINHADO_ENTREGA'
                       , DATA_SINCRONIZACAO_RASTREIO = SYSDATE 
                   WHERE PEDIDO_OKING_ID = :1 '''
    elif connection_type.lower() == 'sql':
        return '''update openk_semaforo.pedido
                     set status                      = 'ENCAMINHADO_ENTREGA'
                       , data_sincronizacao_rastreio = getdate()
                   where pedido_oking_id = ?'''
    elif connection_type.lower() == 'firebird':
        return '''update semaforo_pedido
                     set status                      = 'ENCAMINHADO_ENTREGA'
                       , data_sincronizacao_rastreio = CURRENT_TIMESTAMP
                   where pedido_oking_id = ?'''


def update_entrega_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''update openk_semaforo.pedido 
                    set status                     = 'ENTREGUE'
                      , data_sincronizacao_entrega = now() 
                  where pedido_oking_id = %s'''
    elif connection_type.lower() == 'oracle':
        return '''UPDATE OPENK_SEMAFORO.PEDIDO 
                     SET STATUS                     = 'ENTREGUE'
                       , data_sincronizacao_entrega = SYSDATE 
                   WHERE PEDIDO_OKING_ID = :1'''
    elif connection_type.lower() == 'sql':
        return '''update openk_semaforo.pedido 
                     set status                     = 'ENTREGUE'
                       , data_sincronizacao_entrega = getdate() 
                   where pedido_oking_id = ?'''
    elif connection_type.lower() == 'firebird':
        return '''update semaforo_pedido 
                     set status                     = 'ENTREGUE'
                       , data_sincronizacao_entrega = CURRENT_TIMESTAMP
                   where pedido_oking_id = ?'''


def get_update_data_sincronizacao_nf_command(connection_type: str, versao):
    if connection_type.lower() == 'mysql':
        return f'''update openk_semaforo.pedido 
                     set data_sincronizacao_nf = now() 
                   WHERE {versao} = %s'''
    elif connection_type.lower() == 'oracle':
        return f'''update openk_semaforo.pedido 
                     set data_sincronizacao_nf = sysdate 
                   WHERE {versao} = :1'''
    elif connection_type.lower() == 'sql':
        return f'''update openk_semaforo.pedido 
                     set data_sincronizacao_nf = getdate() 
                   WHERE {versao} = ?'''
    elif connection_type.lower() == 'firebird':
        return f'''update semaforo_pedido
                     set data_sincronizacao_nf = CURRENT_TIMESTAMP
                   WHERE {versao} = ?'''


def update_foto_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''update openk_semaforo.produto 
                     set data_envio_foto = now() 
                  where codigo_erp_sku = %s'''
    elif connection_type.lower() == 'oracle':
        return '''UPDATE OPENK_SEMAFORO.PRODUTO 
                     SET data_envio_foto = SYSDATE 
                   WHERE CODIGO_ERP_SKU = :1'''
    elif connection_type.lower() == 'sql':
        return '''update openk_semaforo.produto
                     set data_envio_foto = getdate()
                   where codigo_erp_sku = ?'''
    elif connection_type.lower() == 'firebird':
        return '''update semaforo_produto
                     set data_envio_foto = CURRENT_TIMESTAMP
                   where codigo_erp_sku = ?'''


def get_log_integracao(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''select log_integracao from openk_semaforo.pedido
        where pedido_oking_id = %s;'''
    elif connection_type.lower() == 'oracle':
        return '''SELECT LOG_INTEGRACAO from openk_semaforo.PEDIDO
        WHERE PEDIDO_OKING_ID = :pedido_oking_id'''
    elif connection_type.lower() == 'sql':
        return '''select log_integracao from openk_semaforo.pedido
        where pedido_oking_id = ?;'''
    elif connection_type.lower() == 'firebird':
        return '''select log_integracao from semaforo_pedido
                where pedido_oking_id = ?;'''


def get_log_integracao2(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''select log_integracao from openk_semaforo.pedido
        where pedido_oking_id = %s;'''
    elif connection_type.lower() == 'oracle':
        return '''SELECT LOG_INTEGRACAO from openk_semaforo.PEDIDO
        WHERE PEDIDO_OKING_ID = :1'''
    elif connection_type.lower() == 'sql':
        return '''select log_integracao from openk_semaforo.pedido
        where pedido_oking_id = ?;'''
    elif connection_type.lower() == 'firebird':
        return '''select log_integracao from semaforo_pedido
        where pedido_oking_id = ?;'''


def update_status_observacao(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''update openk_semaforo.pedido set status_observacao = %s
        where pedido_oking_id = %s;'''
    elif connection_type.lower() == 'oracle':
        return '''UPDATE OPENK_SEMAFORO.PEDIDO SET STATUS_OBSERVACAO = :1
        WHERE PEDIDO_OKING_ID = :2'''
    elif connection_type.lower() == 'sql':
        return '''update openk_semaforo.pedido set status_observacao = ?
        where pedido_oking_id = ?;'''
    elif connection_type.lower() == 'firebird':
        return '''update openk_semaforo.pedido set status_observacao = ?
        where pedido_oking_id = ?;'''
    
    
def update_status_pedido(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''update openk_semaforo.pedido set status = %s
        where pedido_oking_id = %s;'''
    elif connection_type.lower() == 'oracle':
        return '''UPDATE OPENK_SEMAFORO.PEDIDO SET STATUS = :1
        WHERE PEDIDO_OKING_ID = :2'''
    elif connection_type.lower() == 'sql':
        return '''update openk_semaforo.pedido set status = ?
        where pedido_oking_id = ?;'''
    elif connection_type.lower() == 'firebird':
        return '''update openk_semaforo.pedido set status = ?
        where pedido_oking_id = ?;'''    

# def update_produto_command(connection_type: str):
#     if connection_type.lower() == 'mysql':
#         return "update openk_semaforo.produto set data_sincronizacao = now() where codigo_erp_sku = %s"
#     elif connection_type.lower() == 'oracle':
#         return "UPDATE OPENK_SEMAFORO.PRODUTO SET data_sincronizacao = SYSDATE WHERE CODIGO_ERP_SKU = :1"
#     elif connection_type.lower() == 'sql':
#         return "update openk_semaforo.produto set data_sincronizacao = getdate() where codigo_erp_sku = ?"
#
# def get_insert_produto_command(connection_type: str):
#     if connection_type.lower() == 'mysql':
#         return '''insert into openk_semaforo.produto (codigo_erp, codigo_erp_sku, data_atualizacao
#         , data_sincronizacao, data_envio_foto)
# 					values (%s, %s, %s, %s, %s) '''
#     elif connection_type.lower() == 'oracle':
#         return '''INSERT INTO OPENK_SEMAFORO.produto (PEDIDO_ID, SKU, CODIGO_ERP, QUANTIDADE, EAN
#         , VALOR, VALOR_DESCONTO, VALOR_FRETE, CNPJ_FILIAL_VENDA, CODIGO_FILIAL_ERP, CODIGO_FILIAL_EXPEDICAO_ERP
#         , CODIGO_FILIAL_FATURAMENT_ERP)
# 					VALUES (:1, :2, :3, :4, :5)'''
#     elif connection_type.lower() == 'sql':
#         return '''insert into openk_semaforo.produto (codigo_erp, codigo_erp_sku, data_atualizacao
#         , data_sincronizacao, data_envio_foto)
# 					values (?, ?, ?, ?, ?) '''


def get_product_protocol_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''update openk_semaforo.produto 
                     set data_sincronizacao = now(), 
                         data_envio_foto = now 
                   where codigo_erp = %s 
                     and codigo_erp_sku = %s'''
    elif connection_type.lower() == 'oracle':
        return '''update openk_semaforo.produto 
                     set data_sincronizacao = SYSDATE, 
                         data_envio_foto = SYSDATE 
                   where codigo_erp = :codigo_erp 
                     and codigo_erp_sku = :codigo_erp_sku'''
    elif connection_type.lower() == 'sql':
        return '''update openk_semaforo.produto 
                     set data_sincronizacao = getdate(), 
                         data_envio_foto = getdate() 
                   where codigo_erp = ? 
                     and codigo_erp_sku = ?'''
    elif connection_type.lower() == 'firebird':
        return '''update semaforo_produto 
                     set data_sincronizacao = CURRENT_TIMESTAMP, 
                         data_envio_foto = CURRENT_TIMESTAMP 
                   where codigo_erp = ? 
                     and codigo_erp_sku = ?'''


def get_protocol_semaphore_id3_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''update openk_semaforo.semaforo 
                     set data_sincronizacao = now() 
                   where identificador = %s 
                     and tipo_id = %s'''
    elif connection_type.lower() == 'oracle':
        return '''update openk_semaforo.semaforo 
                     set data_sincronizacao = sysdate 
                   where identificador = :1 
                     and tipo_id = :2'''
    elif connection_type.lower() == 'sql':
        return '''update openk_semaforo.semaforo 
                     set data_sincronizacao = getdate() 
                   where identificador = ? 
                     and tipo_id = ?'''
    elif connection_type.lower() == 'firebird':
        return '''update semaforo 
                     set data_sincronizacao = CURRENT_TIMESTAMP 
                   where identificador = ? 
                     and tipo_id = ?'''


def get_insert_in_clients(connection_type: str):
    if connection_type.lower() == 'mysql':
        return '''
            insert into cliente 
                (nome, razao_social, cpf, cnpj, email, telefone_residencial, telefone_celular, cep, tipo_logradouro
                , logradouro, numero, complemento, bairro, cidade, estado, referencia, cliente_erp, direcao
                , data_sincronizacao, data_alteracao, codigo_ibge, inscricaoestadual, origem_cadastro
                , codigo_representante)
            value (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, null, %s, %s, null, %s, %s, %s, %s)
            on duplicate key update
            data_alteracao = values(data_alteracao),
            data_sincronizacao = null
            '''
    elif connection_type.lower() == 'oracle':
        return '''
            MERGE INTO OPENK_SEMAFORO.CLIENTE c
            USING (
                SELECT
                    :1 AS CPF,
                    :2 AS CNPJ,
                    :3 AS DATA_ALTERACAO
                 FROM DUAL
            ) tmp ON (tmp.CPF = c.CPF OR tmp.CNPJ = c.CNPJ)

            WHEN MATCHED THEN
              UPDATE 
                 SET c.DATA_ALTERACAO = tmp.DATA_ALTERACAO,
                     c.DATA_SINCRONIZACAO = NULL

            WHEN NOT MATCHED THEN
            INSERT (NOME, RAZAO_SOCIAL, CPF, CNPJ, EMAIL, TELEFONE_RESIDENCIAL, TELEFONE_CELULAR, CEP, TIPO_LOGRADOURO
                  , LOGRADOURO, NUMERO, COMPLEMENTO, BAIRRO, CIDADE, ESTADO, REFERENCIA, CLIENTE_ERP, DIRECAO
                  , DATA_ALTERACAO, DATA_SINCRONIZACAO, CODIGO_IBGE, INSCRICAO_ESTADUAL, ORIGEM_CADASTRO
                  , CODIGO_REPRESENTANTE)
            VALUES (:4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, NULL, :20, :21, NULL
                , :22, :23, :24, :25)
         '''
    elif connection_type.lower() == 'sql':
        return '''
			MERGE INTO OPENK_SEMAFORO.CLIENTE c
			USING (
				SELECT
					? AS NOME,
					? AS RAZAO_SOCIAL,
					? AS CPF,
					? AS CNPJ,
					? AS EMAIL,
					? AS TELEFONE_RESIDENCIAL,
					? AS TELEFONE_CELULAR,
					? AS CEP,
					? AS TIPO_LOGRADOURO,
					? AS LOGRADOURO,
					? AS NUMERO,
					? AS COMPLEMENTO,
					? AS BAIRRO,
					? AS CIDADE,
					? AS ESTADO,
					? AS REFERENCIA,
					? AS DIRECAO,
					? AS DATA_ALTERACAO,
					? AS CODIGO_IBGE,
					? AS INSCRICAO_ESTADUAL,
					? AS CLIENTE_ERP,
					? AS ORIGEM_CADASTRO,
					? AS CODIGO_REPRESENTANTE
				FROM DUAL
			) tmp ON (tmp.CPF = c.CPF OR tmp.CNPJ = c.CNPJ)

			WHEN MATCHED THEN
				UPDATE SET
					c.DATA_ALTERACAO = tmp.DATA_ALTERACAO,
					c.DATA_SINCRONIZACAO = NULL

			WHEN NOT MATCHED THEN
			INSERT (NOME, RAZAO_SOCIAL, CPF, CNPJ, EMAIL, TELEFONE_RESIDENCIAL, TELEFONE_CELULAR, CEP, TIPO_LOGRADOURO
			       , LOGRADOURO, NUMERO, COMPLEMENTO, BAIRRO, CIDADE, ESTADO,
					REFERENCIA, CLIENTE_ERP, DIRECAO, DATA_ALTERACAO, DATA_SINCRONIZACAO, CODIGO_IBGE
					, INSCRICAO_ESTADUAL, ORIGEM_CADASTRO, CODIGO_REPRESENTANTE)
			VALUES (tmp.NOME, tmp.RAZAO_SOCIAL, tmp.CPF, tmp.CNPJ, tmp.EMAIL, tmp.TELEFONE_RESIDENCIAL
			      , tmp.TELEFONE_CELULAR, tmp.CEP, tmp.TIPO_LOGRADOURO, tmp.LOGRADOURO, tmp.NUMERO, tmp.COMPLEMENTO,
					tmp.BAIRRO, tmp.CIDADE, tmp.ESTADO, tmp.REFERENCIA, NULL, tmp.DIRECAO, tmp.DATA_ALTERACAO, NULL
				  , tmp.CODIGO_IBGE, tmp.INSCRICAO_ESTADUAL, tmp.ORIGEM_CADASTRO, tmp.CODIGO_REPRESENTANTE)
		'''
    elif connection_type.lower() == 'firebird':
        return '''
            insert into semaforo_cliente (nome, razao_social, cpf, cnpj, email, telefone_residencial, telefone_celular,
                                cep, tipo_logradouro, logradouro, numero, complemento, bairro, cidade
                                , estado, referencia, cliente_erp, direcao, data_sincronizacao, data_alteracao
                                , codigo_ibge, inscricaoestadual, origem_cadastro,codigo_representante)
            value (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, null, %s, %s, null, %s, %s, %s, %s)
            on duplicate key update
                data_alteracao = values(data_alteracao),
                data_sincronizacao = null
        '''


def get_update_in_clients(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'update openk_semaforo.cliente set data_alteracao = %s, data_sincronizacao = null where id = %s'
    elif connection_type.lower() == 'oracle':
        return 'UPDATE OPENK_SEMAFORO.CLIENTE SET DATA_ALTERACAO = :1, DATA_SINCRONIZACAO = NULL WHERE id = :2'
    elif connection_type.lower() == 'sql':
        return 'UPDATE OPENK_SEMAFORO.CLIENTE SET DATA_ALTERACAO = ?, DATA_SINCRONIZACAO = NULL WHERE id = ?'
    elif connection_type.lower() == 'firebird':
        return 'update semaforo_cliente set data_alteracao = %s, data_sincronizacao = null where id = %s'


def get_query_client_cpf(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'select id from openk_semaforo.cliente where cpf = %s'
    elif connection_type.lower() == 'oracle':
        return 'SELECT ID FROM OPENK_SEMAFORO.CLIENTE WHERE CPF = :1 '
    elif connection_type.lower() == 'sql':
        return 'select id from openk_semaforo.cliente where cpf = ?'
    elif connection_type.lower() == 'firebird':
        return 'select id from semaforo_cliente where cpf = %s'


def get_query_client_cnpj(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'select id from openk_semaforo.cliente where cnpj = %s'
    elif connection_type.lower() == 'oracle':
        return 'SELECT ID FROM OPENK_SEMAFORO.CLIENTE WHERE CNPJ = :1 '
    elif connection_type.lower() == 'sql':
        return 'select id from openk_semaforo.cliente where cnpj = ?'
    elif connection_type.lower() == 'firebird':
        return 'select id from semaforo_cliente where cnpj = %s'


def get_out_client_protocol_command(connection_type: str):
    if connection_type.lower() == 'mysql':
        return 'update openk_semaforo.cliente set data_sincronizacao = now() where cliente_erp = %s'
    elif connection_type.lower() == 'oracle':
        return 'UPDATE OPENK_SEMAFORO.CLIENTE C SET DATA_SINCRONIZACAO = SYSDATE WHERE CLIENTE_ERP = :1 '
    elif connection_type.lower() == 'sql':
        return 'update openk_semaforo.cliente set data_sincronizacao = getdate() where cliente_erp = ? '
    elif connection_type.lower() == 'firebird':
        return 'update semaforo_cliente set data_sincronizacao = CURRENT_TIMESTAMP where cliente_erp = %s'


def get_order_item_firebird():
    return 'select pedido_id from semaforo_itens_pedido where pedido_id = ? and sku = ? and codigo_erp = ?'
