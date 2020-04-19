import logging
from globals import AccountType, AppLoggerName
from auth.auth_store import AuthStore

logger = logging.getLogger(AppLoggerName)

class Accounts(object):

    def __init__(self):
        super().__init__()
        self.store = AuthStore()

    def add_linked_account(self, sprnklr_id:str, tpy_user_id:str, tpy_acc_type:AccountType, alloc_percentage:float, active_flg:bool, is_primary: bool):
        self.store.add_linked_account(sprnklr_id, tpy_user_id, tpy_acc_type, alloc_percentage, active_flg, is_primary)
    
    def get_linked_accounts(self, sprnklr_id:str):
        linked_accounts = self.store.get_linked_accounts(sprnklr_id)
        logger.debug("Got linked accounts: " + str(linked_accounts))
        return linked_accounts
    
    def set_primary_account(self, sprnklr_id:str, tpy_user_id:str):
        self.store.set_is_primary(sprnklr_id, tpy_user_id)
    


