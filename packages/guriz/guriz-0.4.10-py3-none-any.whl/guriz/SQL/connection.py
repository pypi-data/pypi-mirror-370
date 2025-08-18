import pymysql
from pymysql.cursors import DictCursor
from pymysql.err import Error as PyMySQLError
import logging
from dbutils.pooled_db import PooledDB
from .config import Config
from contextlib import contextmanager

logger = logging.getLogger(__name__)
class MySQLConfig:
    MYSQL_HOST = Config.MYSQL_HOST
    MYSQL_PORT = Config.MYSQL_PORT
    MYSQL_USER = Config.MYSQL_USER
    MYSQL_PASSWORD = Config.MYSQL_PASSWORD
    MYSQL_DB = Config.MYSQL_DB

    MAX_POOL_SIZE = int(100)
    MIN_POOL_SIZE = int(10)

    CONNECT_TIMEOUT = int(120)

    USE_SSL = False
    CHARSET = 'utf8mb4'
    AUTOCOMMIT = False

    TIMEZONE = '-03:00'


class MySQL:
    _pool = None

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            try:
                ssl_config = None
                if MySQLConfig.USE_SSL:
                    ssl_config = {'ca': None} 

                init_command = f"SET time_zone = '{MySQLConfig.TIMEZONE}';"

                cls._pool = PooledDB(
                    creator=pymysql,
                    maxconnections=MySQLConfig.MAX_POOL_SIZE,
                    mincached=MySQLConfig.MIN_POOL_SIZE,
                    maxcached=MySQLConfig.MAX_POOL_SIZE,
                    maxshared=MySQLConfig.MAX_POOL_SIZE,
                    blocking=True,
                    maxusage=None,
                    setsession=None,
                    ping=1,  # Reconecta automaticamente se a conexão cair
                    host=MySQLConfig.MYSQL_HOST,
                    port=MySQLConfig.MYSQL_PORT,
                    user=MySQLConfig.MYSQL_USER,
                    password=MySQLConfig.MYSQL_PASSWORD,
                    database=MySQLConfig.MYSQL_DB,
                    charset=MySQLConfig.CHARSET,
                    connect_timeout=MySQLConfig.CONNECT_TIMEOUT,
                    read_timeout=30,
                    write_timeout=30,
                    autocommit=MySQLConfig.AUTOCOMMIT,
                    cursorclass=DictCursor,
                    ssl=ssl_config
                )
                logger.info("Pool de conexão MySQL criado com sucesso")
            except PyMySQLError as e:
                logger.error(f"Erro ao criar pool de conexão MySQL: {e}")
                raise
        return cls._pool

    @classmethod
    def get_connection(cls):
        """
        Obtém uma conexão do pool. A conexão deve ser fechada após o uso.
        """
        try:
            pool = cls.get_pool()
            connection = pool.connection()
            # Testa a conexão
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            logger.debug("Conexão obtida do pool MySQL")
            return connection
        except PyMySQLError as e:
            logger.error(f"Erro ao obter conexão do pool MySQL: {e}")
            raise

    @classmethod
    def execute_query(cls, query, params=None, with_commit=True, fetch_type='all'):
        """
        Executa uma query SQL com parâmetros usando uma conexão do pool

        Args:
            query (str): Query SQL a ser executada
            params (tuple, dict, None): Parâmetros para a query
            with_commit (bool): Se deve executar commit após a query
            fetch_type (str): Tipo de fetch ('all', 'one', 'many', None)

        Returns:
            result: Resultado da query baseado no fetch_type
        """
        connection = None
        cursor = None
        try:
            connection = cls.get_connection()
            cursor = connection.cursor()

            cursor.execute(query, params)

            # Busca os resultados baseado no tipo solicitado
            result = None
            if fetch_type == 'all':
                result = cursor.fetchall()
            elif fetch_type == 'one':
                result = cursor.fetchone()
            elif fetch_type == 'many':
                result = cursor.fetchmany()

            if with_commit:
                connection.commit()

            logger.debug(f"Query executada com sucesso: {query[:100]}...")
            return result

        except PyMySQLError as e:
            if connection:
                connection.rollback()
            logger.error(f"Erro ao executar query: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()  # Retorna a conexão para o pool

    @classmethod
    def execute_transaction(cls, queries_with_params):
        """
        Executa múltiplas queries em uma única transação

        Args:
            queries_with_params (list): Lista de tuplas (query, params)

        Returns:
            list: Lista com os resultados de cada query
        """
        connection = None
        cursor = None
        results = []

        try:
            connection = cls.get_connection()
            cursor = connection.cursor()

            # Inicia transação explicitamente
            connection.begin()

            for query, params in queries_with_params:
                cursor.execute(query, params)
                # Para SELECT queries, adiciona o resultado
                if query.strip().upper().startswith('SELECT'):
                    results.append(cursor.fetchall())
                else:
                    results.append(cursor.rowcount)

            connection.commit()
            logger.debug(f"Transação executada com sucesso - {len(queries_with_params)} queries")
            return results

        except PyMySQLError as e:
            if connection:
                connection.rollback()
            logger.error(f"Erro na transação: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()  # Retorna a conexão para o pool

    @classmethod
    def execute_select(cls, query, params=None, fetch_type='all'):
        """
        Método específico para queries SELECT
        """
        return cls.execute_query(query, params, with_commit=False, fetch_type=fetch_type)

    @classmethod
    def execute_insert(cls, query, params=None):
        """
        Método específico para queries INSERT

        Returns:
            int: ID do último registro inserido
        """
        connection = None
        cursor = None
        try:
            connection = cls.get_connection()
            cursor = connection.cursor()

            cursor.execute(query, params)
            last_id = cursor.lastrowid
            connection.commit()

            logger.debug(f"INSERT executado com sucesso - ID: {last_id}")
            return last_id

        except PyMySQLError as e:
            if connection:
                connection.rollback()
            logger.error(f"Erro no INSERT: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    @classmethod
    def execute_update(cls, query, params=None):
        """
        Método específico para queries UPDATE

        Returns:
            int: Número de linhas afetadas
        """
        connection = None
        cursor = None
        try:
            connection = cls.get_connection()
            cursor = connection.cursor()

            cursor.execute(query, params)
            affected_rows = cursor.rowcount
            connection.commit()

            logger.debug(f"UPDATE executado com sucesso - {affected_rows} linhas afetadas")
            return affected_rows

        except PyMySQLError as e:
            if connection:
                connection.rollback()
            logger.error(f"Erro no UPDATE: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    @classmethod
    def execute_delete(cls, query, params=None):
        """
        Método específico para queries DELETE

        Returns:
            int: Número de linhas deletadas
        """
        connection = None
        cursor = None
        try:
            connection = cls.get_connection()
            cursor = connection.cursor()

            cursor.execute(query, params)
            deleted_rows = cursor.rowcount
            connection.commit()

            logger.debug(f"DELETE executado com sucesso - {deleted_rows} linhas deletadas")
            return deleted_rows

        except PyMySQLError as e:
            if connection:
                connection.rollback()
            logger.error(f"Erro no DELETE: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    @classmethod
    def test_connection(cls):
        """
        Testa se a conexão com o banco está funcionando
        """
        try:
            result = cls.execute_select("SELECT 1 as test", fetch_type='one')
            logger.info("Teste de conexão MySQL: OK")
            return True
        except PyMySQLError as e:
            logger.error(f"Teste de conexão MySQL falhou: {e}")
            return False

    @classmethod
    def close_pool(cls):
        """
        Fecha o pool de conexões (use apenas quando necessário)
        """
        if cls._pool is not None:
            cls._pool.close()
            cls._pool = None
            logger.info("Pool de conexões MySQL fechado")

    @classmethod
    @contextmanager
    def get_cursor(cls):
        conn = cls.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
            conn.close()