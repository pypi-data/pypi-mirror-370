import pandas as pd
import snowflake.connector
from .credentials import SnowflakeCredentials


class SnowflakeConn:
    def __init__(self, server_creds=None, **kwargs):
        """ Initialize the class
        -----------------------------
        server_creds = {
                        "account": "",
                        "db_name": "",
                        "user_name": "",
                        "password": ""
                        }

        -----------------------------
        :param server_creds: Dictionary containing the info to connect to the Server
        :param kwargs: Additional parameters to be passed to the connection
        """

        self.conn_str = None
        self.conn = None

        if kwargs != {}:
            try:
                db = kwargs['db_name']
                server_creds = SnowflakeCredentials(db).simple_creds()
            except KeyError:
                raise KeyError('Please provide a valid db_name and server_type')

        self.db = server_creds['db_name']
        self.user = server_creds['user_name']
        self.pw = server_creds['password']
        self.account = server_creds['account']

        if self.user and self.pw and self.account:
            self.connect()

    def connect(self):
        """ Open the connection to Snowflake """
        self.conn = snowflake.connector.connect(
            user=self.user,
            password=self.pw,
            account=self.account,
            database=self.db)

    def close(self):
        """ Close the connection to Snowflake """
        self.conn.close()

    def query(self, sql_query):
        """ Read data from Snowflake according to the sql_query
        -----------------------------
        query_str = "SELECT * FROM %s" & table
        con_.query(query_str)
        -----------------------------
        :param sql_query: Query to be sent to Snowflake
        :return: DataFrame gathering the requested data
        """
        cursor = None
        self.connect()
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            col_names = [desc[0] for desc in cursor.description]
            result = pd.DataFrame(rows, columns=col_names)
            return result
        except Exception as e:
            raise Exception(e)
        finally:
            if cursor:
                cursor.close()
            self.close()
