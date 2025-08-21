import pymysql
import pymysql.cursors
from sslib.base.db_conn import DBConn


class MySQL:
    def __init__(self, connect:DBConn) -> None:
        self.conn = pymysql.connect(host=connect.host, port=connect.port, user=connect.user, passwd=connect.password, db=connect.db, charset='utf8', cursorclass=pymysql.cursors.DictCursor)

    def find(self, query:str, args:object = None) -> any:
        try:
            cur = self.conn.cursor()
            cur.execute(query, args)
            result = cur.fetchone()
        finally:
            if cur is not None:
                cur.close()
        return result
    
    def find_all(self, query:str, args:object = None) -> list:
        try:
            cur = self.conn.cursor()
            cur.execute(query, args)
            results = cur.fetchall()
        finally:
            if cur is not None:
                cur.close()
        return results

    def execute(self, query:str, args:object = None) -> int:
        lastId = 0
        try:
            cur = self.conn.cursor()
            cur.execute(query, args)
            self.conn.commit()
            lastId = cur.lastrowid
        except Exception as e:
            print(e)
        finally:
            if cur is not None:
                cur.close()
        return lastId

    def execute_many(self, query:str, args:object):
        try:
            cur = self.conn.cursor()
            cur.executemany(query, args)
            self.conn.commit()
        except Exception as e:
            pass
        finally:
            if cur is not None:
                cur.close()

    def update(self, query:str, args:object = None) -> int:
        affectedRows = 0
        try:
            cur = self.conn.cursor()
            cur.execute(query, args)
            self.conn.commit()
            affectedRows = cur.rowcount
        except Exception as e:
            print(e)
        finally:
            if cur is not None:
                cur.close()
        return affectedRows