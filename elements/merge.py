import json
import cv2


def get_merged(text_list_org, compo_list_org):
    text_list = text_list_org.copy()
    compo_list = compo_list_org.copy()
    merged_list = []
    text_with_compo = []

    for text in text_list:
        text_compo = []

        for compo in reversed(compo_list):
            if list(text)[1] <= list(compo)[1] <= list(text)[3] \
                    and list(text)[2] <= list(compo)[4] <= list(text)[4] \
                    and list(text)[1] <= list(compo)[3] <= list(text)[3] \
                    and list(text)[2] <= list(compo)[2] <= list(text)[4]:
                text_compo.append((list(text)[0], list(compo)))
                compo_list.remove(compo)
        text_with_compo.append(text_compo)
        merged_list.append(text)

    for compo in compo_list:
        merged_list.append(compo)

    return text_with_compo, merged_list


def merge_text(org_img, components, text, merge_root):
    img = org_img.copy()
    compo_json = json.load(open(components, 'r'))
    text_json = json.load(open(text, 'r'))

    compos = []

    count = 0
    for compo in compo_json['compos']:
        element = (count, compo['boundary_left'], compo['boundary_bottom'], compo['boundary_right'],
                   compo['boundary_top'], compo['class'])
        count += 1
        # cv2.rectangle(img, (int(compo['boundary_left']), int(compo['boundary_top'])),
        #               (int(compo['boundary_right']), int(compo['boundary_bottom'])), (0, 255, 0), 1)
        compos.append(element)

    texts = []
    for text in text_json['texts']:
        element = (count, text['boundary_left'], text['boundary_bottom'], text['boundary_right'],
                   text['boundary_top'], 'Text', text['content'])
        count += 1
        # cv2.rectangle(img, (int(text['boundary_left']), int(text['boundary_top'])),
        #               (int(text['boundary_right']), int(text['boundary_bottom'])), (0, 255, 0), 1)
        texts.append(element)

    compo_with_text, merged = get_merged(texts, compos)

    for element in merged:
        cv2.rectangle(img, (int(element[1]), int(element[2])),
                      (int(element[3]), int(element[4])), (0, 255, 0), 1)
    # cv2.imshow('merge result', img)
    # cv2.waitKey(0)

    return merged


def get_merged2(text_list_org, compo_list_org):
    text_list = text_list_org.copy()
    compo_list = compo_list_org.copy()
    merged_list = []
    # text_with_compo = []
    text_compo = {}

    # c = {'id': text.id, 'content': text.content, 'boundary_left': text.boundary['left'],
    #      'boundary_bottom': text.boundary['bottom'], 'boundary_right': text.boundary['right'],
    #      'boundary_top': text.boundary['top'], 'width': text.width, 'height': text.height}
    # (c['boundary_left'], c['boundary_bottom'], c['boundary_right'], c['boundary_top']) = compo.get_boundaries()

    # check if components boundaries are within text boundaries
    for text in text_list:
        text_compo.setdefault(text.id, [])
        for compo in reversed(compo_list):
            compo_left, compo_bottom, compo_right, compo_top = compo.get_boundaries()
            if text.boundary['left'] <= compo_left <= text.boundary['right'] \
                    and text.boundary['bottom'] <= compo_top <= text.boundary['top'] \
                    and text.boundary['left'] <= compo_right <= text.boundary['right'] \
                    and text.boundary['bottom'] <= compo_top <= text.boundary['top']:
                text_compo[text.id].append(compo.id)
                compo_list.remove(compo)
        # merged_list.append(text)

    for compo in compo_list:
        merged_list.append(compo)

    return text_compo, merged_list


def merge_text2(org_img, component_list, text_list):
    img = org_img.copy()
    text_compo, merged = get_merged2(text_list, component_list)

    for element in merged:
        if element.category == 'Compo':
            compo_left, compo_bottom, compo_right, compo_top = element.get_boundaries()
            cv2.rectangle(img, (int(compo_left), int(compo_bottom)),
                          (int(compo_right), int(compo_top)), (0, 255, 0), 1)
            print("compo bbox", element.bbox.boundary_left)
        elif element.category == 'Text':
            cv2.rectangle(img, (int(element.boundary['left']), int(element.boundary['bottom'])),
                          (int(element.boundary['right']), int(element.boundary['top'])), (0, 255, 0), 1)
            print("text bbox", element.bbox.boundary_left)
    # cv2.imshow('merge result', img)
    # cv2.waitKey(0)

    return merged
