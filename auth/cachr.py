import os
import sqlite3
from globals import AccountType

class AuthCachr(object):
    db_filename = 'auth_cache.db'

    def __init__(self):
        # super().__init__()
        if not os.path.exists(AuthCachr.db_filename):
            self._create_db()
        else:
            print("Skipping creating db since file already exists")
    
    def _create_db(self):
        print("Creating the auth cache db")
        with sqlite3.connect(AuthCachr.db_filename) as conn:
            conn.execute("""
            create table auth_cache(
                user_id         text,
                account_type    text,
                refresh_token   text,
                PRIMARY KEY (user_id, account_type)
            );
            """)
    
    def get_refresh_token(self, user_id:str, account_type:AccountType) -> str:
        with sqlite3.connect(AuthCachr.db_filename) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            select refresh_token from auth_cache where user_id = \"{}\" and account_type = \"{}\"
            """.format(user_id, account_type.value))
            results = cursor.fetchall()
            if len(results) == 0:
                print("No cached refresh token found for user_id \"{}\" and account_type \"{}\"".format(user_id, account_type.value))
                return None
            else:
                # Impossible for > 1 result since primary key is user_id & account_type
                print("Found cached refresh token for user_id \"{}\" and account_type \"{}\"".format(user_id, account_type.value))
                return results[0][0]
    
    def persist_refresh_token(self, user_id:str, account_type:AccountType, refresh_token:str) -> None:
        with sqlite3.connect(AuthCachr.db_filename) as conn:
            conn.execute("""
            insert into auth_cache(user_id, account_type, refresh_token) values (\"{}\", \"{}\", \"{}\");
            """.format(user_id, account_type.value, refresh_token))






            

