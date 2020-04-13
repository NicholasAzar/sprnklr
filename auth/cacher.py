from datetime import datetime, timezone
import logging
import os
import sqlite3
from globals import AccountType, AppLoggerName

logger = logging.getLogger(AppLoggerName)

class AuthCacher(object):
    db_filename = 'auth_cache.db'

    def __init__(self):
        # super().__init__() # for some reason i think this created the db_filename as an empty file? TODO(@nzar): investigate.
        if not os.path.exists(AuthCacher.db_filename):
            self._create_db()
        else:
            logger.debug("Skipping creating db since file already exists")
    
    def _create_db(self):
        logger.debug("Initializing a new cache file.")
        with sqlite3.connect(AuthCacher.db_filename) as conn:
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
    
    def get_tokens(self, user_id:str, account_type:AccountType) -> str:
        logger.debug("Getting refresh token from the db")
        with sqlite3.connect(AuthCacher.db_filename) as conn:
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
        with sqlite3.connect(AuthCacher.db_filename) as conn:
            conn.execute("""
            delete from auth_cache where user_id = \"{}\" and account_type = \"{}\"
            """.format(user_id, account_type.value))

            conn.execute("""
            insert into auth_cache(user_id, account_type, access_token, expiry_utc_posix_timestamp, refresh_token) values (\"{}\", \"{}\", \"{}\", {}, \"{}\");
            """.format(user_id, account_type.value, access_token, expiry_dttm.replace(tzinfo=timezone.utc).timestamp(), refresh_token))






            

