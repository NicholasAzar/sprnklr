import os
import yaml
import base64
import webbrowser
import requests
import json
from flask import Flask, request, Response
from globals import AccountType
from auth.cachr import AuthCachr


class Authr(object):
    with open('config/auth_config.yaml', 'r') as auth_config_file:
        auth_config = yaml.load(auth_config_file, Loader=yaml.FullLoader)
        print("Initialized auth config")
    cachr = AuthCachr()
    
    def __init__(self, user_id:str, account_type:AccountType):
        self.config = Authr.auth_config
        self.user_id = user_id
        self.account_type = account_type
        print("Authr init")

    def get_token(self) -> str:
        pass
    
    def _get_refresh_token_cached(self):
        return Authr.cachr.get_refresh_token(self.user_id, self.account_type)
    
    def _persist_refresh_token(self, refresh_token:str) -> None:
        Authr.cachr.persist_refresh_token(self.user_id, self.account_type, refresh_token)


class GoogleAuthr(Authr):
    def __init__(self, user_id, account_type):
        super().__init__(user_id, account_type)
        self.config = self.config['google_auth']
        print("GoogleAuthr init")

    def get_token(self) -> str:
        cached_refresh_token = self._get_refresh_token_cached()
        if cached_refresh_token is not None:
            return self._get_token_from_refresh(cached_refresh_token)
        else:
            return self._get_new_token()

    def _get_token_from_refresh(self, refresh_token:str) -> str:
        print("Found refresh, trying to use it.")
        request_body = {
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret'],
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        response = requests.post(url=self.config['token_url'], data=request_body)
        if response.status_code == 200:
            print('Success: ' + response.text)
            result = json.loads(response.text)
            return result['access_token']
        else:
            print('Error getting access token using refresh: ' + response.content)
        return None

    def _get_new_token(self):
        flask_app = Flask(__name__)
        flask_app.add_url_rule('/', '/', self)
        webbrowser.open_new_tab(self._build_auth_code_url())
        flask_app.run()
        print("Back to obj with auth code: " + self.auth_code)
        return self._get_new_token_from_code()

    def _get_new_token_from_code(self):
        request_body = {
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret'],
            'code': self.auth_code,
            'redirect_uri': self.config['redirect_uri'],
            'grant_type': self.config['grant_type']
        }
        print("Sending request to " + self.config['token_url'] + " with data: " + str(request_body))
        response = requests.post(url=self.config['token_url'], data=request_body)
        if response.status_code == 200:
            print("Success: " + response.text)
            json_data = json.loads(response.text)
            self._persist_refresh_token(json_data['refresh_token'])
            # Or do i need "id_token" here?
            return json_data['access_token']
        else:
            print("Got token error" + str(response.content))

    def _build_auth_code_url(self):
        auth_url_format = "{}?client_id={}&response_type={}&scope={}&access_type={}&redirect_uri={}&login_hint={}"
        return auth_url_format.format(self.config['auth_url'], self.config['client_id'], self.config['response_type'], self.config['scope'], self.config['access_type'], self.config['redirect_uri'], self.user_id)

    # Receive auth code
    def __call__(self):
        self.auth_code = request.args.get('code')
        print('Got auth code: {}'.format(str(self.auth_code)))

        # TODO(@nzar): implement error param handler
        shutdown_hook = request.environ.get('werkzeug.server.shutdown')
        if shutdown_hook is not None:
            shutdown_hook()
        return Response(status=200, headers={})

    # def _save_refresh_token(self, user_email:str, refresh_token:str) -> None:
    #     with open('./' + user_email + '.refresh', 'w') as refresh_file:
    #         refresh_file.write(refresh_token)

class AuthrFactory(object):
    @staticmethod
    def get_authr(user_id:str, account_type:AccountType) -> Authr:
        if account_type == AccountType.GOOGLE:
            return GoogleAuthr(user_id, account_type)