from os.path import join as pjoin
import os
import preprocess as pre
from Webpage import Webpage
import cv2
from config import Configuration

if __name__ == '__main__':

    configuration = Configuration()
    configuration.COMPONENT_DETECTION = True
    configuration.TEXT_DETECTION = True
    configuration.TEXT_AND_COMPONENT_MERGE = True
    # configuration.INPUT_PATH = 'data/input/ConnectEDHome.jpeg'
    configuration.INPUT_PATH = 'data/input/GrammarTest.JPG'
    configuration.OUTPUT_PATH = 'data/output'

    configuration.CHECK_LAYOUT = False
    configuration.CHECK_ALIGNMENT = False
    configuration.CHECK_TEXT_CONTRAST = True
    configuration.CHECK_TEXT_SPELLING = False
    configuration.CHECK_IMAGES = False

    webpage = Webpage(configuration.INPUT_PATH, configuration.OUTPUT_PATH, configuration.RESIZE_HEIGHT)

    original_img = cv2.imread(configuration.INPUT_PATH)
    print(type(original_img))
    print(original_img[0][0])
    webpage.image = original_img

    preprocessed_img = pre.get_vertically_cropped_image(original_img,
                                                        configuration.CROP_VALUE_TOP, configuration.CROP_VALUE_BOTTOM)

    if configuration.TEXT_DETECTION:
        import elements.text_detection as text
        os.makedirs(pjoin(configuration.OUTPUT_PATH, 'ocr'), exist_ok=True)
        webpage.text_elements = text.text_detection(preprocessed_img, configuration)

    if configuration.COMPONENT_DETECTION:
        import elements.non_text_detection as ip
        os.makedirs(pjoin(configuration.OUTPUT_PATH, 'ip'), exist_ok=True)
        image2 = text.draw_text_blocks(preprocessed_img, webpage.text_elements)
        cv2.imwrite('text_example22.jpg', image2)
        webpage.non_text_elements, detected_image = ip.compo_detection(preprocessed_img, image2, configuration)

    if configuration.TEXT_AND_COMPONENT_MERGE:
        from elements import merge as merge

        webpage.elements = merge.merge_text2(preprocessed_img, webpage.non_text_elements, webpage.text_elements)

    if configuration.CHECK_LAYOUT:
        from uicheck.LayoutCheck import LayoutCheck

        layout = LayoutCheck()
        report2, element = layout.check_element_collision(webpage.image_id, preprocessed_img, webpage.elements)
        cv2.imshow("Name", report2)
        cv2.waitKey(0)

        for e in element:
            print(e)

    if configuration.CHECK_ALIGNMENT:
        from uicheck.AlignmentCheck import AlignmentCheck

        alignment = AlignmentCheck()
        bot_aligned = alignment.check_alignment(webpage.image_id, preprocessed_img, webpage.elements, 4, "boundary_bottom")
        top_aligned = alignment.check_alignment(webpage.image_id, preprocessed_img, webpage.elements, 4, "boundary_top")
        left_aligned = alignment.check_alignment(webpage.image_id, preprocessed_img, webpage.elements, 4, "boundary_left")
        right_aligned = alignment.check_alignment(webpage.image_id, preprocessed_img, webpage.elements, 4, "boundary_right")
        row_center_aligned = alignment.check_alignment(webpage.image_id, preprocessed_img, webpage.elements, 4, "row_center")
        col_center_aligned = alignment.check_alignment(webpage.image_id, preprocessed_img, webpage.elements, 4, "column_center")

    if configuration.CHECK_TEXT_CONTRAST:
        from uicheck.ContrastCheck import ContrastCheck

        contrast = ContrastCheck()
        image, text_dic = contrast.check_text_contrast(webpage.image_id, webpage.text_elements, preprocessed_img)

        for i in text_dic:
            if text_dic[i]["test"] != "pass":
                print(text_dic[i]["contrast_lvl"])

    if configuration.CHECK_TEXT_SPELLING:
        from uicheck.GrammarCheck import GrammarCheck

        grammar = GrammarCheck()
        image, webpage.grammar_test_results = grammar.grammar_check(preprocessed_img, webpage.text_elements)
        cv2.imshow("dd", image)
        cv2.waitKey(0)

        for i in webpage.grammar_test_results:
            if webpage.grammar_test_results[i]["test"] != "pass":
                print(webpage.grammar_test_results[i]["contrast_lvl"])

    if configuration.CHECK_IMAGES:
        from uicheck.ImageCheck import ImageCheck

        blurred = ImageCheck()
        img = blurred.check_blured(webpage.image_id, preprocessed_img, webpage.elements, 100)
