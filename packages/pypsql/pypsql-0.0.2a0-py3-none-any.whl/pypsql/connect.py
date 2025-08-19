import re
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy import text
import pandas as pd
import hashlib
import pathlib


def get_credentials(path, filename):
    """Load database credentials from a simple key=value file, or interactively prompt the user.

    The credentials file is expected to contain one *key=value* pair per line. Values may be
    single-quoted. Example:

    .. code-block:: python

        server=localhost
        port=5432
        name_database='mydb'
        name_user='alice'
        password_user='s3cr3t'

    If the file is missing, the user is prompted for each required field.

    Args:
        path (pathlib.Path): Directory containing the credentials file.
        filename (str): Name of the credentials file to read.

    Returns:
        dict: A dictionary with keys:
            - ``server`` (str)
            - ``port`` (str)
            - ``name_database`` (str)
            - ``name_user`` (str)
            - ``password_user`` (str)

    Notes:
        - Trailing quotes in values are stripped.
        - Empty or malformed lines are ignored.

    Example:
        .. code-block:: python

            creds = get_credentials(Path.cwd(), "_credentials.py")
            uri = f"postgresql://{creds['name_user']}:{creds['password_user']}@{creds['server']}:{creds['port']}/{creds['name_database']}"
    """
    try:
        with open(path / filename, 'r') as file:
            cred_list = file.read().splitlines()
        cred_dict = {re.split('=',element)[0].strip() : re.sub("'","",re.split('=',element)[1].strip()) for element in cred_list}

    except FileNotFoundError:
        pass
        cred_dict = {}
        cred_dict['server'] = input("Enter the database's address: ")
        cred_dict['port'] = input("Enter the port: ")
        cred_dict['name_database'] = input("Enter the database's name: ")
        cred_dict['name_user'] = input("Enter your username: ")
        cred_dict['password_user'] = input("Enter your username's password: ")

    return cred_dict


def hash_value(value):
    """Compute a SHA-256 hash (hex digest) of a UTF-8 string.

    Args:
        value (str): The input string to hash.

    Returns:
        str: The 64-character hexadecimal SHA-256 digest.

    Example:
        .. code-block:: python

            digest = hash_value("p@ssw0rd")
            # '5e884898da28047151d0e56f8dc62927...'
    """
    sha256 = hashlib.sha256()
    sha256.update(value.encode('utf-8'))

    return sha256.hexdigest()


