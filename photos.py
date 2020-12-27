import logging
import requests
import json
from globals import AppLoggerName
from datetime import datetime
import yaml
from accounts import Accounts
from auth.authr_factory import AuthrFactory
from globals import AccountType

logger = logging.getLogger(AppLoggerName)

class Photor(object):
    def get_photos(self, access_token:str):
        pass

    def download_photo_to_tmp(self, access_token:str, photo_id:str):
        pass

class GooglePhotor(Photor):
    # TODO (nzar) Config right now is specific to googs - fix that.
    def get_photos(self, access_token:str):
        next_page_token = None
        photos = []
        while True:
            curr_url = self.config['list_photos_url']
            if next_page_token is not None:
                curr_url += "?pageToken=" + next_page_token
            logger.debug("Using url: " + curr_url)
            page_response = requests.get(curr_url, headers={'Content-type': 'application/json', 'Authorization': 'Bearer ' + access_token})
            if page_response.status_code == 200:
                page_data = json.loads(page_response.text)
                logger.debug('Photos: ' + str(page_data['mediaItems']))
                photos.extend(page_data['mediaItems'])
                
                if 'nextPageToken' in page_data:
                    next_page_token = page_data['nextPageToken']
                else:
                    break
            else:
                logger.error('Failed to get page of photos: ' + page_response.content)
        return photos
    
    def download_photo_to_tmp(self, access_token:str, photo_id:str):
        get_response = requests.get('https://photoslibrary.googleapis.com/v1/mediaItems/' + photo_id, headers={'Authorization': 'Bearer ' + access_token})
        if get_response.status_code == 200:
            logger.debug("Download photo response success" + str(get_response.content))
        else:
            logger.error('Failed to download photo to tmp: ' + str(get_response.content))


class PhotorFactory(object):

    @staticmethod
    def get_photor(acc_type:str):
        if acc_type == AccountType.GOOGLE:
            return GooglePhotor()

class PhotorMaster(object): 
    
    with open('config/photo_config.yaml', 'r') as photo_config_file:
        photo_config = yaml.load(photo_config_file, Loader=yaml.FullLoader)
        logger.debug("Initialized photo config")

    def get_photos(self, link_id:str):
        logger.info("Listing photos for link id: " + link_id)
        account = Accounts().get_account_by_link_id(link_id)
        authr = AuthrFactory.get_authr(account['tpy_acc_type'])
        access_token = authr.get_access_token(account['tpy_user_id'])
        photor = PhotorFactory.get_photor(account['tpy_acc_type'])
        return photor.get_photos(access_token)

    def get_photo(self, link_id:str, photo_id:str):
        logger.info("Listing photos for link id: " + link_id)
        account = Accounts().get_account_by_link_id(link_id)
        authr = AuthrFactory.get_authr(account['tpy_acc_type'])
        access_token = authr.get_access_token(account['tpy_user_id'])
        photor = PhotorFactory.get_photor(account['tpy_acc_type'])
        photor.download_photo_to_tmp(access_token, photo_id)


