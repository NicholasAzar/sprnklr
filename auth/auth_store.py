from datetime import datetime, timezone
import logging
import os
import sqlite3
from globals import AccountType, AppLoggerName

logger = logging.getLogger(AppLoggerName)

class AuthStore(object):
    db_filename = 'auth_store.db'

    def __init__(self):
        # super().__init__() # for some reason i think this created the db_filename as an empty file? TODO(@nzar): investigate.
        if not os.path.exists(AuthStore.db_filename):
            self._create_db()
        else:
            logger.debug("Skipping creating db since file already exists")
    
    def _create_db(self):
        logger.debug("Initializing a new cache file.")
        with sqlite3.connect(AuthStore.db_filename) as conn:
            conn.execute("""
            create table auth_cache(
                user_id         text,
                account_type    text,
                access_token    text,
                expiry_utc_posix_timestamp     number,     
                refresh_token   text,
                PRIMARY KEY (user_id, account_type)
            );
            """)
            conn.execute("""
            create table account_map(
                sprnklr_id       text,
                sprnklr_account_type  text,
                tpy_user_id         text,
                tpy_account_type    text,
                alloc_percentage number,
                active_flg          boolean,
                PRIMARY KEY (sprnklr_id, sprnklr_account_type, tpy_user_id, tpy_account_type)
            );
            """)
            conn.execute("""
            create INDEX account_map_user ON account_map(sprnklr_id, sprnklr_account_type);
            """)
    
    def get_tokens(self, user_id:str, account_type:AccountType) -> str:
        logger.debug("Getting refresh token from the db")
        with sqlite3.connect(AuthStore.db_filename) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            select access_token, expiry_utc_posix_timestamp, refresh_token from auth_cache where user_id = \"{}\" and account_type = \"{}\"
            """.format(user_id, account_type.value))
            results = cursor.fetchall()
            if len(results) == 0:
                logger.debug("No cached refresh token found for user_id \"{}\" and account_type \"{}\"".format(user_id, account_type.value))
                return None, None, None
            else:
                # Impossible for > 1 result since primary key is user_id & account_type
                logger.debug("Found cached refresh token for user_id \"{}\" and account_type \"{}\"".format(user_id, account_type.value))
                access_token, expiry_utc_posix_timestamp, refresh_token = results[0]
                expiry_dttm = datetime.utcfromtimestamp(expiry_utc_posix_timestamp)
                return access_token, expiry_dttm, refresh_token
    
    def persist_tokens(self, user_id:str, account_type:AccountType, access_token:str, expiry_dttm:datetime, refresh_token:str) -> None:
        with sqlite3.connect(AuthStore.db_filename) as conn:
            conn.execute("""
            delete from auth_cache where user_id = \"{}\" and account_type = \"{}\"
            """.format(user_id, account_type.value))

            conn.execute("""
            insert into auth_cache(user_id, account_type, access_token, expiry_utc_posix_timestamp, refresh_token) values (\"{}\", \"{}\", \"{}\", {}, \"{}\");
            """.format(user_id, account_type.value, access_token, expiry_dttm.replace(tzinfo=timezone.utc).timestamp(), refresh_token))

    def add_linked_account(self, sprnklr_id:str, tpy_user_id:str, tpy_account_type:AccountType, alloc_percentage:float, active_flg:bool = True):
        with sqlite3.connect(AuthStore.db_filename) as conn:
            query = """
            insert into account_map(sprnklr_id, sprnklr_account_type, tpy_user_id, tpy_account_type, alloc_percentage, active_flg) values (\"{}\", \"{}\", \"{}\", \"{}\", {}, {});
            """.format(sprnklr_id, AccountType.SPRNKLR.value, tpy_user_id, tpy_account_type.value, alloc_percentage, 1 if active_flg else 0)
            logger.debug("Running query: " + query)
            conn.execute(query)

    def get_linked_accounts(self, sprnklr_id:str):
        with sqlite3.connect(AuthStore.db_filename) as conn:
            cursor = conn.cursor()
            query = """
            select tpy_user_id, tpy_account_type, alloc_percentage 
            from account_map
            where sprnklr_id = \"{}\"
            and sprnklr_account_type = \"{}\"
            and active_flg = 1
            """.format(sprnklr_id, AccountType.SPRNKLR.value) 
            logger.debug("Running query: " + query)
            cursor.execute(query)
            results = cursor.fetchall()
            if results is None or len(results) == 0:
                return []
            return results





            

