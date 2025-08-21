global sql_db_types
sql_db_types = {
    'mysql',
    'oracle',
    'sql'
}


class DatabaseConfig:
    def __init__(self, sql: str, db_type: str, db_name: str, db_host: str, db_user: str, db_pwd: str, db_client: str,
                 query_final: str = 'N', semaforo_sql: str = '', port: str = ''):
        self.db_type = db_type
        self.sql = sql
        self.db_name = db_name
        self.db_host = db_host
        self.db_user = db_user
        self.db_pwd = db_pwd
        self.db_client = db_client
        self.port = port
        self.semaforo_sql = semaforo_sql
        self.query_final = query_final

    def is_sql_server(self):
        return self.db_type.lower().strip() == 'sql'

    def is_mysql(self):
        return self.db_type.lower().strip() == 'mysql'

    def is_oracle(self):
        return self.db_type.lower().strip() == 'oracle'

    def is_firebird(self):
        return self.db_type.lower().strip() == 'firebird'


def get_database_config(job_config: dict):
    return DatabaseConfig(
        job_config.get('sql'),
        job_config.get('db_type'),
        job_config.get('db_name'),
        job_config.get('db_host'),
        job_config.get('db_user'),
        job_config.get('db_pwd'),
        job_config.get('db_client'),
        job_config.get('query_final'),
        job_config.get('semaforo_sql'),
        job_config.get('db_port'))


def get_database_config2(job_config: dict):
    return DatabaseConfig(
        job_config.get('sql'),
        job_config.get('db_type'),
        job_config.get('database'),
        job_config.get('host'),
        job_config.get('user'),
        job_config.get('password'),
        job_config.get('db_client'),
        job_config.get('semaforo_sql'),
        job_config.get('port'))


def get_database_config3(job_config: dict):
    return DatabaseConfig(
        job_config.get('sql'),
        job_config.get('banco'),
        job_config.get('esquema_db'),
        job_config.get('host'),
        job_config.get('usuario_db'),
        job_config.get('senha_db'),
        job_config.get('diretorio_db'),
        job_config.get('semaforo_sql'),
        job_config.get('port')
    )


def final_query(db_config: DatabaseConfig):
    if db_config.semaforo_sql is None or db_config.query_final == 'S':
        return db_config.sql.replace('#v', ',')
    clause = "where"
    if "where" in db_config.sql.lower():
        clause = "and"
    if db_config.sql.lower().__contains__("group by"):
        indice = db_config.sql.lower().index('group by') - 1
        string1 = db_config.sql[:indice].lower() + f" {clause} exists ({db_config.semaforo_sql}) " + \
            db_config.sql[indice:].lower()
        string2 = db_config.sql[:indice].lower() + f" {clause} not exists ({db_config.semaforo_sql}) " + \
            db_config.sql[indice:].lower()
        newsql = f"""{string1.replace("from", ", 1 as existe from")}
                                  union
                                 {string2.replace("from", ", 0 as existe from")}"""
    else:
        newsql = f"""{db_config.sql.lower().replace("from", ", 1 as existe from")} {clause} 
                     exists ({db_config.semaforo_sql})
                  union 
                     {db_config.sql.lower().replace("from", ", 0 as existe from")} {clause} 
                     not exists ({db_config.semaforo_sql.lower().replace("and s.data_alteracao", 
                                                                         " -- and s.data_alteracao")})"""

    newsql = newsql.lower().replace('#v', ',')
    if db_config.db_type.lower() == 'firebird':
        newsql = newsql.replace('openk_semaforo.', "")
    return newsql
