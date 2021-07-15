from http.cookiejar import LoadError
from os.path import dirname
import os
from .post_bulk import BulkDownloader
import argparse
from .igramscraper.exception.instagram_auth_exception import InstagramAuthException
argument = argparse.ArgumentParser(prog=f"python3 -m {dirname(__file__).split('/')[-1]}", description="IG BULKDOWNLOADER")
argument.add_argument("--username", help="Username Account", type=str)
argument.add_argument("--password", help="Password Account", type=str)
argument.add_argument("--token", help="Cookie File with Netscape Format", type=str)
argument.add_argument("--max", help="Maximum take media from posts, default 20")
argument.add_argument("--type", help="Bulk type e.g: post, ", type=str)
argument.add_argument("--worker", help="default 3", type=int)
argument.add_argument("--alternative", help="alternative method, default False", type=bool, default=False)
argument.add_argument("--mark", help="with spesific list account use , for sparate", type=str)
parse = argument.parse_args()
BulkOptions = {"alternative":parse.alternative}
DownloadOptions = {"selected_user":parse.mark.split(",") if parse.mark else []}
if parse.worker:
    if parse.worker.isnumeric():
        worker = int(parse.worker)
    else:
        worker = 3
else:
    worker = 3
if parse.type == 'post':
    try:
        if parse.token:
            bulk=BulkDownloader(cookie_path=parse.token, **BulkOptions)
            bulk.downloadAllPost(parse.max if parse.max else 20,worker, **DownloadOptions)
        elif parse.username and parse.password:
            bulk = BulkDownloader(parse.username, parse.password, **BulkOptions)
            bulk.downloadAllPost(parse.max if parse.max else 20, worker, **DownloadOptions)
        else:
            os.system(f"python3 -m {dirname(__file__).split('/')[-1]} --help")
    except InstagramAuthException:
        print("Login Failed")
    except FileNotFoundError:
        print(f"'{parse.token}' File Not Found")
    except LoadError:
        print(f"'{parse.token}' does not look like a Netscape format cookies file")

else:
    os.system(f"python3 -m {dirname(__file__).split('/')[-1]} --help")
