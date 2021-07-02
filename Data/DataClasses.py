import os
from datetime import datetime, timezone
from environement import image_path
import cv2 as cv

class DataBase:
    def __init__(self, _id=None, tableName = "INVALID"):
        self.id = _id
        self.tableName = tableName

    def save(self):
        pass

    def get_element(self):
        return (
            ("_id",),
            (self.id,)
        )


class ExpectedText(DataBase):
    def __init__(self, text, x_repeats, y_repeats, _id=None, ):
        super().__init__(_id, "EXPECTED_TEXT")
        self.text = text
        self.x_repeats = x_repeats
        self.y_repeats = y_repeats

    def get_element(self):
        return (
            ("_id", "text", "x_repeats", "y_repeats"),
            (self.id, self.text, self.x_repeats, self.y_repeats)
        )


class BaseImg(DataBase):
    time: datetime
    expected_text: ExpectedText
    image_path: str

    def __init__(self, img, time, expected_text, _id=None):
        super().__init__(_id, "BASE_IMG")
        self.time = time
        self.img = img
        self.expected_text = expected_text

        self.image_path = None

    def save(self):
        self.image_path = image_path + "base_" + self.time.strftime('%Y-%m-%d_%H-%M-%S') + ".png"

        cv.imwrite(self.image_path, self.img)

    def get_element(self):
        return (
            ("_id", "expected_text", "img_path", "time"),
            (self.id, self.expected_text.id, self.image_path, int(self.time.replace(tzinfo=timezone.utc).timestamp()))
        )


class CorrectedImg(DataBase):
    def __init__(self, img, base_img, _id=None):
        super().__init__(_id, "CORRECTED_IMG")
        self.base_img = base_img
        self.img = img

        self.image_path = None

    def save(self):
        self.image_path = image_path + "corrected_" + self.base_img.time.strftime('%Y-%m-%d_%H-%M-%S') + ".png"
        cv.imwrite(self.image_path, self.img)

    def get_element(self):
        return (
            ("_id", "img_path", "base_img"),
            (self.id, self.image_path, self.base_img.id)
        )
