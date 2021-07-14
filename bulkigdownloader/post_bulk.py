from typing import Union
from .utility import createFolder, FindUsernameById
from sys import stdout
from instatools3 import igdownload
from concurrent.futures import ThreadPoolExecutor
from igramscraper.instagram import Instagram
from requests import get

class BulkDownloader:
    def __init__(self,username="",password="", cookie_path:Union[str, bool]=False) -> None:
        self.instagram = Instagram()
        if isinstance(cookie_path, str):
            self.instagram.set_cookies(cookie_path)
            try:
                self.instagram.session_username = self.instagram.get_account_by_id(self.instagram.user_session['ds_user_id']).username
            except Exception as e:
                self.instagram.session_username = FindUsernameById(self.instagram.user_session['ds_user_id']).with_commentpicker
        else:
            self.instagram.with_credentials(username, password)
            self.instagram.login()

    def downloadAllPost(self, worker:int):
        headers = self.instagram.generate_headers(self.instagram.user_session)
        with ThreadPoolExecutor(max_workers=worker) as kuli :
            for index,i in enumerate(self.getAllPost, 1):
                stdout.write(f"\rDownload Media From {list(i)[0]} => {index}          ")
                kuli.submit(self.bulkPostDownloadFile, i, headers).result()
                stdout.flush()
        return True

    @property
    def get_all_following(self):
        following=self.instagram.get_following(self.instagram.user_session["ds_user_id"])["accounts"]
        return following

    @property
    def getAllPost(self)->dict:
        for user in self.get_all_following:
            all_post = self.instagram.get_medias_by_user_id(user.identifier)
            for index, i in enumerate(all_post, 1):
                stdout.write(f"\rScrapping from {user.username} => {index}/{len(all_post)} post {round((index/all_post.__len__())*100)}%            ")
                res=igdownload(i.link, self.instagram.generate_headers(self.instagram.user_session))
                res.update({"created_at":i.created_time})
                stdout.flush()
                yield {user.username:res}

    def bulkPostDownloadFile(self, allUserObject, headers):
        username = list(allUserObject)[0]
        for directory in [self.instagram.session_username, f"{self.instagram.session_username}/{username}", f"{self.instagram.session_username}/{username}/Photos", f"{self.instagram.session_username}/{username}/Videos"]:
            createFolder(directory)
        for index, media in enumerate(allUserObject[username]['result'], 1):
                stdout.write(f"\r Writing File      {index}/{allUserObject[username]['result'].__len__()}                     ")
                open(f"{self.instagram.session_username}/{username}/{['Videos','Photos'][media['type'] == 'image']}/{allUserObject[username]['created_at']}-{index}.{['mp4', 'jpg'][media['type'] == 'image'] }", "wb").write(get(media['url'], headers=headers).content)
                stdout.flush()
        