import subprocess
import sys
import importlib.util
import pkg_resources


def install_package(package):
    try:
        pkg_resources.get_distribution(package)
    except pkg_resources.DistributionNotFound:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    # finally:
    #     globals()[package] = importlib.import_module(package)


def import_package(package_name):
    try:
        module = importlib.import_module(package_name)
        return module
    except ImportError as e:
        print(f"Erro ao importar o pacote {package_name}: {e}")
        return None


def install_package_database(db_type):
    if db_type.lower() == 'mysql':
        install_package('mysql-connector-python')
    elif db_type.lower() == 'sql':
        install_package('pyodbc')
    elif db_type.lower() == 'oracle':
        install_package('cx_Oracle')
    elif db_type.lower() == 'firebird':
        install_package('firebirdsql==1.2.3')
    else:
        raise ValueError("Tipo de banco de dados não suportado")
