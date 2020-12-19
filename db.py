import sqlite3
from os.path import join as path_to
import time


class Database:
    def __init__(self, name):
        self.con = None
        self.cur = None
        self.address = path_to(rf'data\databases', name)

    def add_user_in_auth(self, email, password):
        try:
            self.con = sqlite3.connect(self.address)
            self.cur = self.con.cursor()
            print(email, 'auth')
            self.cur.execute(f'INSERT INTO auth (password, email) VALUES ("{password}", "{email}");')

            self.con.commit()
            return ['', 200]
        except Exception as e:
            print('db: ', e)
            return [e, 400]

    def add_user_in_profile(self, email):
        try:
            self.con = sqlite3.connect(self.address)
            self.cur = self.con.cursor()
            print(email, 'profile')
            self.cur.execute(f'INSERT INTO profile (email) VALUES ("{email}");')

            self.con.commit()
            return ['', 200]
        except Exception as e:
            print('db: ', e)
            return [e, 400]

    def add_user(self, email, password):
        res = self.add_user_in_auth(email, password)
        res.append(self.add_user_in_profile(email))
        return res

    def get_info(self, name, columns, table):
        try:
            self.con = sqlite3.connect(self.address)
            self.cur = self.con.cursor()
            res = self.cur.execute(f'SELECT {str(columns)} FROM {table} WHERE email = "{name}";').fetchall()
            try:
                print('db res: ', res[0][0])
                return [res, 200]
            except IndexError:
                return ['', 404]

        except Exception as e:
            print('db: ', e)
            if e == 'database is locked':
                time.sleep(5)
                try:
                    self.con = sqlite3.connect(self.address)
                    self.cur = self.con.cursor()
                    res = self.cur.execute(f'SELECT {str(columns)} FROM {table} WHERE email = "{name}";').fetchall()
                    return [res, 200]
                except Exception as e:
                    print('db: ', e)
                    return [e, 400]
            return [e, 400]

    def put_info(self, row, row_val, column, value, table):
        try:
            self.con = sqlite3.connect(self.address)
            self.cur = self.con.cursor()
            print(f'UPDATE {table} SET {column} = "{value}" WHERE {row} = "{row_val}";')
            self.cur.execute(f'UPDATE {table} SET {column} = "{value}" WHERE {row} = "{row_val}";')
            self.con.commit()
            return ['', 200]
        except Exception as e:
            print('db: ', e, 'val: ', value)
            return [e, 400]
