from sys import exit
from os import remove
from os.path import isfile
import pickle
from typing import Union
from .utility import createFolder, FindUsernameById, get_user_alternative
from sys import stdout
from instatools3 import igdownload
from concurrent.futures import ThreadPoolExecutor
from .igramscraper.instagram import Instagram
from requests import get


class BulkDownloader:
    def __init__(self,username="",password="", cookie_path:Union[str, bool]=False, alternative:bool=False) -> None:
        self.instagram = Instagram()
        self.alternative = alternative
        if isinstance(cookie_path, str):
            self.instagram.set_cookies(cookie_path)
            try:
                self.instagram.session_username = self.instagram.get_account_by_id(self.instagram.user_session['ds_user_id']).username
            except Exception as e:
                self.instagram.session_username = FindUsernameById(self.instagram.user_session['ds_user_id']).with_commentpicker
        else:
            self.instagram.with_credentials(username, password)
            self.instagram.login()
        self.userinfo = get_user_alternative(self.instagram.session_username).api() if alternative else self.instagram.get_account_by_id(self.instagram.user_session['ds_user_id'])

    def downloadAllPost(self, max:Union[bool, int]=20, worker:Union[int]=4, selected_user=[]):
        headers = self.instagram.generate_headers(self.instagram.user_session)
        with ThreadPoolExecutor(max_workers=int(worker)) as kuli :
            for index,i in enumerate(self.getAllPost(max, selected_user=selected_user), 1):
                stdout.write(f"\rDownload Media From {list(i)[0]} => {index}          ")
                kuli.submit(self.bulkPostDownloadFile, i, headers).result()
                stdout.flush()
        return True

    @property
    def get_all_following(self):
        following=self.instagram.get_following(self.userinfo.identifier, self.userinfo.follows_count, self.userinfo.follows_count)['accounts']
        return following

    def getAllPost(self, max, selected_user:list)->dict:
        account_list:list = []
        all_post:list = []
        index:int = 0
        u_index:int = 0
        user = None
        restore = False
        if isfile("backup"):
            while True:
                rest = input("continue the previous task [Y/N/C/D]: ")
                if rest.lower() == "y":
                    restore = True
                    break
                elif rest.lower() == "n":
                    restore = False
                    break
                elif rest.lower() == "c":
                    exit(1)
                elif rest.lower() == "d":
                    remove('backup')
                    exit(1)
        if restore:
            fileb = pickle.loads(open("backup","rb").read())
            account_list = fileb["account_list"]
            for user in fileb["all_post"].keys():
                all_post = fileb["all_post"][user]
                for index, i in enumerate(all_post, 1):
                    try:
                        stdout.write(f"\rScrapping from {user.username} => {index}/{len(all_post)} post {round((index/all_post.__len__())*100)}%            ")
                        res=igdownload(i.link if i.link[-1] == "/" else i.link+"/", self.instagram.generate_headers(self.instagram.user_session))
                        if not res["status"]:
                            res = igdownload(i.link, self.instagram.generate_headers(self.instagram.user_session))
                            if not res["status"]:
                                res["result"] = []
                        res.update({"created_at":i.created_time})
                        stdout.flush()
                        yield {user.username:res}
                    except Exception as e:
                        print(e)
                        open("backup","wb").write(pickle.dumps({"account_list":account_list[u_index:], "all_post":{user:all_post[index-1:]} if user else {}}))
                        exit(1)
            for u_index, user in enumerate(account_list, 1):
                all_post = self.instagram.get_medias_by_user_id(user.identifier, int(max) if type(max) == str and max.isnumeric() else user.media_count)
                for index, i in enumerate(all_post, 1):
                    try:
                        stdout.write(f"\rScrapping from {user.username} => {index}/{len(all_post)} post {round((index/all_post.__len__())*100)}%            ")
                        res=igdownload(i.link if i.link[-1] == "/" else i.link+"/", self.instagram.generate_headers(self.instagram.user_session))
                        if not res["status"]:
                            res = igdownload(i.link, self.instagram.generate_headers(self.instagram.user_session))
                            if not res["status"]:
                                res["result"] = []
                        res.update({"created_at":i.created_time})
                        stdout.flush()
                        yield {user.username:res}
                    except Exception as e:
                        print(e)
                        open("backup","wb").write(pickle.dumps({"account_list":account_list[u_index:], "all_post":{user:all_post[index-1:]} if user else {}}))
                        exit(1)
        else:
            if selected_user:
                for i in selected_user:
                    account_list.append( get_user_alternative(i).api() if self.alternative else self.instagram.get_account(i))
            else:
                account_list = self.get_all_following
            for u_index, user in enumerate(account_list, 1):
                all_post = self.instagram.get_medias_by_user_id(user.identifier, int(max) if type(max) == str and max.isnumeric() else user.media_count)
                for index, i in enumerate(all_post, 1):
                    try:
                        stdout.write(f"\rScrapping from {user.username} => {index}/{len(all_post)} post {round((index/all_post.__len__())*100)}%            ")
                        res=igdownload(i.link if i.link[-1] == "/" else i.link+"/", self.instagram.generate_headers(self.instagram.user_session))
                        if not res["status"]:
                            res = igdownload(i.link, self.instagram.generate_headers(self.instagram.user_session))
                            if not res["status"]:
                                res["result"] = []
                        res.update({"created_at":i.created_time})
                        stdout.flush()
                        yield {user.username:res}
                    except Exception as e:
                        open("backup","wb").write(pickle.dumps({"account_list":account_list[u_index:], "all_post":{user:all_post[index-1:]} if user else {}}))
                        print(e)
                        exit(1)

    def bulkPostDownloadFile(self, allUserObject, headers):
        username = list(allUserObject)[0]
        for directory in [self.instagram.session_username, f"{self.instagram.session_username}/{username}", f"{self.instagram.session_username}/{username}/Photos", f"{self.instagram.session_username}/{username}/Videos"]:
            createFolder(directory)
        for index, media in enumerate(allUserObject[username]['result'], 1):
                stdout.write(f"\r Writing File      {index}/{allUserObject[username]['result'].__len__()}                     ")
                open(f"{self.instagram.session_username}/{username}/{['Videos','Photos'][media['type'] == 'image']}/{allUserObject[username]['created_at']}-{index}.{['mp4', 'jpg'][media['type'] == 'image'] }", "wb").write(get(media['url'], headers=headers).content)
                stdout.flush()
        
