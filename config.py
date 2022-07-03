class Configuration:

    def __init__(self):

        self.TEXT_DETECTION = True
        self.COMPONENT_DETECTION = True
        self.TEXT_AND_COMPONENT_MERGE = True

        # Parameters
        self.THRESHOLD_REC_MIN_EVENNESS = 0.7
        self.THRESHOLD_REC_MAX_DENT_RATIO = 0.25
        self.THRESHOLD_LINE_THICKNESS = 8
        self.THRESHOLD_LINE_MIN_LENGTH = 0.95  # (120/800, 422.5/450) maximum h and w ratio for an atomic compo (button)
        self.THRESHOLD_COMPO_MAX_SCALE = (0.25, 0.98)
        self.THRESHOLD_TEXT_MAX_WORD_GAP = 10
        self.THRESHOLD_TEXT_MAX_HEIGHT = 0.04  # 40/800 maximum height of text
        self.THRESHOLD_TOP_BOTTOM_BAR = (0.045, 0.94)  # (36/800, 752/800) height ratio of top and bottom bar
        self.THRESHOLD_BLOCK_MIN_HEIGHT = 0.03  # 24/800
        self.THRESHOLD_MIN_BINARY_GRADIENT = 15
        self.THRESHOLD_MIN_ELEMENT_AREA = 15
        self.CROP_VALUE_TOP = 0
        self.CROP_VALUE_BOTTOM = 0
        self.CROP_VALUE_LEFT = 0
        self.KERNEL_SIZE = 0
        self.RESIZE_HEIGHT = 800
        self.CROP_VALUE_RIGHT = 0
        self.FF_BLOCK = 5
        self.INPUT_PATH = None
        self.OUTPUT_PATH = None

        # Tests
        self.CHECK_LAYOUT = False
        self.CHECK_ALIGNMENT = False
        self.CHECK_TEXT_CONTRAST = False
        self.CHECK_SPELLING = False
        self.CHECK_GRAMMAR = False
        self.CHECK_IMAGES = False
