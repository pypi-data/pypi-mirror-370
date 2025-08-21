import json
import ssl
import time
from contextlib import contextmanager

import boto3
import psycopg2
import pymysql
import redis
from pymemcache import PooledClient
from pymysql import OperationalError

from common.secretmanager import SecretManager

context = ssl.create_default_context()


class RDSConnection:
    def __init__(self, db_secret_name, access_key=None, secret_key=None, region_name=None):
        self.__region_name = region_name
        self.__access_key = access_key
        self.__secret_key = secret_key
        self.__db_secret_name = db_secret_name
        self.__aws_secret_manager = SecretManager(region_name=self.__region_name, access_key=self.__access_key,
                                                  secret_key=self.__secret_key)
        self.__database_values = self.__aws_secret_manager.get_secret_key_value(self.__db_secret_name)
        self.__user = self.__database_values.get('username')
        self.__password = self.__database_values.get('password')
        self.__host = self.__database_values.get('host')
        self.__port = int(self.__database_values.get('port')) if self.__database_values.get('port') else 3306
        self.__connect_timeout = 30

    @contextmanager
    def get_connection(self):
        """Always open a new connection, and close after use"""
        conn = pymysql.connect(user=self.__user, password=self.__password, host=self.__host,
                               port=self.__port, connect_timeout=self.__connect_timeout)
        try:
            yield conn
        finally:
            conn.close()

    def conn(self):
        return pymysql.connect(user=self.__user, password=self.__password, host=self.__host, port=self.__port,
                               connect_timeout=self.__connect_timeout)

    @staticmethod
    def cursor(conn):
        """ Return the cursor object """
        return conn.cursor()

    def executemany_query(self, query, values=None, retry_count=3):
        """ Execute the query with multiple values """
        attempt = 0
        while attempt < retry_count:
            try:
                with self.get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.executemany(query, values)
                        conn.commit()
                        return cursor
            except OperationalError as error:
                if error.args[0] in (1213, 1205):  # Deadlock or lock wait timeout
                    attempt += 1
                    wait_time = 2 ** attempt
                    print(f"INFO: Deadlock detected. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise
            except Exception as e:
                print(f"ERROR: {str(e)}")
                raise
        raise Exception(f"ERROR: Failed to execute query after {retry_count} attempts")

    def execute_query(self, query, values=None, retry_count=3):
        """ Execute a single query """
        attempt = 0
        while attempt < retry_count:
            try:
                with self.get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(query, values)
                        conn.commit()
                        return cursor
            except OperationalError as error:
                if error.args[0] in (1213, 1205):  # Deadlock or lock wait timeout
                    attempt += 1
                    wait_time = 2 ** attempt
                    print(f"INFO: Deadlock detected. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise
            except Exception as e:
                print(f"ERROR: {str(e)}")
                raise
        raise Exception(f"ERROR: Failed to execute query after {retry_count} attempts")

    def fetchall(self, query, values=None):
        """ Fetch all rows for a given query """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, values)
                    return cursor.fetchall()
        except Exception as e:
            print(f'ERROR: {str(e)}')
            return []


class RedisConnection:
    def __init__(self, redis_secret_name, access_key=None, secret_key=None, region_name=None):
        self.__region_name = region_name
        self.__access_key = access_key
        self.__secret_key = secret_key
        self.__redis_secret_name = redis_secret_name
        self.__aws_secret_manager = SecretManager(region_name=self.__region_name, access_key=self.__access_key,
                                                  secret_key=self.__secret_key)
        self.__redis_values = self.__aws_secret_manager.get_secret_key_value(self.__redis_secret_name)
        self.__host = self.__redis_values.get('host')
        self.__port = self.__redis_values.get('port')

    def conn(self):
        try:
            red_conn = redis.StrictRedis(host=self.__host, port=self.__port)
            return red_conn
        except redis.ConnectionError as e:
            print(f"Redis Connection Error: {e}")
        except redis.RedisError as e:
            print(f"Redis Error: {e}")

    def get(self, key):
        conn = self.conn()
        return conn.get(key)

    def set(self, key, data, ex_time):
        conn = self.conn()
        conn.set(key, data, ex=ex_time)


class TimescaleDBConnection:
    def __init__(self, timescaledb_secret_name, access_key=None, secret_key=None, region_name=None):
        self.__region_name = region_name
        self.__access_key = access_key
        self.__secret_key = secret_key
        self.__timescaledb_secret_name = timescaledb_secret_name
        self.__aws_secret_manager = SecretManager(region_name=self.__region_name, access_key=self.__access_key,
                                                  secret_key=self.__secret_key)
        self.__timescaledb_values = self.__aws_secret_manager.get_secret_key_value(self.__timescaledb_secret_name)
        self.__username = self.__timescaledb_values.get('username')
        self.__password = self.__timescaledb_values.get('password')
        self.__host = self.__timescaledb_values.get('host')
        self.__port = int(self.__timescaledb_values.get('port'))
        self.__dbname = self.__timescaledb_values.get('dbname')

    def conn(self):
        return psycopg2.connect(user=self.__username, password=self.__password, host=self.__host, port=self.__port,
                                database=self.__dbname)

    def cursor(self, conn):
        """ Return a cursor object """
        return conn.cursor()

    def execute_query(self, query, values=None):
        """ Execute a single query """
        conn = self.conn()
        try:
            cursor = self.cursor(conn=conn)
            cursor.execute(query, values)
            conn.commit()
            return cursor
        finally:
            conn.close()

    def executemany_query(self, query, values=None):
        """ Execute a query with multiple parameters """
        conn = self.conn()
        try:
            cursor = self.cursor(conn=conn)
            cursor.executemany(query, values)
            conn.commit()
            return cursor
        finally:
            conn.close()

    def fetchall(self, query, values=None):
        """ Execute a query and fetch all data """
        conn = self.conn()
        try:
            cursor = self.cursor(conn=conn)
            cursor.execute(query, values)
            result = cursor.fetchall()
            return result
        except Exception as e:
            print(f'ERROR: {str(e)}')
            return []
        finally:
            conn.close()


class MemcachedConnection:
    def __init__(self, memcached_secret_name, access_key=None, secret_key=None, region_name=None, add_context=False):
        self.__region_name = region_name
        self.__access_key = access_key
        self.__secret_key = secret_key
        self.__memcached_secret_name = memcached_secret_name
        self.__aws_secret_manager = SecretManager(region_name=self.__region_name, access_key=self.__access_key,
                                                  secret_key=self.__secret_key)
        self.__memcached_values = self.__aws_secret_manager.get_secret_key_value(self.__memcached_secret_name)
        self.__host = self.__memcached_values.get('host')
        self.__port = self.__memcached_values.get('port')
        if add_context:
            self.__client = PooledClient((self.__host, self.__port), tls_context=context, max_pool_size=20)
        else:
            self.__client = PooledClient((self.__host, self.__port), max_pool_size=20)

    def set_data_into_memcache(self, key, data, ttl=600, verbose=False):
        try:
            key = key.replace(" ", "")
            json_data = json.dumps(data, default=str)

            self.__client.set(key, json_data, expire=ttl)
            if verbose:
                print(f"INFO: Data set to memcached: {data}")
        except Exception as error:
            print(f"ERROR: {error}")

    def get_data_from_memcached(self, key, verbose=False):
        try:
            key = key.replace(" ", "")
            cached_data = self.__client.get(key)

            if cached_data:
                data = json.loads(cached_data)
                if verbose:
                    print(f"INFO: Data got from memcached: {data}")
                return data, True
        except Exception as error:
            print(f"ERROR: {error}")

        return None, None

    def delete_data_from_memcache(self, key, verbose=False):
        try:
            key = key.replace(" ", "")
            self.__client.delete(key)
            if verbose:
                print(f"INFO: Data deleted from memcached for key: {key}")
        except Exception as error:
            print(f"ERROR: {error}")


class TimestreamConnection:
    def __init__(self, access_key=None, secret_key=None, region_name=None):
        self.__access_key = access_key
        self.__secret_key = secret_key
        self.__region_name = region_name

    def get_write_client(self):
        try:
            session = boto3.session.Session(aws_access_key_id=self.__access_key,
                                            aws_secret_access_key=self.__secret_key)
            return session.client(service_name="timestream-write", region_name=self.__region_name)
        except Exception as e:
            print(f'Exception while getting write client for timestream: {e}')
            raise e

    def get_query_client(self):
        try:
            session = boto3.session.Session(aws_access_key_id=self.__access_key,
                                            aws_secret_access_key=self.__secret_key)
            return session.client(service_name="timestream-query", region_name=self.__region_name)
        except Exception as e:
            print(f'Exception while getting query client for timestream: {e}')
            raise e
