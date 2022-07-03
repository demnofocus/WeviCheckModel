import base64
from os.path import join as pjoin
import os

import pymongo

import preprocess as pre
from Webpage import Webpage
import cv2
import elements.text_detection as text
import elements.non_text_detection as ip
from config import Configuration
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin
from flask_pymongo import PyMongo
import numpy as np
from PIL import Image
import io

app = Flask(__name__)
cors = CORS(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/wevicheck"
mongo = PyMongo(app)
configuration = Configuration()

db = pymongo.MongoClient('localhost', 27017)['wevicheckdb']


@app.route(rule="/test_parameters", methods=["POST"])
def parameter_test():
    req = request.get_json(force=True)
    print('[SERVER] - Received parameters: {}'.format(req.keys()))
    min_grad = float(req["bin_grad"])
    min_ele_area = float(req["min_ele_area"])
    image_string = req["image"]

    image_info = ""
    new_image_string = ""
    if "jpeg" in image_string:
        image_info = "data:image/jpeg;base64,"
        new_image_string = image_string.replace(image_info, "")
    elif "png" in image_string:
        image_info = "data:image/png;base64,"
        new_image_string = image_string.replace(image_info, "")
    elif "jpg" in image_string:
        image_info = "data:image/jpg;base64,"
        new_image_string = image_string.replace(image_info, "")

    file_image = base64.b64decode(new_image_string)

    image_array = np.frombuffer(buffer=file_image, dtype=np.uint8)
    image = cv2.imdecode(buf=image_array, flags=cv2.IMREAD_ANYCOLOR)

    # Generate binary image
    gray_img = pre.get_grey(original=image)
    binary_img_array = pre.get_binary_image(gray_img=gray_img, grad_min=min_grad)

    binary_img22 = Image.fromarray(binary_img_array)
    binary_buffered = io.BytesIO()
    binary_img22.save(binary_buffered, "JPEG")

    binary_encode = image_info + str(base64.b64encode(binary_buffered.getvalue()))[2:][:-1]

    # Generate element detected image
    configuration.INPUT_PATH = 'data/input/ConnectEDHome.jpeg'
    configuration.OUTPUT_PATH = 'data/output'
    configuration.THRESHOLD_MIN_ELEMENT_AREA = min_ele_area
    elements, detected_img_array = ip.compo_detection(image, image, configuration)

    detected_img22 = Image.fromarray(detected_img_array)
    detected_buffered = io.BytesIO()
    detected_img22.save(detected_buffered, "JPEG")

    detected_encode = image_info + str(base64.b64encode(detected_buffered.getvalue()))[2:][:-1]

    message = {"binary_img": binary_encode, "detected_img": detected_encode}
    # print("[MODEL] - Generated binary image", jsonify(message))

    return message


@app.route('/select_tests', methods=['POST'])
def set_tests():
    req = request.get_json(force=True)
    print('[SERVER] - Received tests: {}'.format(req))

    if not req["layout"] is None:
        configuration.CHECK_LAYOUT = req["layout"]
    if not req["alignment"] is None:
        configuration.CHECK_ALIGNMENT = req["alignment"]
    if not req["text_contrast"] is None:
        configuration.CHECK_TEXT_CONTRAST = req["text_contrast"]
    if not req["spelling"] is None:
        configuration.CHECK_SPELLING = req["spelling"]
    if not req["grammar"] is None:
        configuration.CHECK_GRAMMAR = req["grammar"]
    if not req["images"] is None:
        configuration.CHECK_IMAGES = req["images"]

    print("Tests: layout={0}, alignment={1}, text_color={2}, spelling={3}, grammar={4}, images={5}"
          .format(configuration.CHECK_LAYOUT,
                  configuration.CHECK_ALIGNMENT,
                  configuration.CHECK_TEXT_CONTRAST,
                  configuration.CHECK_SPELLING,
                  configuration.CHECK_GRAMMAR,
                  configuration.CHECK_IMAGES))
    message = {
        "status": "success"
    }

    return message


@app.route(rule='/ui_check', methods=['POST'])
def ui_check():
    req = request.get_json(force=True)
    print('[SERVER] - Received parameters: {}'.format(req.keys()))
    # min_grad = float(req["bin_grad"])
    # min_ele_area = float(req["min_ele_area"])
    image_string = req["image"]

    image_info = ""
    new_image_string = ""
    if "jpeg" in image_string:
        image_info = "data:image/jpeg;base64,"
        new_image_string = image_string.replace(image_info, "")
    elif "png" in image_string:
        image_info = "data:image/png;base64,"
        new_image_string = image_string.replace(image_info, "")
    elif "jpg" in image_string:
        image_info = "data:image/jpg;base64,"
        new_image_string = image_string.replace(image_info, "")

    file_image = base64.b64decode(new_image_string)

    image_array = np.frombuffer(buffer=file_image, dtype=np.uint8)
    image = cv2.imdecode(buf=image_array, flags=cv2.IMREAD_ANYCOLOR)

    configuration.OUTPUT_PATH = 'data/output'
    configuration.INPUT_PATH = 'data/output'

    webpage = Webpage(configuration.INPUT_PATH, configuration.OUTPUT_PATH, configuration.RESIZE_HEIGHT)

    original_img = image

    print(type(original_img))
    print(original_img.shape)
    print(original_img[0][0])
    webpage.image = original_img

    preprocessed_img = pre.get_vertically_cropped_image(original_img, configuration.CROP_VALUE_TOP,
                                                        configuration.CROP_VALUE_BOTTOM)

    os.makedirs(pjoin(configuration.OUTPUT_PATH, 'ocr'), exist_ok=True)
    os.makedirs(pjoin(configuration.OUTPUT_PATH, 'ip'), exist_ok=True)

    webpage.text_elements = text.text_detection(preprocessed_img, configuration)
    image2 = text.draw_text_blocks(preprocessed_img, webpage.text_elements)
    cv2.imwrite('text_example22.jpg', image2)

    webpage.non_text_elements, detected_img = ip.compo_detection(preprocessed_img, image2, configuration)

    message = {}
    message.update({"image_info": {"image_name": "ConnectED s1.jpeg", "image_id": webpage.image_id}})

    if configuration.TEXT_AND_COMPONENT_MERGE:
        from elements import merge as merge
        webpage.elements = merge.merge_text2(preprocessed_img, webpage.non_text_elements, webpage.text_elements)

    if configuration.CHECK_LAYOUT:
        from uicheck.LayoutCheck import LayoutCheck

        layout = LayoutCheck()
        image_array, report = layout.check_element_collision(webpage.image_id, preprocessed_img, webpage.elements)

        image_report = Image.fromarray(image_array)
        image_report_buffered = io.BytesIO()
        image_report.save(image_report_buffered, "JPEG")

        report_encoded = "data:image/jpeg;base64," + str(base64.b64encode(image_report_buffered.getvalue()))[2:][:-1]
        report = {"number1": {"info": "hello"}, "number2": {"info": "hello2"}, "number3": {"info": "hello2"}}
        message.update({"layout_test": {"image": report_encoded, "report": report}})

    if configuration.CHECK_ALIGNMENT:
        from uicheck.AlignmentCheck import AlignmentCheck

        alignment = AlignmentCheck()
        image_array = alignment.check_alignment(webpage.image_id, preprocessed_img, webpage.elements, 4, "boundary_bottom")
        image_report = Image.fromarray(image_array)
        image_report_buffered = io.BytesIO()
        image_report.save(image_report_buffered, "JPEG")
        report_encoded = "data:image/jpeg;base64," + str(base64.b64encode(image_report_buffered.getvalue()))[2:][:-1]

        image_array2 = alignment.check_alignment(webpage.image_id, preprocessed_img, webpage.elements, 4, "boundary_top")
        image_report2 = Image.fromarray(image_array2)
        image_report_buffered2 = io.BytesIO()
        image_report2.save(image_report_buffered2, "JPEG")
        report_encoded2 = "data:image/jpeg;base64," + str(base64.b64encode(image_report_buffered2.getvalue()))[2:][:-1]

        image_array3 = alignment.check_alignment(webpage.image_id, preprocessed_img, webpage.elements, 4, "boundary_left")
        image_report3 = Image.fromarray(image_array3)
        image_report_buffered3 = io.BytesIO()
        image_report3.save(image_report_buffered3, "JPEG")
        report_encoded3 = "data:image/jpeg;base64," + str(base64.b64encode(image_report_buffered3.getvalue()))[2:][:-1]

        image_array4 = alignment.check_alignment(webpage.image_id, preprocessed_img, webpage.elements, 4, "boundary_right")
        image_report4 = Image.fromarray(image_array4)
        image_report_buffered4 = io.BytesIO()
        image_report4.save(image_report_buffered4, "JPEG")
        report_encoded4 = "data:image/jpeg;base64," + str(base64.b64encode(image_report_buffered4.getvalue()))[2:][:-1]

        image_array5 = alignment.check_alignment(webpage.image_id, preprocessed_img, webpage.elements, 4, "row_center")
        image_report5 = Image.fromarray(image_array5)
        image_report_buffered5 = io.BytesIO()
        image_report5.save(image_report_buffered5, "JPEG")
        report_encoded5 = "data:image/jpeg;base64," + str(base64.b64encode(image_report_buffered5.getvalue()))[2:][:-1]

        image_array6 = alignment.check_alignment(webpage.image_id, preprocessed_img, webpage.elements, 4, "column_center")
        image_report6 = Image.fromarray(image_array6)
        image_report_buffered6 = io.BytesIO()
        image_report6.save(image_report_buffered6, "JPEG")
        report_encoded6 = "data:image/jpeg;base64," + str(base64.b64encode(image_report_buffered6.getvalue()))[2:][:-1]

        message.update({"alignment_test":
                        {"boundary_bottom": report_encoded,
                         "boundary_top": report_encoded2,
                         "boundary_left": report_encoded3,
                         "boundary_right": report_encoded4,
                         "row_center": report_encoded5,
                         "column_center": report_encoded6}})
        print(len(alignment.alignment_list))

    if configuration.CHECK_TEXT_CONTRAST:
        from uicheck.ContrastCheck import ContrastCheck

        contrast = ContrastCheck()
        image_array, text_list = contrast.check_text_contrast(webpage.image_id, webpage.text_elements, preprocessed_img)

        image_report = Image.fromarray(image_array)
        image_report_buffered = io.BytesIO()
        image_report.save(image_report_buffered, "JPEG")

        report_encoded = "data:image/jpeg;base64," + str(base64.b64encode(image_report_buffered.getvalue()))[2:][:-1]
        message.update({"contrast_test": {"image": report_encoded, "report": text_list}})

    if configuration.CHECK_SPELLING:
        from uicheck.SpellCheck import SpellCheck
        spell = SpellCheck()
        image_array, webpage.spelling_results = spell.spell_check(preprocessed_img, webpage.text_elements)

        image_report = Image.fromarray(image_array)
        image_report_buffered = io.BytesIO()
        image_report.save(image_report_buffered, "JPEG")
        report_encoded = "data:image/jpeg;base64," + str(base64.b64encode(image_report_buffered.getvalue()))[2:][:-1]
        message.update({"spelling_test": {"image": report_encoded, "report": webpage.spelling_results}})

    if configuration.CHECK_GRAMMAR:
        from uicheck.GrammarCheck import GrammarCheck

        grammar = GrammarCheck()
        image_array, webpage.grammar_test_results = grammar.grammar_check(preprocessed_img, webpage.text_elements)

        image_report = Image.fromarray(image_array)
        image_report_buffered = io.BytesIO()
        image_report.save(image_report_buffered, "JPEG")
        report_encoded = "data:image/jpeg;base64," + str(base64.b64encode(image_report_buffered.getvalue()))[2:][:-1]
        message.update({"grammar_test": {"image": report_encoded, "report": webpage.grammar_test_results}})

    if configuration.CHECK_IMAGES:
        from uicheck.ImageCheck import ImageCheck

        blurred = ImageCheck()
        image_array, blur_check_dic = blurred.check_blured(webpage.image_id, preprocessed_img, webpage.elements, 100)

        image_report = Image.fromarray(image_array)
        image_report_buffered = io.BytesIO()
        image_report.save(image_report_buffered, "JPEG")

        report_encoded = "data:image/jpeg;base64," + str(base64.b64encode(image_report_buffered.getvalue()))[2:][:-1]
        message.update({"image_test": {"image": report_encoded, "report": blur_check_dic}})

    print(message.keys())
    return message


if __name__ == '__main__':
    app.run(debug=True)