class DatabaseConnector():
    """Create a PostgreSQL connector backed by SQLAlchemy with a queued connection pool.

    This class reads connection parameters from a credentials file (see
    ``get_credentials``) and constructs an SQLAlchemy engine. It provides helpers
    to execute queries, push pandas DataFrames, and run SQL scripts.

    Args:
        path (pathlib.Path, optional): Base path where SQL files and the credentials
            file live. Defaults to the directory of this module.
        db_credential_file (str, optional): Filename of the credentials file within
            ``path``. Defaults to ``'_credentials.py'``.

    Attributes:
        path (pathlib.Path): Base path for SQL files and credentials.
        db_credential_file (str): Credentials filename.
        server (str): Database host.
        port (str): Database port.
        name_database (str): Database name.
        name_user (str): Username.
        password_user (str): Password.
        engine (sqlalchemy.engine.Engine): Configured SQLAlchemy engine using
            ``QueuePool`` (``pool_size=10``).

    Example:
        .. code-block:: python

            dbc = DatabaseConnector()
            with dbc.start_engine() as conn:
                rows = conn.execute(text("SELECT 1")).all()
    """
    def __init__(self, path=pathlib.Path(__file__).parent.resolve(), db_credential_file='_credentials.py'):
        self.path = path
        self.db_credential_file = db_credential_file

        credentials = get_credentials(self.path, self.db_credential_file)
        self.server = credentials['server']
        self.port = credentials['port']
        self.name_database = credentials['name_database']
        self.name_user = credentials['name_user']
        self.password_user = credentials['password_user']
        self.engine = create_engine(
            'postgresql://' + self.name_user +':' + self.password_user + '@' + self.server + ':' + self.port + '/' + self.name_database, 
            poolclass=QueuePool, 
            pool_size=10
        )

    def start_engine(self):
        """Open a new connection from the configured SQLAlchemy engine.

        Returns:
            sqlalchemy.engine.Connection: An active database connection.

        Notes:
            The caller is responsible for closing the connection (use a context manager
            or ``close()``).
        """
        return self.engine.connect()

    def is_multiline(self, string):
        """Return True if the string contains at least one newline.

        Args:
            string (str): String to test.

        Returns:
            bool: ``True`` if multiline, else ``False``.
        """
        return '\n' in string

    def get_data(self, sql_file:str, replace_dict:dict={}, outcommenting:list=[]):
        """
        Fetch data using an external SQL file or a raw SQL string with simple templating.

        You can pass either:

        - the path (relative to ``self.path``) to a ``.sql`` file, **or**
        - a raw SQL string (multiline strings are treated as SQL).

        Two templating conventions are supported:

        - ``%KEY`` → replaced with a **quoted** value when ``replace_dict['KEY']`` is a string,
          or with the plain value for non-strings.
        - ``§KEY`` → replaced with the **unquoted** value (useful for identifiers or lists).

        You can also **outcomment** lines containing a key and a percent marker by listing the
        key in ``outcommenting``. Matching lines are prefixed with ``--`` **only if** that key
        has not already been replaced.

        Args:
            sql_file (str): Relative path to a SQL file under ``self.path`` **or** a raw
                SQL string (multiline).
            replace_dict (dict, optional): Mapping of placeholder keys to replacement values.
                Use ``%KEY`` for auto-quoting strings, ``§KEY`` for raw insertion.
                Defaults to ``{}``.
            outcommenting (list, optional): Keys whose matching lines (containing the key and
                a ``%``) should be commented out. Defaults to ``[]``.

        Returns:
            pandas.DataFrame: Query results.

        Examples
        --------

        Replace a scalar::

            df = dbc.get_data("queries/get_users.sql", replace_dict={"user_id": 42})

        Insert a raw identifier or list::

            df = dbc.get_data("q.sql", replace_dict={"schema": "public"})
            # In SQL: SELECT * FROM §schema.users  -> SELECT * FROM public.users

        Outcomment a filter::

            df = dbc.get_data("q.sql", outcommenting=["limit_clause"])
            # A line like:  AND users.age > %limit_clause  ->  --AND users.age > %limit_clause

        Notes
        -----
        - Replacements are simple regex substitutions; ensure your placeholders do not
          collide with SQL content.
        - Prefer parameterized queries for user-supplied data when possible.

        Security
        --------
        This helper performs textual substitution. Avoid injecting untrusted input into
        identifiers or raw fragments (``§KEY``). For dynamic values, prefer ``%KEY`` with
        safe literals or use SQLAlchemy parameters.
        """
        if self.is_multiline(str(sql_file)) == False:
            with open(self.path / sql_file, 'r') as file:
                query = file.read()
        else:
            query = sql_file

        for key, value in replace_dict.items():
            if isinstance(value, str):
                query = re.sub('%'+key, "'" + str(value)+ "'", query)
                query = re.sub('§'+key,  str(value), query)
            else:
                query = re.sub('%'+key, str(value), query)

        if outcommenting != []:
            for oc in outcommenting:
                dict_outcomment = {line:'--'+line for line in query.splitlines() if re.search(oc, line) != None and re.search('%', line) != None}
                for k,v in dict_outcomment.items():
                    query = re.sub(k,v,query)
        # print(query)
        query = text(query)

        with self.engine.connect() as connection:
            df = pd.read_sql(query, connection)

        return df

    def push_data(self, df:pd.DataFrame, schema:str, table:str, if_exists:str='replace', index=True):
        """Write a pandas DataFrame to a PostgreSQL table.

        Args:
            df (pandas.DataFrame): The DataFrame to persist.
            schema (str): Target schema name.
            table (str): Target table name.
            if_exists (str, optional): One of ``'replace'``, ``'fail'``, or ``'append'``.
                Defaults to ``'replace'``.
            index (bool, optional): Whether to write the DataFrame index. Defaults to ``True``.

        Returns:
            None

        Example:
            .. code-block:: python

                dbc.push_data(df, schema="public", table="events", if_exists="append")

        Notes:
            Uses ``engine.begin()`` for transactional writes and sets ``index_label='idx'``
            when ``index=True``.
        """
        with self.engine.begin() as connection:  # Ensures proper transaction handling and connection closure
            df.to_sql(name=table, con=connection, schema=schema, if_exists=if_exists, index=index, index_label='idx')


    def drop_table(self, schema: str, table: str):
        """Drop a table if it exists.

        Args:
            schema (str): Schema name.
            table (str): Table name.

        Returns:
            None

        Example:
            .. code-block:: python

                dbc.drop_table("public", "staging_temp")
        """
        query = f"DROP TABLE IF EXISTS {schema}.{table}"

        with self.engine.begin() as connection:
            connection.execute(text(query))


    def execute_script(self, sql_script: str):
        """Execute an arbitrary SQL script within a transaction.

        Args:
            sql_script (str): A full SQL statement or multi-statement script.

        Returns:
            None

        Example:
            .. code-block:: python

                dbc.execute_script(\"\"\"
                CREATE TABLE IF NOT EXISTS public.example(id int primary key);
                INSERT INTO public.example VALUES (1) ON CONFLICT DO NOTHING;
                \"\"\")
        """
        with self.engine.begin() as connection:
            connection.execute(text(sql_script))


    def _reconnect_engine(self):
        """(Internal) Create a fresh SQLAlchemy engine with the current credentials.

        Returns:
            sqlalchemy.engine.Engine: A newly constructed engine instance with
            ``gssencmode=disable`` and a ``QueuePool`` (``pool_size=10``).

        Notes:
            Useful if the original engine needs to be recreated due to environment changes.
        """
        return create_engine(
            f'postgresql://{self.name_user}:{self.password_user}@'
            f'{self.server}:{self.port}/{self.name_database}'
            f'?gssencmode=disable',
            poolclass=QueuePool,
            pool_size=10
        )
