from hdbcli import dbapi
from config import db_config    

def get_connection():
    conn = dbapi.connect(
        address=db_config.sap_hana_url,
        port=db_config.sap_hana_port,
        user=db_config.sap_hana_username,
        password=db_config.sap_hana_password,
    )
    _ = conn.cursor()

    return conn
