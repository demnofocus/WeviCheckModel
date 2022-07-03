from os.path import join as pjoin
import os
import preprocess as pre
import elements.Component as Compo
from elements.Component import Component
import numpy as np
import json
import cv2


def save_corners_json(file_path, compos):
    img_shape = compos[0].image_shape
    output = {'img_shape': img_shape, 'compos': []}
    f_out = open(file_path, 'w')

    for compo in compos:
        c = {'id': compo.id, 'class': compo.category}
        (c['boundary_left'], c['boundary_bottom'], c['boundary_right'], c['boundary_top']) = compo.get_boundaries()
        c['width'] = compo.width
        c['height'] = compo.height
        output['compos'].append(c)

    json.dump(output, f_out, indent=4)


def build_directory(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
    return directory


def nesting_inspection(grey, compos, ffl_block):
    """
    Inspect all big compos through block division by flood-fill
    :param compos:
    :param grey:
    :param ffl_block: gradient threshold for flood-fill
    :return: nesting compos
    """

    nesting_compos = []
    for i, compo in enumerate(compos):
        if compo.height > 50:
            replace = False
            clip_grey = compo.get_clipped(grey)
            n_compos = nested_components_detection(grey=clip_grey, grad_thresh=ffl_block)
            Compo.cvt_compos_relative_pos(n_compos, compo.bbox.boundary_left, compo.bbox.boundary_bottom)

            for n_compo in n_compos:
                if n_compo.redundant:
                    compos[i] = n_compo
                    replace = True
                    break
            if not replace:
                nesting_compos += n_compos
    return nesting_compos


def nested_components_detection(grey, grad_thresh, step_h=10, step_v=10, line_thickness=2,
                                min_rec_evenness=2, max_dent_ratio=2):
    compos = []
    mask = np.zeros((grey.shape[0] + 2, grey.shape[1] + 2), dtype=np.uint8)

    row, column = grey.shape[0], grey.shape[1]
    for x in range(0, row, step_h):
        for y in range(0, column, step_v):
            if mask[x, y] == 0:

                # flood fill algorithm to get background (layout block)
                mask_copy = mask.copy()
                ff = cv2.floodFill(grey, mask, (y, x), None, grad_thresh, grad_thresh, cv2.FLOODFILL_MASK_ONLY)
                # ignore small regions
                if ff[0] < 500:
                    continue
                mask_copy = mask - mask_copy
                region = np.reshape(cv2.findNonZero(mask_copy[1:-1, 1:-1]), (-1, 2))
                region = [(p[1], p[0]) for p in region]
                # for i in region:
                #     print(i)

                compo = Component(region, grey.shape)
                if compo.height < 30:
                    continue

                if compo.area / (row * column) > 0.9:
                    continue
                elif compo.area / (row * column) > 0.7:
                    compo.redundant = True

                # get the boundary of this region
                # ignore lines
                if compo.is_line(line_thickness):
                    continue
                # ignore non-rectangle as blocks must be rectangular
                if not compo.is_rectangle(min_rec_evenness, max_dent_ratio):
                    continue

                compos.append(compo)
    return compos


def compo_filter(compos, min_area, img_shape):
    # updated code
    max_height = img_shape[0] * 0.8
    compos_new = []
    for compo in compos:
        if compo.area < min_area:
            continue
        elif compo.height > max_height:
            continue
        else:
            height_ratio = compo.width / compo.height
            width_ratio = compo.height / compo.width
            if height_ratio > 50 or width_ratio > 40 or (min(compo.height, compo.width) < 8
                                                         and max(height_ratio, width_ratio) > 10):
                continue
        compos_new.append(compo)

    return compos_new


def component_detection(binary, min_obj_area):
    step_h = 5
    step_v = 2
    mask = np.zeros((binary.shape[0] + 2, binary.shape[1] + 2), dtype=np.uint8)
    compos_all = []

    row, column = binary.shape[0], binary.shape[1]
    for i in range(0, row, step_h):
        for j in range(i % 2, column, step_v):
            if binary[i, j] == 255 and mask[i, j] == 0:
                mask_copy = mask.copy()
                ff = cv2.floodFill(binary, mask, (j, i), None, 0, 0, cv2.FLOODFILL_MASK_ONLY)
                if ff[0] < min_obj_area:
                    continue
                # print("passed", ff[0])
                mask_copy = mask - mask_copy
                region = np.reshape(cv2.findNonZero(mask_copy[1:-1, 1:-1]), (-1, 2))
                region = [(p[1], p[0]) for p in region]

                # filter out some compos
                component = Component(region, binary.shape)

                # ignore small area
                if component.width <= 3 or component.height <= 3:
                    continue

                compos_all.append(component)

    return compos_all


def is_block(clip, thread=0.15):
    """
    Block is a rectangle border enclosing a group of compos (consider it as a wireframe)
    Check if a compo is block by checking if the inner side of its border is blank
    """
    side = 4  # scan 4 lines inner forward each border
    # top border - scan top down
    blank_count = 0
    for i in range(1, 5):
        if sum(clip[side + i]) / 255 > thread * clip.shape[1]:
            blank_count += 1
    if blank_count > 2:
        return False
    # left border - scan left to right
    blank_count = 0
    for i in range(1, 5):
        if sum(clip[:, side + i]) / 255 > thread * clip.shape[0]:
            blank_count += 1
    if blank_count > 2:
        return False

    side = -4
    # bottom border - scan bottom up
    blank_count = 0
    for i in range(-1, -5, -1):
        if sum(clip[side + i]) / 255 > thread * clip.shape[1]:
            blank_count += 1
    if blank_count > 2:
        return False
    # right border - scan right to left
    blank_count = 0
    for i in range(-1, -5, -1):
        if sum(clip[:, side + i]) / 255 > thread * clip.shape[0]:
            blank_count += 1
    if blank_count > 2:
        return False
    return True


def compo_block_recognition(binary, compos, block_side_length=0.15):

    height, width = binary.shape
    for compo in compos:
        if compo.height / height > block_side_length and compo.width / width > block_side_length:
            clip = compo.get_clipped(binary)
            if is_block(clip):
                compo.category = 'Block'

    return compos


def rm_contained_compos_not_in_block(compos):
    """
    remove all components contained by others that are not Block
    """
    marked = np.full(len(compos), False)
    for i in range(len(compos) - 1):
        for j in range(i + 1, len(compos)):
            relation = compos[i].get_relationship(compos[j])
            if relation == -1 and compos[j].category != 'Block':
                marked[i] = True
            if relation == 1 and compos[i].category != 'Block':
                marked[j] = True
    new_compos = []
    for i in range(len(marked)):
        if not marked[i]:
            new_compos.append(compos[i])
    return new_compos


def draw_bounding_box(org, components, color=(0, 255, 0), line=2, show=False, write_path=None, name='board',
                      is_return=False, wait_key=0):
    """
    Draw bounding box of components on the original image
    :param wait_key:
    :param is_return:
    :param name:
    :param write_path:
    :param org: original image
    :param components: bbox [(column_min, boundary_bottom, column_max, boundary_top)]
                    -> top_left: (column_min, boundary_bottom)
                    -> bottom_right: (column_max, boundary_top)
    :param color: line color
    :param line: line thickness
    :param show: show or not
    :return: labeled image
    """
    if not show and write_path is None and not is_return:
        return

    board = org.copy()
    for compo in components:
        bbox = compo.get_boundaries()
        board = cv2.rectangle(board, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, line)
    if show:
        # board = pre.get_resize_img(board, 1 / 3)
        cv2.imshow(name, board)
        cv2.imwrite('text_example245.jpg', board)
        if wait_key is not None:
            cv2.waitKey(wait_key)
        if wait_key == 0:
            cv2.destroyWindow(name)

    return board


def compo_detection(org_image, text_block_img, config):
    input_img_path = config.INPUT_PATH
    name = input_img_path.split('/')[-1][:-4] if '/' in input_img_path else input_img_path.split('\\')[-1][:-4]
    ip_root = build_directory(pjoin(config.OUTPUT_PATH, "ip"))

    # Step 1  get binary map
    grey = pre.get_grey(text_block_img)
    binary = pre.get_binary_image(grey, grad_min=int(config.THRESHOLD_MIN_BINARY_GRADIENT))

    # Step 2 element detection
    elements = component_detection(binary, min_obj_area=int(config.THRESHOLD_MIN_ELEMENT_AREA))

    # Step 3 results refinement
    elements = compo_filter(elements, min_area=int(config.THRESHOLD_MIN_ELEMENT_AREA), img_shape=binary.shape)
    elements = compo_block_recognition(binary, elements)
    Compo.compos_update(elements, text_block_img.shape)
    Compo.compos_containment(elements)

    # Step 4 check if big compos have nesting elements
    elements += nesting_inspection(grey, elements, ffl_block=config.FF_BLOCK)
    Compo.compos_update(elements, text_block_img.shape)
    detected_img = draw_bounding_box(org_image, elements, show=False,
                                     name='nested inspect', write_path=pjoin(ip_root, name + '.jpg'), wait_key=0)
    # Step 7 save detection result
    Compo.compos_update(elements, org_image.shape)
    save_corners_json(pjoin(ip_root, name + '.json'), elements)
    return elements, detected_img
