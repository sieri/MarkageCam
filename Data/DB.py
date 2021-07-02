import os
import sqlite3

from Data.DataClasses import *

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


class DbConnector:
    """Save an image on the database"""

    def __init__(self, db_name="./db.sqlite3", mr="./img"):
        self.db_name = db_name
        self.media_root = mr

        self.db = None

    def __enter__(self):
        try:
            self.db = sqlite3.connect(self.db_name)
            self.has_tables()
        except sqlite3.Error as e:
            print(e)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db is not None:
            self.db.close()

    def insert(self, data: DataBase):
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

        self.db.execute(sql, val)
        self.db.commit()

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


# temp test code
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

        cur.execute('select * FROM EXPECTED_TEXT;')
        print(cur.fetchall())