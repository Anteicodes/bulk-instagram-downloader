from os.path import dirname
import os
from .post_bulk import BulkDownloader
import argparse

argument = argparse.ArgumentParser(prog=f"python3 -m {dirname(__file__).split('/')[-1]}", description="IG BULKDOWNLOADER")
argument.add_argument("--username", help="Username Account")
argument.add_argument("--password", help="Password Account")
argument.add_argument("--token", help="Cookie File with Netscape Format")
argument.add_argument("--max", help="Maximum take media from posts, default 20")
argument.add_argument("--type", help="Bulk type e.g: post, ")
argument.add_argument("--worker", help="default 3")
parse = argument.parse_args()
if parse.worker:
    if parse.worker.isnumeric():
        worker = int(parse.worker)
    else:
        worker = 3
else:
    worker = 3
if parse.type == 'post':
    if parse.token:
        bulk=BulkDownloader(cookie_path=parse.token)
        bulk.downloadAllPost(parse.max if parse.max else 20,worker)
    elif parse.username and parse.password:
        bulk = BulkDownloader(parse.username, parse.password)
        bulk.downloadAllPost(parse.max if parse.max else 20, worker)
    else:
        os.system(f"python3 -m {dirname(__file__).split('/')[-1]} --help")
else:
    os.system(f"python3 -m {dirname(__file__).split('/')[-1]} --help")
