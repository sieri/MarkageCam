import sqlite3

tableNames = ["BASE_IMG", "CORRECTED_IMG", "TREATED_IMG"]


class imageSaver:
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

    def save_base_img(self):
        pass

    def has_tables(self):
        cur = self.db.cursor()
        for t in tableNames:
            cur.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name= ?;''',
                        (t,)
                        )
            if len(cur.fetchall()) == 0:
                print("no db")
                cur.execute('''
                    CREATE TABLE ''' + t + '''("test text, test2 date")
                '''
                            )
            else:
                print("table here")


# temp test code
if __name__ == '__main__':
    with imageSaver() as i:
        i.save_base_img()