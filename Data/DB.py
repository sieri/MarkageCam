import os
import sqlite3

import cv2 as cv

from Data import Filters
from Data.Filters import *

from datetime import datetime, timezone

from environement import image_path,debug


tables_names = ["EXPECTED_TEXT", "BASE_IMG", "CORRECTED_IMG"]

tables_schemas = {
    "EXPECTED_TEXT": """(_id INTEGER PRIMARY KEY,
    text TEXT  NOT NULL,
    x_repeats INTEGER NOT NULL,
    y_repeats INTEGER NOT NULL);""",

    "BASE_IMG": """(_id INTEGER PRIMARY KEY,
    img_path TEXT NOT NULL,
    time INTEGER NOT NULL,
    expected_text INTEGER NOT NULL,
    FOREIGN KEY (expected_text)
        REFERENCES EXPECTED_TEXT (_id)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
    );"""
    ,

    "CORRECTED_IMG": """(_id INTEGER PRIMARY KEY,
     base_img INTEGER NOT NULL,
     img_path  text,
     FOREIGN KEY (base_img)
        REFERENCES BASE_IMG (_id)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
    );"""
}

_currently_open = None

class DataBase:
    tableName = "INVALID"

    def __init__(self, id=None):
        self.id = id
        _add_current_data(type(self), self)

    @staticmethod
    def read(dict_parameter):
        pass

    def save(self):
        pass

    def get_element(self):
        return (
            ("_id",),
            (self.id,)
        )

