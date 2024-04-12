import sqlite3

class SQLiteDB:
    def __init__(self, db_path):
        self.db_path = db_path

    def no_array(self,array):
        for f in array:
            return f 

    def login(self, username, password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()

        conn.close()

        if result:
            columns = [desc[0] for desc in cursor.description]
            user_data = dict(zip(columns, result))
            return user_data
        else:
            return None

    def select_data(self, query):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(query)
        result = cursor.fetchall()

        conn.close()

        return result

    def execute_query(self, query):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(query)
            conn.commit()
            return True
        except:
            conn.rollback()
            return False
        finally:
            conn.close()
