import logging
import os
import yaml
import base64
import webbrowser
import requests
import json
from datetime import datetime, timedelta
from flask import Flask, request, Response
from globals import AccountType, AppLoggerName
from auth.cacher import AuthCacher

logger = logging.getLogger(AppLoggerName)

class Authr(object):
    with open('config/auth_config.yaml', 'r') as auth_config_file:
        auth_config = yaml.load(auth_config_file, Loader=yaml.FullLoader)
        logger.debug("Initialized auth config")
    cacher = AuthCacher()
    
    def __init__(self, user_id:str, account_type:AccountType):
        self.config = Authr.auth_config
        self.user_id = user_id
        self.account_type = account_type
        logger.debug("Authr init")

    def get_access_token(self) -> str:
        pass # interface
    
    def _get_tokens_from_cache(self) -> dict:
        logger.debug("Checking cache for tokens")
        access_token, expiry_dttm, refresh_token = Authr.cacher.get_tokens(self.user_id, self.account_type)
        if expiry_dttm is not None and access_token is not None and (datetime.now() + timedelta(seconds=30)) < expiry_dttm:
            logger.info("Found non-expired access token in cache")
            return access_token, None
        elif refresh_token is not None:
            logger.info("Found expired access token, returning refresh")
            return None, refresh_token
        logger.info("No valid tokens found in cache")
        return None, None

    
    def _persist_tokens(self, access_token:str, expiry_dttm:datetime, refresh_token:str) -> None:
        Authr.cacher.persist_tokens(self.user_id, self.account_type, access_token, expiry_dttm, refresh_token)


class GoogleAuthr(Authr):
    def __init__(self, user_id, account_type):
        super().__init__(user_id, account_type)
        self.config = self.config['google_auth']
        logger.debug("GoogleAuthr init")

    def get_access_token(self) -> str:
        access_token, refresh_token = self._get_tokens_from_cache()
        if access_token is not None:
            return access_token
        elif refresh_token is not None:
            refresh_result = self._get_token_from_refresh(refresh_token)
            if refresh_result is not None: # if refresh fails for some reason, fallback to get new token.
                return refresh_result
        return self._get_new_token()

    def _get_token_from_refresh(self, refresh_token:str) -> str:
        logger.debug("Found refresh, trying to use it.")
        request_body = {
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret'],
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        response = requests.post(url=self.config['token_url'], data=request_body)
        if response.status_code == 200:
            logger.debug('Get token from refresh success: ' + response.text)
            result = json.loads(response.text)
            expiry_dttm = datetime.now() + timedelta(seconds=result['expires_in'])
            self._persist_tokens(result['access_token'], expiry_dttm, refresh_token) # should I use the new one?
            return result['access_token']
        else:
            logger.warn('Error getting access token using refresh: ' + response.content)
        return None

    def _get_new_token(self):
        flask_app = Flask(__name__)
        flask_app.add_url_rule('/', '/', self)
        webbrowser.open_new_tab(self._build_auth_code_url())
        flask_app.run()
        logger.debug("Back to obj with auth code: " + self.auth_code)
        return self._get_new_token_from_code()

    def _get_new_token_from_code(self):
        request_body = {
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret'],
            'code': self.auth_code,
            'redirect_uri': self.config['redirect_uri'],
            'grant_type': self.config['grant_type']
        }
        logger.debug("Sending request to " + self.config['token_url'] + " with data: " + str(request_body))
        response = requests.post(url=self.config['token_url'], data=request_body)
        if response.status_code == 200:
            logger.debug("Get new token success: " + response.text)
            json_data = json.loads(response.text)
            expiry_dttm = datetime.now() + timedelta(seconds=json_data['expires_in'])
            self._persist_tokens(json_data['access_token'], expiry_dttm, json_data['refresh_token'])
            return json_data['access_token']
        else:
            logger.error("Failed to get new token: " + str(response.content))

    def _build_auth_code_url(self):
        auth_url_format = "{}?client_id={}&response_type={}&scope={}&access_type={}&redirect_uri={}&login_hint={}"
        return auth_url_format.format(self.config['auth_url'], self.config['client_id'], self.config['response_type'], self.config['scope'], self.config['access_type'], self.config['redirect_uri'], self.user_id)

    # Receive auth code
    def __call__(self):
        self.auth_code = request.args.get('code')
        logger.debug('Got auth code: {}'.format(str(self.auth_code)))

        # TODO(@nzar): implement error param handler
        shutdown_hook = request.environ.get('werkzeug.server.shutdown')
        if shutdown_hook is not None:
            shutdown_hook()
        return Response(status=200, headers={})


class AuthrFactory(object):
    @staticmethod
    def get_authr(user_id:str, account_type:AccountType) -> Authr:
        if account_type == AccountType.GOOGLE:
            return GoogleAuthr(user_id, account_type)