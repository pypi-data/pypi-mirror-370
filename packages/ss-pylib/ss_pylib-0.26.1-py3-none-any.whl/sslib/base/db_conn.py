class DBConn:
    def __init__(self, host:str, port:int, user:str, password:str, db:str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db