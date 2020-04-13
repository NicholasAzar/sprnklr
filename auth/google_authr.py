import logging
import os
import webbrowser
import requests
import json
from datetime import datetime, timedelta
from flask import Flask, request, Response
from globals import AccountType, AppLoggerName
from auth.authr import Authr

logger = logging.getLogger(AppLoggerName)

class GoogleAuthr(Authr):
    def __init__(self):
        super().__init__(AccountType.GOOGLE)
        self.config = self.config['google']
        logger.debug("GoogleAuthr init")

    def _get_tokens_from_refresh(self, refresh_token:str) -> (str, datetime, str):
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
            if 'refresh_token' in result:
                refresh_token = result['refresh_token']
            return result['access_token'], expiry_dttm, refresh_token
        else:
            logger.warn('Error getting access token using refresh: ' + response.content)
        return (None, None, None)

    def _get_new_token(self, user_id:str = None):
        flask_app = Flask(__name__)
        flask_app.add_url_rule('/', '/', self)
        webbrowser.open_new_tab(self._build_auth_code_url(user_id=user_id))
        flask_app.run()
        logger.debug("Back to obj with auth code: " + self.auth_code)
        return self._get_new_token_from_code()

    def _get_new_token_from_code(self) -> (str, str, datetime, str):
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
            user_id = self._get_field_from_id_token(json_data['id_token'], 'email')
            logger.debug('Got user id from id_token: ' + user_id)
            return user_id, json_data['access_token'], expiry_dttm, json_data['refresh_token']
            # return json_data['access_token']
        else:
            logger.error("Failed to get new token: " + str(response.content))
        return (None, None, None, None)

    def _build_auth_code_url(self, user_id:str = None):
        auth_url = "{}?client_id={}&response_type={}&scope={}&access_type={}&redirect_uri={}".format(
            self.config['auth_url'], 
            self.config['client_id'], 
            self.config['response_type'], 
            self.config['scope'],
            self.config['access_type'],
            self.config['redirect_uri'])
        if user_id is not None:
            auth_url += "&login_hint=" + user_id
        return auth_url

    # Receive auth code
    def __call__(self):
        self.auth_code = request.args.get('code')
        logger.debug('Got auth code: {}'.format(str(self.auth_code)))

        # TODO(@nzar): implement error param handler
        shutdown_hook = request.environ.get('werkzeug.server.shutdown')
        if shutdown_hook is not None:
            shutdown_hook()
        return Response(status=200, headers={})