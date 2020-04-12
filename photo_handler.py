import requests
import json

class PhotoHandler(object):

    def __init__(self, config:dict, src_access_token:str, dest_access_token:str):
        self.config = config
        self.src_access_token = src_access_token
    
    def list_photos_in_source(self):
        next_page_token = None
        while True:
            curr_url = self.config['list_photos_url']
            if next_page_token is not None:
                curr_url += "?pageToken=" + next_page_token
            print("curr url: " + curr_url)
            page_response = requests.get(curr_url, headers={'Content-type': 'application/json', 'Authorization': 'Bearer ' + self.src_access_token})
            if page_response.status_code == 200:
                print("sucess getting page")
                page_data = json.loads(page_response.text)
                print('Photos: ' + str(page_data['mediaItems']))
                
                if 'nextPageToken' in page_data:
                    next_page_token = page_data['nextPageToken']
                else:
                    break
            else:
                print('error getting page: ' + page_response.content)
    
    def list_photos_in_dest(self):
        pass

    def copy_photo_to_dest(self):
        pass
    