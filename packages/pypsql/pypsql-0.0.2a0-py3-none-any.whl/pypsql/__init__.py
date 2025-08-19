# Define the package version
__version__ = "0.0.2-alpha"


# Import public classes and functions
from .connect import get_credentials, hash_value, DatabaseConnector
from .ssh_connect import SSHDatabaseConnector