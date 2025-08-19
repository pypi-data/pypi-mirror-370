import pypsql
from pathlib import Path
import pandas as pd
from datetime import datetime


df = pd.DataFrame({'test':[1, 2, 3]})
df['timestamp'] = pd.Timestamp.now()

# sql_script = """
# BEGIN;

# -- 1. Create (if not exists) and make postgres the owner
# CREATE SCHEMA IF NOT EXISTS test_schema
#   AUTHORIZATION postgres;

# -- 2. Give postgres the right to use and create inside it
# GRANT USAGE ON SCHEMA test_schema TO postgres;
# GRANT CREATE ON SCHEMA test_schema TO postgres;
# """

# ssh connection
with pypsql.SSHDatabaseConnector(
    ssh_host='10.1.4.56',
    ssh_username='ubuntu',
    ssh_pkey='/Users/marli453/.ssh/id_rsa_docker',
    ssh_port=888,
    remote_bind_address=('172.18.0.4', 5432),
    local_bind_port=5432,
    path=Path("/Users/marli453/Desktop/"),
    db_credential_file='db_credentials.py'
) as conn:
    # Execute script above
    # conn.execute_script(sql_script)

    # Push pandas DataFrame generated above to DB
    conn.push_data(df=df, schema='test_schema', table='test_table', if_exists='replace')

    # Load the created table from the DB into memory
    test_sql = """
    SELECT * 
    FROM test_schema.test_table
    """

    df_test = conn.get_data(test_sql)
    print(df_test)

    # Delete table from the DB
    conn.drop_table(schema='test_schema', table='test_table')



# # local connection
# conn = pypsql.DatabaseConnector(
#     path=Path("/Users/marli453/Desktop/"),
#     db_credential_file='db_credentials_local.py'
# )

# conn.execute_script(sql_script)
# conn.push_data(df=df, schema='test_schema', table='test_table', if_exists='replace')