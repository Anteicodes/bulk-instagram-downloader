from sys import stdout
import os
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
        all_post = self.getAllPost
        with ThreadPoolExecutor(max_workers=worker) as kuli :
            for index, i in enumerate(all_post.keys(), 1):
                stdout.write(f"\rDownload all media => {index}/{all_post.__len__()} post {round((index/all_post.__len__())*100)}%                ")
                self.bulkPostDownloadFile(kuli.submit(User,{i:all_post[i]}, self.instagram).result())
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
            post = {user.username:[]}
            all_post = self.instagram.get_medias_by_user_id(user.identifier)
            for index, i in enumerate(all_post, 1):
                stdout.write(f"\rScrapping from {user.username} => {index}/{len(all_post)} post {round((index/all_post.__len__())*100)}%            ")
                res=igdownload(i.link, self.instagram.generate_headers(self.instagram.user_session))
                res.update({"created_at":i.created_time})
                post[user.username].append(res)
                stdout.flush()
            data.update(post)
        return data
    def bulkPostDownloadFile(self, allUserObject):
        if not os.path.isdir(self.instagram.session_username):
            stdout.write(f"\rCreating Folder {self.instagram.session_username}          ")
            os.mkdir(self.instagram.session_username)
            stdout.flush()
        if not os.path.isdir(f"{self.instagram.session_username}/{allUserObject.username}"):
            stdout.write(f"\rCreating Folder {allUserObject.username}                    ")
            os.mkdir(f"{self.instagram.session_username}/{allUserObject.username}")
            stdout.flush()
        if not os.path.isdir(f"{self.instagram.session_username}/{allUserObject.username}/post"):
            os.mkdir(f"{self.instagram.session_username}/{allUserObject.username}/post")
        for post in allUserObject.post:
            if os.path.isdir(f"{self.instagram.session_username}/{allUserObject.username}/post/{post.created}"):
                True
            else:
                stdout.write(f"\rCreating Folder {post.created}             ")
                os.mkdir(f"{self.instagram.session_username}/{allUserObject.username}/post/{post.created}")
                stdout.flush()
            for index, media in enumerate(post.media, 1):
                stdout.write(f"\r Writing File      {index}/{post.media.__len__()}                     ")
                open(f"{self.instagram.session_username}/{allUserObject.username}/post/{post.created}/{index}.{['mp4','jpg'][media.type == 'image']}", "wb").write(media.binary)
                stdout.flush()
        
class User:
    def __init__(self, data:dict, instagram) -> None:
        self.username = list(data)[0]
        self.post    = [Post(i, instagram) for i in data[list(data)[0]]]

class Media:
    def __init__(self, data:dict, instagram) -> None:
        self.binary:bytes = download(data["url"], instagram)
        self.type = data["type"]
class Post:
    def __init__(self, data:dict, instagram) -> None:
        self.created:int = data["created_at"]
        self.media = [Media(i, instagram) for i in data["result"]]
def download(url:str, instagram)->bytes:
    return get(url, headers=instagram.generate_headers(instagram.user_session)).content