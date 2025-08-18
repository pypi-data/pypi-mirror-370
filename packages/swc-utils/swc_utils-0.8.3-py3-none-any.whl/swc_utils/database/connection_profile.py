class ConnectionProfile:
    """
    ConnectionProfile class is used to store the connection information for the database.
    """
    def __init__(self, host: str, port: int, database: str, username: str, password: str, sql_type: str):
        """
        :param host: Database host
        :param port: Database port
        :param database: Database name
        :param username: Database username
        :param password: Database password
        :param sql_type: Database type (sqlite or mysql)
        """
        self.mysql_host = host
        self.mysql_port = port
        self.mysql_database = database
        self.mysql_username = username
        self.mysql_password = password
        self.sql_type = sql_type
        
    @property
    def connection_uri(self) -> str:
        if self.sql_type == "sqlite":
            uri_elements = [
                'sqlite:///',
                self.mysql_database
            ]
        elif self.sql_type == "mysql":
            uri_elements = [
                'mysql://',
                self.mysql_username,
                ':',
                self.mysql_password,
                '@',
                self.mysql_host,
                ':',
                str(self.mysql_port),
                '/',
                self.mysql_database
            ]
        else:
            raise TypeError("No such SQLType", self.sql_type)
        
        return ''.join(uri_elements)
