import os
import yaml
import base64
import webbrowser
import requests
import json
from flask import Flask, request, Response

class auth_handler(object):
    def __init__(self, auth_config:dict):
        self.config = auth_config
        self.flask_app = Flask(__name__)
        self.flask_app.add_url_rule('/', '/', self)
        self.auth_code = ""

    def get_token(self, user_email:str) -> str:
        if os.path.exists('./' + user_email + ".refresh"):
            with open('./' + user_email + ".refresh") as refresh_file:
                return self._get_token_from_refresh(user_email, refresh_file.read())
        else:
            return self._get_new_token(user_email)
                
    def _get_token_from_refresh(self, user_email:str, refresh_token:str) -> str:
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

    def _get_new_token(self, user_email:str):
        webbrowser.open_new_tab(self._build_auth_code_url(user_email))
        self.flask_app.run()
        print("Back to obj with auth code: " + self.auth_code)
        return self._get_new_token_from_code(user_email)
    
    def _get_new_token_from_code(self, user_email:str):
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
            self._save_refresh_token(user_email, json_data['refresh_token'])
            # Or do i need "id_token" here?
            return json_data['access_token']
        else:
            print("Got token error" + str(response.content))

    def _build_auth_code_url(self, user_email):
        auth_url_format = "{}?client_id={}&response_type={}&scope={}&access_type={}&redirect_uri={}&login_hint={}"
        return auth_url_format.format(self.config['auth_url'], self.config['client_id'], self.config['response_type'], self.config['scope'], self.config['access_type'], self.config['redirect_uri'], user_email)

    # Receive auth code
    def __call__(self):
        self.auth_code = request.args.get('code')
        print('Got auth code: {}'.format(str(self.auth_code)))

        # TODO(@nzar): implement error param handler
        shutdown_hook = request.environ.get('werkzeug.server.shutdown')
        if shutdown_hook is not None:
            shutdown_hook()
        return Response(status=200, headers={})
    
    def _save_refresh_token(self, user_email:str, refresh_token:str) -> None:
        with open('./' + user_email + '.refresh', 'w') as refresh_file:
            refresh_file.write(refresh_token)
