import os
import sys
def createFolder(path):
    if not os.path.isdir(path):
        sys.stdout.write(f"\rCreating Folder {os.path.dirname(path)}           ")
        os.mkdir(path)
        sys.stdout.flush()
