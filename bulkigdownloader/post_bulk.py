from .utility import createFolder
from sys import stdout
from instatools3 import igdownload
from concurrent.futures import ThreadPoolExecutor
from igramscraper.instagram import Instagram
from requests import get

class BulkDownloader:
    def __init__(self,username,password) -> None:
        self.instagram = Instagram()
        self.instagram.with_credentials(username, password)
        self.instagram.login()

    def downloadAllPost(self, worker:int):
        headers = self.instagram.generate_headers(self.instagram.user_session)
        with ThreadPoolExecutor(max_workers=worker) as kuli :
            for index,i in enumerate(self.getAllPost, 1):
                stdout.write(f"\rDownload Media From {list(i)[0]} => {index}          ")
                kuli.submit(self.bulkPostDownloadFile, i, headers)
                stdout.flush()
        return True

    @property
    def get_all_following(self):
        following=self.instagram.get_following(self.instagram.user_session["ds_user_id"])["accounts"]
        return following

    @property
    def getAllPost(self)->dict:
        data = {}
        for user in self.get_all_following:
            all_post = self.instagram.get_medias_by_user_id(user.identifier)
            for index, i in enumerate(all_post, 1):
                stdout.write(f"\rScrapping from {user.username} => {index}/{len(all_post)} post {round((index/all_post.__len__())*100)}%            ")
                res=igdownload(i.link, self.instagram.generate_headers(self.instagram.user_session))
                res.update({"created_at":i.created_time})
                stdout.flush()
                yield {user.username:res}
        return data

    def bulkPostDownloadFile(self, allUserObject, headers):
        for directory in [self.instagram.session_username, f"{self.instagram.session_username}/{allUserObject.username}", f"{self.instagram.session_username}/{allUserObject.username}/Photos", f"{self.instagram.session_username}/{allUserObject.username}/Videos"]:
            createFolder(directory)
        for post in allUserObject.keys():
            for index, media in enumerate(allUserObject[post]['result'], 1):
                stdout.write(f"\r Writing File      {index}/{allUserObject[post]['result'].__len__()}                     ")
                open(f"{self.instagram.session_username}/{allUserObject.username}/{['Videos','Photos'][media['type'] == 'image']}/{post['created_at']}-{index}.{['mp4', 'jpg'][media['type'] == 'image'] }", "wb").write(get(media['url'], headers=headers).content)
                stdout.flush()
        