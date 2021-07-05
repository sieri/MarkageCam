from Data import DataClasses

expected_texts = dict()
base_imgs = dict()
corrected_img = dict()

def add(data_type, value):
    id = value.id
    if id is None:
        return

    if data_type is DataClasses.ExpectedText:
        expected_texts[id] = value
    elif data_type is DataClasses.BaseImg:
        base_imgs[id] = value
    elif data_type is DataClasses.CorrectedImg:
        corrected_img[id] = value