from Data import CurrentData
from datetime import datetime, timezone
from environement import image_path
import cv2 as cv


class DataBase:
    tableName = "INVALID"

    def __init__(self, id=None):
        self.id = id
        CurrentData.add(type(self), self)

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

        if CurrentData.expected_texts[expected_text_id] is not None:
            expected_text = CurrentData.expected_texts[expected_text_id]
        else:
            expected_text = None # todo: read data from text

        img_path = dict_parameter["img_path"]

        img = cv.imread(img_path)

        return BaseImg(img, time, expected_text, id)

    def save(self):
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

        if CurrentData.base_imgs[base_img_id] is not None:
            base_img = CurrentData.base_imgs[base_img_id]
        else:
            base_img = None # todo: read data from DB

        img_path = dict_parameter["img_path"]

        img = cv.imread(img_path)

        return BaseImg(img, base_img, id)

    def save(self):
        self.image_path = image_path + "corrected_" + self.base_img.time.strftime('%Y-%m-%d_%H-%M-%S') + ".png"
        cv.imwrite(self.image_path, self.img)

    def get_element(self):
        return (
            ("_id", "img_path", "base_img"),
            (self.id, self.image_path, self.base_img.id)
        )
