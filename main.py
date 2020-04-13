import os
import logging
import yaml
from photo_handler import PhotoHandler
from auth.authr_factory import AuthrFactory
from globals import AccountType, AppLoggerName

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(AppLoggerName)

logger.debug("Starting.")

# google_authr = AuthrFactory.get_authr(AccountType.GOOGLE)
# access_token = google_authr.get_access_token('sprnkleruser1@gmail.com')


auth0authr = AuthrFactory.get_authr(AccountType.AUTH0)
access_token = auth0authr.get_access_token()

logger.debug('In main, with token: ' + access_token)

# with open('config/photo_config.yaml', 'r') as photo_config_file:
#     photo_config = yaml.load(photo_config_file, Loader=yaml.FullLoader)

# PhotoHandler(photo_config, access_token, None).list_photos_in_source()

logger.info("Script completed without error.")