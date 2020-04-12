import yaml
from auth_handler import auth_handler
from photo_handler import PhotoHandler

with open('config/auth_config.yaml', 'r') as auth_config_file:
    auth_config = yaml.load(auth_config_file, Loader=yaml.FullLoader)

access_token = auth_handler(auth_config['google_auth']).get_token(auth_config['accounts'][0])
print('In main, with token: ' + access_token)

with open('config/photo_config.yaml', 'r') as photo_config_file:
    photo_config = yaml.load(photo_config_file, Loader=yaml.FullLoader)

PhotoHandler(photo_config, access_token, None).list_photos_in_source()