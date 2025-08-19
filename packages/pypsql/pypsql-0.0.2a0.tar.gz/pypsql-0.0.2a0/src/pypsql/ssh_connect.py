# ssh_connect.py
import subprocess, time, pathlib
from .connect import DatabaseConnector
import socket

class SSHDatabaseConnector:
    """Create an SSH-based PostgreSQL connector with automatic tunneling.

    This class establishes a local SSH tunnel to a remote host and binds it to a
    local port. It then delegates all database operations to an underlying
    ``DatabaseConnector`` instance configured to use the tunneled connection.

    Args:
        ssh_host (str): Remote SSH hostname or IP.
        ssh_username (str): SSH username.
        ssh_pkey (str): Path to a private key file for SSH authentication.
        ssh_port (int, optional): SSH port. Defaults to 22.
        remote_bind_address (tuple, optional): (host, port) tuple for the remote
            database endpoint. Defaults to ('127.0.0.1', 5432).
        local_bind_port (int, optional): Local port to bind the tunnel. Defaults to 6543.
        db_credential_file (str, optional): Credentials filename for the database.
            Defaults to '_credentials.py'.
        path (pathlib.Path, optional): Base path for credentials and SQL files.
            Defaults to the module directory.

    Attributes:
        ssh_host (str): Remote host.
        ssh_username (str): SSH user.
        ssh_pkey (str): Private key path.
        ssh_port (int): SSH port.
        remote_bind_address (tuple): Remote DB host and port.
        local_bind_port (int): Local tunnel port.
        path (pathlib.Path): Base path for SQL and credentials.
        db (DatabaseConnector): Active database connector bound to localhost.

    Example:
        .. code-block:: python
        
            with SSHDatabaseConnector(
                ssh_host="example.com",
                ssh_username="alice",
                ssh_pkey="~/.ssh/id_rsa",
            ) as ssh_db:
                df = ssh_db.get_data("queries/get_users.sql")
    """
    def __init__(self,
                 ssh_host: str,
                 ssh_username: str,
                 ssh_pkey: str,
                 ssh_port: int = 22,
                 remote_bind_address: tuple = ('127.0.0.1', 5432),
                 local_bind_port: int = 6543,
                 db_credential_file: str = '_credentials.py',
                 path: pathlib.Path = pathlib.Path(__file__).parent.resolve(),
                 ):
        self.ssh_host = ssh_host
        self.ssh_username = ssh_username
        self.ssh_pkey = ssh_pkey
        self.ssh_port = ssh_port
        self.remote_bind_address = remote_bind_address
        self.local_bind_port = local_bind_port
        self.path = path
        self.db_credential_file = db_credential_file

        # Launch a background ssh tunnel
        cmd = [
            "ssh",
            "-i", str(self.ssh_pkey),
            "-p", str(self.ssh_port),
            "-L", f"{self.local_bind_port}:{self.remote_bind_address[0]}:{self.remote_bind_address[1]}",
            f"{self.ssh_username}@{self.ssh_host}",
            "-N",  # no remote command
            "-o", "StrictHostKeyChecking=no",
            "-o", "ExitOnForwardFailure=yes"
        ]
        self._proc = subprocess.Popen(cmd)
        time.sleep(1)   # give the tunnel a moment to come up

        sock = socket.socket()
        try:
            sock.connect(('127.0.0.1', self.local_bind_port))
            sock.close()
            print(f"✅ Tunnel is listening on localhost:{self.local_bind_port}")
        except Exception as e:
            raise RuntimeError(f"Tunnel failed to bind on localhost:{self.local_bind_port}") from e


        # now point your connector at localhost:<local_bind_port>
        self.db = DatabaseConnector(path=self.path, db_credential_file=self.db_credential_file)
        self.db.server = '127.0.0.1'
        self.db.port = str(self.local_bind_port)
        self.db.engine = self.db._reconnect_engine()

    def get_data(self, *args, **kwargs):
        """Fetch data via the tunneled DatabaseConnector.

        Delegates to ``DatabaseConnector.get_data``.

        Args:
            *args: Positional arguments forwarded to ``get_data``.
            **kwargs: Keyword arguments forwarded to ``get_data``.

        Returns:
            pandas.DataFrame
        """
        return self.db.get_data(*args, **kwargs)

    def push_data(self, *args, **kwargs):
        """Push data via the tunneled DatabaseConnector.

        Delegates to ``DatabaseConnector.push_data``.

        Args:
            *args: Positional arguments forwarded.
            **kwargs: Keyword arguments forwarded.

        Returns:
            None
        """
        return self.db.push_data(*args, **kwargs)

    def drop_table(self, *args, **kwargs):
        """Drop a table via the tunneled DatabaseConnector.

        Delegates to ``DatabaseConnector.drop_table``.

        Args:
            *args: Positional arguments forwarded.
            **kwargs: Keyword arguments forwarded.

        Returns:
            None
        """
        return self.db.drop_table(*args, **kwargs)

    def execute_script(self, *args, **kwargs):
        """Execute a SQL script via the tunneled DatabaseConnector.

        Delegates to ``DatabaseConnector.execute_script``.

        Args:
            *args: Positional arguments forwarded.
            **kwargs: Keyword arguments forwarded.

        Returns:
            None
        """
        return self.db.execute_script(*args, **kwargs)

    def close(self):
        """Close the SSH tunnel and clean up resources.

        This method terminates the background SSH process if it is still running.

        Returns:
            None
        """
        self._proc.terminate()
        self._proc.wait()

    def __enter__(self):
        """Enter the context manager.

        Returns:
            SSHDatabaseConnector: Self reference for use in ``with`` blocks.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager.

        Ensures that the tunnel is closed even if an exception occurs.

        Args:
            exc_type (type): Exception type.
            exc_val (Exception): Exception value.
            exc_tb (traceback): Traceback object.

        Returns:
            bool: Always ``False`` to propagate any exception raised inside the with-block.
        """
        # always close the tunnel, even on error
        self.close()
        # returning False will re‑raise any exception inside the with‑block
        return False

    def close(self):
        """Destructor hook to ensure tunnel cleanup.

        Attempts to close the SSH tunnel gracefully when the object is garbage collected.
        Suppresses any exceptions.
        """
        if hasattr(self, "_proc") and self._proc.poll() is None:
            self._proc.terminate()
            self._proc.wait()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass