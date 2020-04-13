from globals import AccountType
from auth.auth0_authr import Auth0Authr
from auth.google_authr import GoogleAuthr
from auth.authr import Authr 

class AuthrFactory(object):
    @staticmethod
    def get_authr(account_type:AccountType) -> Authr:
        if account_type == AccountType.GOOGLE:
            return GoogleAuthr()
        elif account_type == AccountType.AUTH0:
            return Auth0Authr()