from Data import DB
from ImgTreatement import DebugDisplay


def process(img: DB.CorrectedImg):
    DebugDisplay.show_resized("Test", img.img)