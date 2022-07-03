import preprocess
from elements.Text import Text
from easyocr import Reader
import cv2
import json
import time
from os.path import join as pjoin


def cleanup_text(text):
    # strip out non-ASCII text using OpenCV
    return "".join([c if ord(c) < 128 else "" for c in text]).strip()


def detect_easyocr(input_image):
    langs = ['en']

    reader = Reader(langs, gpu=1 > 0)
    results = reader.readtext(input_image, paragraph=True)
    return results


def text_cvt_easy_orc_format(ocr_result):
    texts = []
    if ocr_result is not None:
        for count, (bbox, content) in enumerate(ocr_result):
            (tl, tr, br, bl) = bbox
            tl = (int(tl[0]), int(tl[1]))
            br = (int(br[0]), int(br[1]))

            # cleanup the text
            content = cleanup_text(content)

            boundary = {'left': int(tl[0]), 'top': int(br[1]),
                        'right': int(br[0]), 'bottom': int(tl[1])}
            texts.append(Text(content, boundary))

    return texts


def text_filter_noise(texts):
    valid_texts = []
    for text in texts:
        if len(text.content) <= 1 and text.content.lower() not in ['a', ',', '.', '!', '?', '$', '%', ':', '&', '+', '~']:
            continue
        valid_texts.append(text)
    return valid_texts


def visualize_texts(org_image, texts, show=False, write_path=None):
    image = org_image.copy()
    # Show text boundaries
    for text in texts:
        cv2.rectangle(image, (text.boundary['left'], text.boundary['top']),
                      (text.boundary['right'], text.boundary['bottom']), (0, 0, 255), 2)

    # # Resize image
    # img_resize = image
    # if parameters['resize_height'] > 0:
    #     img_resize = preprocess.resize_by_height(image, parameters['resize_height'])

    # Show image
    if show:
        cv2.imshow('texts', image)
        cv2.waitKey(0)
        cv2.destroyWindow('texts')
    if write_path is not None:
        cv2.imwrite(write_path, image)


def save_detection_json(file_path, texts, img_shape):
    f_out = open(file_path, 'w')
    output = {'img_shape': img_shape, 'texts': []}
    for text in texts:
        c = {'id': text.id, 'content': text.content, 'boundary_left': text.boundary['left'],
             'boundary_bottom': text.boundary['bottom'], 'boundary_right': text.boundary['right'],
             'boundary_top': text.boundary['top'], 'width': text.width, 'height': text.height}
        output['texts'].append(c)
    json.dump(output, f_out, indent=4)


def text_detection(image, config):
    start = time.time()
    # setup output path and name
    name = config.INPUT_PATH.split('/')[-1][:-4]
    ocr_root = pjoin(config.OUTPUT_PATH, 'ocr')

    # Detecting text
    ocr_result = detect_easyocr(image)
    texts = text_cvt_easy_orc_format(ocr_result)

    # Filter text noise
    texts = text_filter_noise(texts)

    # Visualize results
    visualize_texts(image, texts, show=False, write_path=pjoin(ocr_root, name+'.png'))
    save_detection_json(pjoin(ocr_root, name + '.json'), texts, image.shape)
    print("[Text Detection Completed in %.3f s] Input: %s Output: %s" % (
        time.time() - start, config.INPUT_PATH, pjoin(ocr_root, name + '.json')))

    for text in texts:
        print(text.id, " ", text.content, " ", text.boundary, " ", text.width, " ", text.height, " ",
              text.word_width, " ", text.area, " ")

    return texts


def draw_text_blocks(org_img, texts):
    drawn_image = org_img.copy()
    # Show text boundaries
    for text in texts:
        cv2.rectangle(drawn_image, (text.boundary['left'], text.boundary['top']),
                      (text.boundary['right'], text.boundary['bottom']), (0, 0, 0), -1)
    return drawn_image
