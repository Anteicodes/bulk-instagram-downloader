import requests
import os
import sys
def createFolder(path):
    if not os.path.isdir(path):
        sys.stdout.write(f"\rCreating Folder {os.path.dirname(path)}           ")
        os.mkdir(path)
        sys.stdout.flush()
class FindUsernameById:
    def __init__(self, id) -> None:
        self.id = id
    @property
    def with_commentpicker(self):
        request = requests.Session()
        request.headers = {'referer': 'https://commentpicker.com/instagram-username.php','sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"','sec-ch-ua-mobile': '?0','sec-fetch-dest': 'empty','sec-fetch-mode': 'cors','sec-fetch-site': 'same-origin','user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}
        token = request.get("https://commentpicker.com/actions/token.php").text
        return request.get("https://commentpicker.com/actions/find-insta-username.php?userid=44940697347&token=5df8b6f93cf24c3c37498be5976a57e6aac95a7f465ad3dedb2469a05d7810db", params={"user_id":self.id, "token":token}).json().get("username")