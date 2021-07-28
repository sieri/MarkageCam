import json
import os
import time
import unittest
from datetime import datetime

import numpy as np

from Data import DB
from Data.Filters import EqualFilter
from ImgTreatement import DebugDisplay
import cv2 as cv


class DB_load(unittest.TestCase):
    DB_NAME = "test_db.sqlite3"

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        os.remove(self.DB_NAME)

    def test_open_db(self):
        with DB.DbConnector(self.DB_NAME) as db:
            self.assertTrue(os.path.exists(self.DB_NAME), "DB didn't create the file")

    def test_schema(self):
        with DB.DbConnector(self.DB_NAME) as db:
            cur = db.db.cursor()
            for name in DB.tables_names:
                cur.execute("""SELECT sql FROM sqlite_master WHERE name = ?;""", (name,))
                test = cur.fetchall()
                self.assertIn(DB.tables_schemas[name].replace('\n', '\\n').replace(";", ""), str(test[0]))

    def test_insert(self):
        with DB.DbConnector(self.DB_NAME) as db:
            self.fill(db)

    def fill(self, db):
        self.img = np.zeros((255, 255, 3), np.ubyte)
        self.img[120:136, 120:136, :] = np.full((16, 16, 3), 255, np.ubyte)
        self.corrected = self.img.copy()
        self.corrected[120:136, 120:136, :] = np.full((16, 16, 3), 128, np.ubyte)

        self.expected_text = "this is a test"
        self.x = 34
        self.y = 42

        self.time = datetime.now()

        ex = DB.ExpectedText(self.expected_text, self.x, self.y)
        img = DB.BaseImg(img=self.img, time=datetime.now(), expected_text=ex)
        cor = DB.CorrectedImg(img=self.corrected, base_img=img, )

        db.insert(ex)
        db.insert(img)
        db.insert(cor)

        self.assertIsNotNone(ex.id)
        self.assertIsNotNone(img.id)
        self.assertIsNotNone(cor.id)

        return ex, img, cor

    def check_read(self, db, cor):
        db.add_filter(EqualFilter(cor.id, "_id"))
        read_cor = db.read(DB.CorrectedImg)[0]

        self.check_corrected(cor, read_cor)

        return read_cor

    def check_corrected(self, cor, read_cor):
        self.assertIsInstance(read_cor, DB.CorrectedImg)
        self.assertIsInstance(read_cor.base_img, DB.BaseImg)
        self.assertIsInstance(read_cor.base_img.expected_text, DB.ExpectedText)
        self.assertEqual(read_cor.id, cor.id)
        self.assertTrue((read_cor.img == cor.img).all())
        self.assertEqual(read_cor.base_img.id, cor.base_img.id)
        self.assertTrue((read_cor.base_img.img == cor.base_img.img).all())
        self.assertEqual(read_cor.base_img.expected_text.text, cor.base_img.expected_text.text)
        self.assertEqual(read_cor.base_img.expected_text.x_repeats, cor.base_img.expected_text.x_repeats)
        self.assertEqual(read_cor.base_img.expected_text.y_repeats, cor.base_img.expected_text.y_repeats)

    def testRead(self):
        # fill
        with DB.DbConnector(self.DB_NAME) as db:
            ex, img, cor = self.fill(db)

        # close db, then read it again
        with DB.DbConnector(self.DB_NAME) as db:
            read_cor = self.check_read(db, cor)
            self.assertIs(read_cor, cor)
            self.assertIs(read_cor.base_img, img)
            self.assertIs(read_cor.base_img.expected_text, img.expected_text)

        # close the db, clear current data to simulate a reboot
        DB.expected_texts.clear()
        DB.base_imgs.clear()
        DB.corrected_imgs.clear()

        with DB.DbConnector(self.DB_NAME) as db:
            read_cor = self.check_read(db, cor)
            self.assertIsNot(read_cor, cor)
            self.assertIsNot(read_cor.base_img, img)
            self.assertIsNot(read_cor.base_img.expected_text, img.expected_text)

    def testResult(self):
        with DB.DbConnector(self.DB_NAME) as db:
            ex, img, cor = self.fill(db)
            res = DB.Result(corrected_img=cor, accuracy=12, correct=True)
            db.insert(res)
            self.assertIsNotNone(res.id)

        with DB.DbConnector(self.DB_NAME) as db:
            db.add_filter(EqualFilter(res.id, "_id"))
            read_result = db.read(DB.Result)[0]
            self.assertIsNotNone(read_result)
            self.assertIs(read_result, res)


        with DB.DbConnector(self.DB_NAME) as db:
            read_result = db.read(res)[0]
            self.assertIsNotNone(read_result)
            self.assertEqual(read_result.id, res.id)
            self.assertEqual(read_result.accuracy, res.accuracy)
            self.assertEqual(read_result.correct, res.correct)
            self.check_corrected(cor=cor, read_cor=read_result.corrected_img)


if __name__ == '__main__':
    unittest.main()
