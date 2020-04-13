import logging
import yaml
from photo_handler import PhotoHandler
from auth.authr import AuthrFactory
from globals import AccountType, AppLoggerName

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(AppLoggerName)

logger.debug("Starting.")

authr = AuthrFactory.get_authr('sprnkleruser1@gmail.com', AccountType.GOOGLE)

access_token = authr.get_access_token()
logger.debug('In main, with token: ' + access_token)

with open('config/photo_config.yaml', 'r') as photo_config_file:
    photo_config = yaml.load(photo_config_file, Loader=yaml.FullLoader)

PhotoHandler(photo_config, access_token, None).list_photos_in_source()

logger.info("Script completed without error.")