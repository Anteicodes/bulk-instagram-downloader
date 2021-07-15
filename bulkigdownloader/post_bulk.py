from sys import exit
from os import remove
from os.path import isfile
import pickle
from typing import Union

import requests
from .utility import createFolder, FindUsernameById, get_user_alternative, download_with_stream, remove_blank
from sys import stdout
from instatools3 import igdownload
from concurrent.futures import ThreadPoolExecutor
from .igramscraper.instagram import Instagram
from requests import get

from bulkigdownloader.igramscraper import instagram


class BulkDownloader:
    def __init__(self,username="",password="", cookie_path:Union[str, bool]=False, alternative:bool=False, instagram=None) -> None:
        self.instagram = Instagram()
        self.alternative = alternative
        if isinstance(cookie_path, str):
            self.instagram.set_cookies(cookie_path)
            try:
                self.instagram.session_username = self.instagram.get_account_by_id(self.instagram.user_session['ds_user_id']).username
            except Exception as e:
                self.instagram.session_username = FindUsernameById(self.instagram.user_session['ds_user_id']).with_commentpicker
        elif username and password:
            self.instagram.with_credentials(username, password)
            self.instagram.login()
        elif instagram:
            self.instagram = instagram
        self.userinfo = get_user_alternative(self.instagram.session_username).api() if alternative else self.instagram.get_account_by_id(self.instagram.user_session['ds_user_id'])
    
    def downloadAllPost(self, max:Union[bool, int]=20, worker:Union[int]=4, selected_user=[]):
        headers = self.instagram.generate_headers(self.instagram.user_session)
        with ThreadPoolExecutor(max_workers=int(worker)) as kuli :
            for index,i in enumerate(self.getAllPost(max, selected_user=selected_user), 1):
                stdout.write(remove_blank(f"\rDownload Media From {list(i)[0]} => {index}"))
                kuli.submit(self.bulkPostDownloadFile, i, headers).result()
                stdout.flush()
        return True

    @property
    def get_all_following(self):
        following=self.instagram.get_following(self.userinfo.identifier, self.userinfo.follows_count, self.userinfo.follows_count)['accounts']
        return following
    def downloadAllHighlight(self, worker:int=3, selected_user:list=[]):
        headers = self.instagram.generate_headers(self.instagram.user_session)
        with ThreadPoolExecutor(max_workers=worker) as pool:
            for index, i in enumerate(self.getAllHighlight(selected_user=selected_user, headers=headers)):
                for post_highlight in i:
                    pool.submit(self.highlightDownloadFile, post_highlight, headers).result()

    def downloadAllStory(self, worker:int=3):
        with ThreadPoolExecutor(max_workers=worker) as gas:
            for index, i in enumerate(self.getAllStory, 1):
                gas.submit(self.downloadStoryFile, i).result()


    @property
    def getAllStory(self):
        for user in self.get_all_following:
            for story in self.instagram.get_stories(user.identifier):
                for index, i in enumerate(story.stories, 1):
                    i.__dict__.update({'created_at': i.created_time})
                    res = {"result": [{"url": i.image_high_resolution_url if i.type == "image" else i.video_standard_resolution_url, "created_at": i.created_time, "type": i.type}]}
                    yield {user.username: res}

    def downloadStoryFile(self, storyObj):
        username = list(storyObj)[0]
        for directory in [self.instagram.session_username, f"{self.instagram.session_username}/{username}", f"{self.instagram.session_username}/{username}/Stories", f"{self.instagram.session_username}/{username}/Stories/Photos", f"{self.instagram.session_username}/{username}/Stories/Videos"]:
            createFolder(directory)
        for index, i in enumerate(storyObj[username]['result'], 1):
            download_with_stream(i["url"], self.instagram.generate_headers(self.instagram.user_session), f"{self.instagram.session_username}/{username}/Stories/{['Photos','Videos'][i['type'] == 'video']}/{i['created_at']}.{['jpg','mp4'][i['type'] == 'video']}", f"From {username}")


    def getAllHighlight(self, selected_user:list, headers:dict):
        all_user = []
        if selected_user:
            for i in selected_user:
                all_user.append(get_user_alternative(i).api() if self.alternative else self.instagram.get_account(i))
        for index, user in enumerate(all_user):
            yield requests.get(f"https://i.instagram.com/api/v1/highlights/{user.identifier}/highlights_tray/", headers=headers).json()["tray"]

    def highlightDownloadFile(self, id:dict, headers:dict):
        requests.options("https://i.instagram.com/api/v1/feed/reels_media/", params={"reel_ids":id['id']}, headers=headers)
        js=requests.get("https://i.instagram.com/api/v1/feed/reels_media/", params={"reel_ids":id['id']}, headers=headers).json()
        for id_highlight in js['reels']:
            username = js['reels'][id_highlight]['user']['username']
            for directory in [self.instagram.session_username, f"{self.instagram.session_username}/{username}", f"{self.instagram.session_username}/{username}/Highlight", f"{self.instagram.session_username}/{username}/Highlight/Photos", f"{self.instagram.session_username}/{username}/Highlight/Videos"]:
                createFolder(directory)
            for index, media in enumerate(js['reels'][id_highlight]['items']): #2:video 1:image
                download_with_stream(media["video_versions"][0]['url'] if media["media_type"] == 2 else media["image_versions2"]['candidates'][0]['url'], headers, f'{self.instagram.session_username}/{username}/Highlight/{["Videos", "Photos"][media["media_type"]==1]}/{js["reels"][id_highlight]["created_at"]}-{index}.{["mp4", "jpg"][media["media_type"]==1]}',f'From {username} ')


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
                        stdout.write(remove_blank(f"\rScrapping from {user.username} => {index}/{len(all_post)} post {round((index/all_post.__len__())*100)}%"))
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
                        stdout.write(remove_blank(f"\rScrapping from {user.username} => {index}/{len(all_post)} post {round((index/all_post.__len__())*100)}%"))
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
                        stdout.write(remove_blank(f"\rScrapping from {user.username} => {index}/{len(all_post)} post {round((index/all_post.__len__())*100)}% "))
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
        for directory in [self.instagram.session_username, f"{self.instagram.session_username}/{username}",f"{self.instagram.session_username}/{username}/Post", f"{self.instagram.session_username}/{username}/Post/Photos", f"{self.instagram.session_username}/{username}/Post/Videos"]:
            createFolder(directory)
        for index, media in enumerate(allUserObject[username]['result'], 1):
                download_with_stream(media['url'], headers, f"{self.instagram.session_username}/{username}/Post/{['Videos','Photos'][media['type'] == 'image']}/{allUserObject[username]['created_at']}-{index}.{['mp4', 'jpg'][media['type'] == 'image'] }", username)
        
