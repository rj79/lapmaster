import unittest
import os
from db_utils import Uploader

TEST_FILE_NAME = '/tmp/db_utils_unittest.csv'

class TestFile:
    def __init__(self, filename):
        self.FileName = filename
        with open(self.FileName, 'w'):
            pass

    def writeline(self, text):
        with open(self.FileName, 'a') as f:
            f.write(text + os.linesep)

    def __str__(self):
        text = ""
        for line in open(self.FileName, 'r'):
            text += line
        return text


class FakeDB:
    def __init__(self):
        self.Data = ""

    def UploadData(self, data):
        self.Data = data
        return {"deleted": 0, "added": [{"bib": 101, "passage": 59}], "messages": []}


class TestDbUpload(unittest.TestCase):
    def setUp(self):
        self.File = TestFile(TEST_FILE_NAME)
        
    def tearDown(self):
        os.unlink(TEST_FILE_NAME)

    def test_simple(self):
        self.File.writeline('1408987100.0,start all');
        self.File.writeline('1408987200.0,101');
        self.File.writeline('1408987300.0,102');
        db = FakeDB()
        uploader = Uploader(db, TEST_FILE_NAME, 10)
        uploader._upload()
        self.assertEqual("1408987100\tall\n" + 
                         "1408987200\t101\n" + 
                         "1408987300\t102",
                         db.Data)

    def test_missing_bib(self):
        self.File.writeline('1408987100.0,start all');
        self.File.writeline('1408987200.0,101');
        self.File.writeline('1408987300.0,!!!!');
        self.File.writeline('1408987400.0,102');
        db = FakeDB()
        uploader = Uploader(db, TEST_FILE_NAME, 10)
        uploader._upload()
        self.assertEqual("1408987100\tall\n" + 
                         "1408987200\t101\n" + 
                         "1408987400\t102",
                         db.Data)
