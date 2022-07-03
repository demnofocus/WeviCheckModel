from uuid import uuid4


def get_name_from_path(path):
    return path.split('/')[-1][:-4]


def get_id(name):
    return name + str(uuid4())


class Webpage:
    def __init__(self, input_path, output_path, resize_height):
        self.image_id = get_id(get_name_from_path(input_path))
        self.image = None
        # self.name = get_name_from_path(input_path)
        # self.input_path = input_path
        # self.output_path = output_path
        self.resize_height = resize_height
        self.text_elements = []
        self.non_text_elements = []
        self.elements = []
        self.parameters = []
        self.alignment_test_result = []
        self.contrast_test_results = []
        self.collision_test_results = []
        self.text_defects = []
        self.spelling_results = []
        self.grammar_test_results = []
