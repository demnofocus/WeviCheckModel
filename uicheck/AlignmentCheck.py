import cv2
import random
import csv
import preprocess as pre


def find_in_nested_list(main_list, element):
    if len(main_list) != 0:
        for row_list in main_list:
            if row_list.__contains__(element):
                return True


def get_new_colour(colour_list):
    col = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    if len(colour_list) != 0:
        if colour_list.__contains__(col):
            get_new_colour(colour_list)
    return col


def get_alignment_name(alignment_type):
    if alignment_type == 1:
        return "left_aligned_columns"
    elif alignment_type == 2:
        return "right_aligned_columns"
    elif alignment_type == 3:
        return "top_aligned_rows"
    elif alignment_type == 4:
        return "bottom_aligned_rows"


def print_report(name, list_of_filtered_lists, org_image):
    image = org_image.copy()
    colours = []
    for list_of_elements_filtered in list_of_filtered_lists:
        colour = get_new_colour(colours)
        colours.append(colour)
        if len(list_of_elements_filtered) > 1:
            for widget in list_of_elements_filtered:
                cv2.rectangle(image, (widget.bbox.boundary_left, widget.bbox.boundary_bottom),
                              (widget.bbox.boundary_right, widget.bbox.boundary_top), colour, 2)

    write_path = 'data/reports/alignment/' + name + '.jpg'

    with open('data/reports/alignment/' + name + '.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(list_of_filtered_lists)

    cv2.imwrite(write_path, image)
    scaled_img = pre.get_resize_img(image, 1 / 3)
    cv2.imshow(name, scaled_img)
    cv2.waitKey(0)


def get_report(org_image, list_of_filtered_lists):
    image = org_image.copy()
    colours = []
    for list_of_elements_filtered in list_of_filtered_lists:
        colour = get_new_colour(colours)
        colours.append(colour)
        if len(list_of_elements_filtered) > 1:
            for widget in list_of_elements_filtered:
                cv2.rectangle(image, (widget.bbox.boundary_left, widget.bbox.boundary_bottom),
                              (widget.bbox.boundary_right, widget.bbox.boundary_top), colour, 2)
    return image


def get_center(point1, point2):
    return int(point1 + (abs(point2-point1)/2))


class AlignmentCheck:
    def __init__(self):
        self.alignment_list = []
        self.report_image_list = []

    def check_alignment(self, image_id, image, element_list, threshold, alignment_type):
        aligned_ele_list = []
        for element in element_list:
            row = []
            if not find_in_nested_list(aligned_ele_list, element):
                row.append(element)
                for element2 in element_list:
                    if element2 != element:
                        if alignment_type == "boundary_bottom":
                            if (0 <= abs(element.bbox.boundary_bottom - element2.bbox.boundary_bottom) < threshold) \
                                    and not find_in_nested_list(aligned_ele_list, element2):
                                row.append(element2)
                        elif alignment_type == "boundary_top":
                            if (0 <= abs(element.bbox.boundary_top - element2.bbox.boundary_top) < threshold) \
                                    and not find_in_nested_list(aligned_ele_list, element2):
                                row.append(element2)
                        elif alignment_type == "boundary_left":
                            if (0 <= abs(element.bbox.boundary_left - element2.bbox.boundary_left) < threshold) \
                                    and not find_in_nested_list(aligned_ele_list, element2):
                                row.append(element2)
                        elif alignment_type == "boundary_right":
                            if (0 <= abs(element.bbox.boundary_right - element2.bbox.boundary_right) < threshold) \
                                    and not find_in_nested_list(aligned_ele_list, element2):
                                row.append(element2)
                        elif alignment_type == "row_center":
                            if (0 <= abs(get_center(element.bbox.boundary_bottom, element.bbox.boundary_top)
                                         - get_center(element2.bbox.boundary_bottom, element2.bbox.boundary_top))
                                < threshold) \
                                    and not find_in_nested_list(aligned_ele_list, element2):
                                row.append(element2)
                        elif alignment_type == "column_center":
                            if (0 <= abs(get_center(element.bbox.boundary_left, element.bbox.boundary_right)
                                         - get_center(element2.bbox.boundary_left, element2.bbox.boundary_right))
                                < threshold) \
                                    and not find_in_nested_list(aligned_ele_list, element2):
                                row.append(element2)
                        else:
                            print("not valid")
                aligned_ele_list.append(row)

        # name = str(image_id) + "_" + alignment_type
        # self.alignment_list.append([name, rows_list])
        # print_report(name, rows_list, image)
        return get_report(image, aligned_ele_list)
