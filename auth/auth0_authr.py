import logging
import requests
import yaml
import webbrowser
import json
from datetime import datetime, timedelta
from auth.authr import Authr
from flask import Flask, request, Response
from globals import AccountType, AppLoggerName

logger = logging.getLogger(AppLoggerName)


class Auth0Authr(Authr):
    auth0_flask_app = Flask(__name__)

    def __init__(self):
        super().__init__(AccountType.AUTH0)
        self.config = Auth0Authr.auth_config['auth0']
        logger.debug("Auth0Authr")
    

    def _get_new_token(self, user_id:str = None) -> str:
        logger.debug("Getting new Auth0 token")
        # Receive auth code
        @Auth0Authr.auth0_flask_app.route('/')
        def receive_auth_code():
            self.auth_code = request.args.get('code')
            logger.debug('Got auth code: {}'.format(str(self.auth_code)))

            # TODO(@nzar): implement error param handler
            shutdown_hook = request.environ.get('werkzeug.server.shutdown')
            if shutdown_hook is not None:
                shutdown_hook()
                logger.debug("Called shutdown hook on auth0 authr")
            else:
                logger.error("Failed to call shutdown hook on auth0 authr")
            return Response(status=200, headers={})
        # flask_app.add_url_rule('/', '/', self)
        webbrowser.open_new_tab(self._build_auth_code_url())
        Auth0Authr.auth0_flask_app.run()
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
        logger.debug('Sending request to: ' + self.config['token_url'])
        response = requests.post(url = self.config['token_url'], data = request_body)
        if response.status_code == 200:
            logger.debug('Auth0 success token response')
            json_data = json.loads(response.text)
            expiry_dttm = datetime.now() + timedelta(seconds=json_data['expires_in'])
            user_id = self._get_field_from_id_token(json_data['id_token'], 'email')
            return user_id, json_data['access_token'], expiry_dttm, json_data['refresh_token']
        else:
            logger.error('Auth0 failed token request: ' + response.content)
        return (None, None, None, None)

    def _build_auth_code_url(self) -> str:
        auth_url_format = "{}?client_id={}&response_type={}&redirect_uri={}&scope={}"
        auth_url = auth_url_format.format(
            self.config['auth_url'],
            self.config['client_id'],
            self.config['response_type'],
            self.config['redirect_uri'],
            self.config['scope'])
        logger.debug("Auth code url: " + auth_url)
        return auth_url
    







