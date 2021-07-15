from typing import Union
import requests
import os
import sys

from requests.api import head
from .igramscraper.model.account import Account
def createFolder(path):
    if not os.path.isdir(path):
        sys.stdout.write(f"\rCreating Folder {os.path.dirname(path)}           ")
        os.mkdir(path)
        sys.stdout.flush()
class get_user_alternative():
    def __init__(self, username:str, trial:int=3) -> None:
        self.username = username
        self.proxy = {}
        self.trial = trial
    def api(self, headers={"User-Agent":"Chromium"},**options)->Union[Account, bool]:
        for i in range(self.trial):
            try:
                x=requests.get(f'https://www.instagram.com/{self.username}/?__a=1', headers=headers, **options).json()
                user=Account()
                user_s = x["graphql"]["user"]
                user.identifier = user_s["id"]
                user.username = user_s["username"]
                user.full_name = user_s["full_name"]
                user.profile_pic_url = user_s["profile_pic_url"]
                user.profile_pic_url_hd = user_s["profile_pic_url_hd"]
                user.biography = user_s["biography"]
                user.follows_count = user_s["edge_follow"]['count']
                user.followed_by_count = user_s['edge_followed_by']['count']
                user.highlight_reel_count = user_s["highlight_reel_count"]
                user.media_count = user_s["edge_owner_to_timeline_media"]['count']
                return user
            except Exception:
                print('\r[?] Parse json Error')
                continue
        print('\r[x] Your Ip is Blocked ')
        return False

class FindUsernameById:
    def __init__(self, id) -> None:
        self.id = id
    @property
    def with_commentpicker(self):
        request = requests.Session()
        request.headers = {'referer': 'https://commentpicker.com/instagram-username.php','sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"','sec-ch-ua-mobile': '?0','sec-fetch-dest': 'empty','sec-fetch-mode': 'cors','sec-fetch-site': 'same-origin','user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}
        token = request.get("https://commentpicker.com/actions/token.php").text
        return request.get("https://commentpicker.com/actions/find-insta-username.php?userid=44940697347&token=5df8b6f93cf24c3c37498be5976a57e6aac95a7f465ad3dedb2469a05d7810db", params={"user_id":self.id, "token":token}).json().get("username")