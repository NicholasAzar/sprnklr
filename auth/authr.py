import logging
import os
import yaml
import base64
import json
from datetime import datetime, timedelta
from globals import AccountType, AppLoggerName
from auth.cacher import AuthCacher

logger = logging.getLogger(AppLoggerName)

class Authr(object):
    with open('config/auth_config.yaml', 'r') as auth_config_file:
        auth_config = yaml.load(auth_config_file, Loader=yaml.FullLoader)
        logger.debug("Initialized auth config")
    cacher = AuthCacher()
    
    def __init__(self, account_type: AccountType):
        self.config = Authr.auth_config
        self.account_type = account_type
        logger.debug("Authr init")

    def get_access_token(self, user_id:str = None) -> str:
        if user_id is not None:
            access_token, refresh_token = self._get_tokens_from_cache(user_id)
            if access_token is not None:
                return access_token
            elif refresh_token is not None:
                access_token, expiry_dttm, refresh_token = self._get_tokens_from_refresh(refresh_token)
                if access_token is not None: # if refresh fails for some reason, fallback to get new token.
                    self._persist_tokens(user_id, access_token, expiry_dttm, refresh_token)
                    return access_token
        user_id, access_token, expiry_dttm, refresh_token = self._get_new_token(user_id=user_id)
        self._persist_tokens(user_id, access_token, expiry_dttm, refresh_token)
        return access_token
    
    def _get_new_token(self, user_id:str = None) -> str:
        pass # interface

    def _get_token_from_refresh(self, refresh_token:str) -> str:
        pass # interface
    
    def _get_tokens_from_cache(self, user_id:str) -> dict:
        logger.debug("Checking cache for tokens")
        access_token, expiry_dttm, refresh_token = Authr.cacher.get_tokens(user_id, self.account_type)
        if expiry_dttm is not None and access_token is not None and (datetime.now() + timedelta(seconds=30)) < expiry_dttm:
            logger.info("Found non-expired access token in cache")
            return access_token, None
        elif refresh_token is not None:
            logger.info("Found expired access token, returning refresh")
            return None, refresh_token
        logger.info("No valid tokens found in cache")
        return None, None

    
    def _persist_tokens(self, user_id:str, access_token:str, expiry_dttm:datetime, refresh_token:str) -> None:
        Authr.cacher.persist_tokens(user_id, self.account_type, access_token, expiry_dttm, refresh_token)
    
    def _get_field_from_id_token(self, id_token:str, field_name:str) -> str:
        id_token_body = id_token.split('.')[1]
        id_token_body_padded = id_token_body + "=" * (-len(id_token_body) % 4)
        decoded_body = base64.standard_b64decode(id_token_body_padded)
        logger.debug("Decoded id token body: " + str(decoded_body))
        json_body = json.loads(decoded_body)
        return json_body[field_name]