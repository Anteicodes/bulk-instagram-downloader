import bulkigdownloader
from bulkigdownloader.post_bulk import BulkDownloader
import unittest
import os
class testIgeh(unittest.TestCase):
    def test_import(self):
        from bulkigdownloader import BulkDownloader
    def test_bulk(self):
        username = os.environ.get("username")
        password = os.environ.get("password")
        if username and password:
            bulkigdownloader(username, password).downloadAllPost(10)
        print("Test skipped")
if __name__ == '__main__':
    unittest.main()