class DbConnector:
    """Save an image on the database"""

    def __init__(self, db_name="./db.sqlite3", mr="./img"):
        self.db_name = db_name
        self.media_root = mr

        self.db = None
        self.filters = []

    def __enter__(self):
        global _currently_open
        try:
            self.db = sqlite3.connect(self.db_name)
            self.has_tables()
            _currently_open = self
        except sqlite3.Error as e:
            print(e)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _currently_open
        _currently_open = self
        if self.db is not None:
            self.db.close()

    def insert(self, data: DataBase):
        cur = self.db.cursor()
        data.save()
        element_list = data.get_element()

        text = []
        val = []

        for t,v in zip(element_list[0],element_list[1]):
            if v is not None:
                text.append(t)
                val.append(v)

        sql = '''INSERT INTO %s(%s) VALUES (%s) ''' % (
            data.tableName,
            ",".join(text),
            ("?," * len(text))[:-1]
        )
        try:
            if debug:
                print(sql)
            cur.execute(sql, val)
            self.db.commit()
            data.id = cur.lastrowid
        except sqlite3.Error as e:
            print(e)

    def add_filter(self, f : Filter):
        self.filters.append(f)

    def generate_filter(self):
        if len(self.filters) == 0:
            return " "
        else:
            statement = ""
            for f in self.filters:
                if f == self.filters[0]:
                    statement = "WHERE %s" % f.statement
                else:
                    statement += "%s %s" % (f.logical_sign, f.statement)
        return statement

    def read(self, data_type, clearFilter=True):
        cur = self.db.cursor()

        filters = self.generate_filter()

        sql = '''SELECT * FROM %s %s;''' % (data_type.tableName, filters)
        if debug:
            print(sql)
        cur.execute(sql)
        data = cur.fetchall()

        strippped_indexes = [x[0] for x in cur.description]
        values_list = []
        for e in data:
            parameters = dict()
            for i in range(len(e)):
                parameters[strippped_indexes[i]] = e[i]
            new_element = data_type.read(parameters)
            values_list.append(new_element)

        if clearFilter:
            self.filters.clear()

        return values_list

    def has_tables(self):
        cur = self.db.cursor()
        for t in tables_names:
            cur.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name= ?;''',
                        (t,)
                        )
            if len(cur.fetchall()) == 0:
                # create the missing table
                query = '''CREATE TABLE ''' + t + tables_schemas[t]
                self.db.execute(query)
                self.db.commit()





class ExpectedText(DataBase):
    tableName = "EXPECTED_TEXT"

    def __init__(self, text, x_repeats, y_repeats, id=None, ):
        super().__init__(id)
        self.text = text
        self.x_repeats = x_repeats
        self.y_repeats = y_repeats

    @staticmethod
    def read(dict_parameter):
        id = dict_parameter["_id"]
        text = dict_parameter["text"]
        x_repeats = dict_parameter["x_repeats"]
        y_repeats = dict_parameter["y_repeats"]

        return ExpectedText(text, x_repeats, y_repeats, id)

    def get_element(self):
        return (
            ("_id", "text", "x_repeats", "y_repeats"),
            (self.id, self.text, self.x_repeats, self.y_repeats)
        )


class BaseImg(DataBase):
    time: datetime
    expected_text: ExpectedText
    image_path: str

    tableName = "BASE_IMG"

    def __init__(self, img, time, expected_text, id=None):
        super().__init__(id)
        self.time = time
        self.img = img
        self.expected_text = expected_text

        self.image_path = None

    @staticmethod
    def read(dict_parameter):
        id = dict_parameter["_id"]
        time = datetime.fromtimestamp(dict_parameter["time"], tz=timezone.utc)

        expected_text_id = dict_parameter["expected_text"]

        if expected_text_id in expected_texts:
            expected_text = expected_texts[expected_text_id]
        else:
            db = _currently_open

            db.add_filter(Filters.EqualFilter(expected_text_id, "_id"))
            expected_text = db.read(ExpectedText)

        img_path = dict_parameter["img_path"]

        img = cv.imread(img_path)

        return BaseImg(img, time, expected_text, id)

    def save(self):
        if not os.path.isdir(image_path):
            os.mkdir(image_path)

        self.image_path = image_path + "base_" + self.time.strftime('%Y-%m-%d_%H-%M-%S') + ".png"

        cv.imwrite(self.image_path, self.img)

    def get_element(self):
        return (
            ("_id", "expected_text", "img_path", "time"),
            (self.id, self.expected_text.id, self.image_path, int(self.time.replace(tzinfo=timezone.utc).timestamp()))
        )






class CorrectedImg(DataBase):
    tableName = "CORRECTED_IMG"

    def __init__(self, img, base_img, id=None):
        super().__init__(id)
        self.base_img = base_img
        self.img = img

        self.image_path = None

    @staticmethod
    def read(dict_parameter):
        id = dict_parameter["_id"]
        time = datetime.fromtimestamp(dict_parameter["time"], tz=timezone.utc)

        base_img_id = dict_parameter["base_img"]

        if base_imgs[base_img_id] is not None:
            base_img = base_imgs[base_img_id]
        else:
            db = _currently_open

            db.add_filter(Filters.EqualFilter(base_img_id, "_id"))
            base_img = db.read(ExpectedText)

        img_path = dict_parameter["img_path"]

        img = cv.imread(img_path)

        return BaseImg(img, base_img, id)

    def save(self):
        if not os.path.isdir(image_path):
            os.mkdir(image_path)

        self.image_path = image_path + "corrected_" + self.base_img.time.strftime('%Y-%m-%d_%H-%M-%S') + ".png"
        cv.imwrite(self.image_path, self.img)

    def get_element(self):
        return (
            ("_id", "img_path", "base_img"),
            (self.id, self.image_path, self.base_img.id)
        )



expected_texts = dict()
base_imgs = dict()
corrected_img = dict()


def _add_current_data(data_type, value):
    id = value.id
    if id is None:
        return

    if data_type is ExpectedText:
        expected_texts[id] = value
    elif data_type is BaseImg:
        base_imgs[id] = value
    elif data_type is CorrectedImg:
        corrected_img[id] = value


if __name__ == '__main__':

    if os.path.exists('./db.sqlite3'):
        os.remove('./db.sqlite3')
    with DbConnector() as i:
        print(i.db_name)
        cur = i.db.cursor()
        test2 = ExpectedText("Hello Wolrd", 4, 5)
        test = ExpectedText("Hello EVERYONE", 3, 5)
        i.insert(test2)
        i.insert(test)

        from Capture import Camera
        from cv2 import waitKey

        cam = Camera.Cam("../camConfig.json")
        cam.activate_camera()
        cam.show_camera()
        waitKey(199)
        img = BaseImg(img=cam.get_image(), time=datetime.now(), expected_text=test)
        i.insert(img)
        #     text = i.read(ExpectedText)

        print("\n img")
        cur.execute('select * FROM BASE_IMG;')
        img_read = i.read(BaseImg)

        cam.close_camera()