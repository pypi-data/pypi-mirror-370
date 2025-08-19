# pypSQL


<a href="https://www.marius-liebald.com/pypsql/index.html" style="float:right; margin-left:10px;">
<img src="docs/source/_static/img/pypsql_logo_dark.png" style="height:139px !important; width:auto !important;" alt="pypsql utilities website" />
</a>

<!-- badges: start -->

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
<!-- badges: end -->

`pypsql` is a lightweight framework for connecting to PostgreSQL
databases, whether locally or remotely hosted. It builds on top of
[`SQLAlchemy`](https://www.sqlalchemy.org/) to provide a simple,
Pythonic interface for establishing connections, running queries, and
managing database sessions.

# Contributors

[Marius Liebald](https://www.marius-liebald.de) (maintainer)

# Installation

``` bash
pip install pypsql
```

# Basic Usage

## Provide database credentials

You can store the database connection details in a file, for example:

``` python
server=<host name or address>   # e.g., localhost, 127.0.0.1, or a public IP
port=<port number>              # default: 5432
name_database=<database name>   # e.g., my_db
name_user=<role>                # e.g., Alice
password_user=<password>        # e.g., 123abc
```

You may place this file anywhere on the client machine. Importantly,
this step is optional. You can also provide the variables interactively
via terminal prompts.

## No SSH required

An SSH tunnel is not needed if:

- the server and client run on the same machine,
- the server and client are in the same (virtual) network, or
- the server is accessible via its public IP.

In this case, simply run the Python script:

``` python
import pypsql
from pathlib import Path

conn = pypsql.DatabaseConnector(
    path=Path(<path to the credential file>), # e.g., "/Users/marius/Desktop/"
    db_credential_file=<name of credential file>   # e.g., "credentials.py"
)

sql_script = """
SELECT *
FROM customers
"""

df = conn.get_data(sql_script)

print(df)
```

Note that this example assumes the database contains a table named
`customers`.

## Connection via SSH

To be filled.

# Official Documentation

The documentation is hosted under
<https://www.marius-liebald.com/pypsql/index.html>

# License

The package is distributed under the [MIT license](LICENSE.txt).

# References

<div id="refs" class="references csl-bib-body hanging-indent"
entry-spacing="0">

<div id="ref-sqlalchemy2025" class="csl-entry">

Bayer, Michael, and contributors. 2025. “SQLAlchemy.”
<https://www.sqlalchemy.org/>.

</div>

</div>
