import bulkigdownloader
from bulkigdownloader.post_bulk import BulkDownloader
import unittest
import os
class testIgeh(unittest.TestCase):
    def test_import(self):
        from bulkigdownloader import BulkDownloader
    def test_bulk(self):
        """BulkDownloader(cookie_path="sessions/instagram.com_cookies.txt").downloadAllPost(10)"""
        #gk jadi hampir kena ban
        pass

if __name__ == '__main__':
    unittest.main()