from os import environ as env
import logging
import yaml
import json
import base64
from functools import wraps
from photo_handler import PhotoHandler
from auth.authr_factory import AuthrFactory
from globals import AccountType, AppLoggerName, merge_two_sorted_object_lists
from accounts import Accounts

from werkzeug.exceptions import HTTPException
from flask import Flask, jsonify, redirect, session, url_for

from authlib.integrations.flask_client import OAuth
from auth.auth_store import AuthStore
from datetime import datetime, timedelta

logging.basicConfig(level=env.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(AppLoggerName)

with open('config/auth_config.yaml', 'r') as auth_config_file:
    auth_config = yaml.load(auth_config_file, Loader=yaml.FullLoader)
    auth0_config = auth_config['auth0']
    google_config = auth_config['google']
    logger.debug("Initialized auth config")

app = Flask(__name__)
app.secret_key = 'A secret?'
app.debug = True if env.get('LOGLEVEL') == 'DEBUG' else False

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=auth0_config['client_id'],
    client_secret=auth0_config['client_secret'],
    api_base_url=auth0_config['base_url'],
    access_token_url=auth0_config['base_url'] + '/oauth/token',
    authorize_url=auth0_config['base_url'] + '/authorize',
    client_kwargs={
        'scope': auth0_config['scope']
    }
)

google_auth = oauth.register(
    'google',
    client_id = google_config['client_id'],
    client_secret=google_config['client_secret'],
    api_base_url='https://www.googleapis.com/oauth2/v4/token',
    access_token_url=google_config['token_url'],
    authorize_url=google_config['auth_url'],
    client_kwargs={
        'scope': google_config['scope']
    }
)

@app.errorhandler(Exception)
def handle_auth_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session: # deny
            return redirect('/login')
        return f(*args, **kwargs) # allow
    return decorated

@app.route('/callback-auth0')
def callback_auth0_handler():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    user_info = resp.json()
    session['jwt_payload'] = user_info
    session['profile'] = {
        'user_id': user_info['email'],
        'sub': user_info['sub'],
        'name': user_info['name'],
        'picture': user_info['picture']
    }
    return jsonify(message="Login successful")

@app.route('/callback-google')
@requires_auth
def callback_google_handler():
    result = google_auth.authorize_access_token()
    # Since we don't need any additional user info this is fine for now.
    sprnklr_id = session['profile']['user_id']
    id_token_content = parse_id_token(result['id_token'])
    tpy_user_id = id_token_content['email']
    accounts = Accounts()
    accounts.add_linked_account(sprnklr_id, tpy_user_id, AccountType.GOOGLE, 100.0, True)

    auth_store = AuthStore()
    expiry_dttm = datetime.now() + timedelta(seconds=result['expires_in'])
    auth_store.persist_tokens(tpy_user_id, AccountType.GOOGLE, result['access_token'], expiry_dttm, result['refresh_token'])
    return jsonify(message="Login successful")


@app.route('/login')
def login_handler():
    return auth0.authorize_redirect(redirect_uri=auth0_config['redirect_uri'])


@app.route('/list-accounts')
@requires_auth
def list_accounts_handler():
    sprnklr_id = session['profile']['user_id']
    logger.debug("My user id: " + sprnklr_id)
    linked_accounts = Accounts().get_linked_accounts(sprnklr_id)
    return jsonify(linked_accounts=linked_accounts)

@app.route('/add-google-account')
@requires_auth
def add_account_handler():
    return google_auth.authorize_redirect(redirect_uri=google_config['redirect_uri'])

@app.route('/list-photos')
@requires_auth
def list_photos_handler():
    with open('config/photo_config.yaml', 'r') as photo_config_file:
        photo_config = yaml.load(photo_config_file, Loader=yaml.FullLoader)

    linked_accounts = Accounts().get_linked_accounts(session['profile']['user_id'])

    photos = []
    for account in linked_accounts:
        linked_user_id = account[0]
        linked_acc_type = AccountType(account[1])

        authr = AuthrFactory.get_authr(linked_acc_type)
        access_token = authr.get_access_token(linked_user_id)

        next_set = PhotoHandler(photo_config, access_token).list_photos_in_source()
        photos = merge_two_sorted_object_lists(photos, next_set, lambda photo: datetime.strptime(photo['mediaMetadata']['creationTime'], f"%Y-%m-%dT%H:%M:%SZ"))

    return jsonify(photos=str(photos))


def parse_id_token(id_token:str) -> dict:
    id_token_body = id_token.split('.')[1]
    id_token_body_padded = id_token_body + "=" * (-len(id_token_body) % 4)
    return json.loads(base64.standard_b64decode(id_token_body_padded))


app.run(host='localhost', port=env.get('PORT', 3000))

# sprnklr_id = 'nckazr@gmail.com'
# sprnklr_acc_type = AccountType.AUTH0
# remote_user_id = 'sprnkleruser1@gmail.com'
# remote_acc_type = AccountType.GOOGLE



# google_authr = AuthrFactory.get_authr(AccountType.GOOGLE)
# access_token = google_authr.get_access_token(remote_user_id)

# logger.debug("in main, remote user access token: " + access_token)


# auth0_authr = AuthrFactory.get_authr(AccountType.AUTH0)
# access_token = auth0_authr.get_access_token(sprnklr_id)

# logger.debug('In main, sprnklr user access token: ' + access_token)

# violates unique constraint when rerun.
# accounts.add_linked_account(prime_user_id, prime_acc_type, tpy_user_id, tpy_acc_type, 100.0, True)


logger.info("Script completed without error.")