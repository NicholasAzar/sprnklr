import logging
import requests
import json
from globals import AppLoggerName
from datetime import datetime

logger = logging.getLogger(AppLoggerName)

class PhotoHandler(object):

    def __init__(self, config:dict, src_access_token:str):
        self.config = config
        self.src_access_token = src_access_token
    
    def list_photos_in_source(self):
        logger.info("Listing photos from source")
        next_page_token = None
        photos = []
        while True:
            curr_url = self.config['list_photos_url']
            if next_page_token is not None:
                curr_url += "?pageToken=" + next_page_token
            logger.debug("Using url: " + curr_url)
            page_response = requests.get(curr_url, headers={'Content-type': 'application/json', 'Authorization': 'Bearer ' + self.src_access_token})
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