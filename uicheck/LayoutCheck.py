import cv2
import csv
import preprocess as pre


def print_reports(name, org_image, element_list):
    image = org_image.copy()
    for widget in element_list:
        print(widget[0], widget[1], widget[2], widget[3])
        cv2.rectangle(image, (widget[0], widget[1]), (widget[2], widget[3]), (0, 0, 255), 2)

    write_path = 'data/reports/layout/' + name + '.jpg'

    with open('data/reports/layout/' + name + '.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(element_list)

    cv2.imwrite(write_path, image)
    scaled_img = pre.get_resize_img(image, 1 / 3)
    cv2.imshow(name, scaled_img)
    cv2.waitKey(0)


def get_report(name, org_image, element_list):
    image = org_image.copy()
    for widget in element_list:
        print(widget.bbox.boundary_left, widget.bbox.boundary_right,
              widget.bbox.boundary_bottom, widget.bbox.boundary_top)
        cv2.rectangle(image, (widget.bbox.boundary_left, widget.bbox.boundary_bottom),
                      (widget.bbox.boundary_right, widget.bbox.boundary_top), (0, 0, 255), 2)

    # write_path = 'data/reports/layout/' + name + '.jpg'

    # with open('data/reports/layout/' + name + '.csv', 'w', encoding='UTF8', newline='') as f:
    #     writer = csv.writer(f)
    #     writer.writerows(element_list)

    # cv2.imwrite(write_path, image)
    # scaled_img = pre.get_resize_img(image, 1 / 3)
    # cv2.imshow(name, scaled_img)
    # cv2.waitKey(0)
    return image, element_list


class LayoutCheck:
    def __init__(self):
        self.collided_element_list = []

    def check_element_collision(self, image_id,  image, element_list):
        collided_elements = []

        widget_list = element_list

        for widget1 in widget_list:
            w1left = widget1.bbox.boundary_left
            w1right = widget1.bbox.boundary_right
            w1bottom = widget1.bbox.boundary_bottom
            w1top = widget1.bbox.boundary_top

            for widget2 in reversed(widget_list):
                if widget2.bbox != widget1.bbox:
                    w2left = widget2.bbox.boundary_left
                    w2right = widget2.bbox.boundary_right
                    w2bottom = widget2.bbox.boundary_bottom
                    w2top = widget2.bbox.boundary_top
                    # check for partial collision
                    if (w1left <= w2left <= w1right and w1bottom <= w2bottom <= w1top) \
                            or (w1left <= w2right <= w1right and w1bottom <= w2bottom <= w1top) \
                            or (w1left <= w2right <= w1right and w1bottom <= w2top <= w1top) \
                            or (w1left <= w2left <= w1right and w1bottom <= w2top <= w1top):
                        # check for full collision
                        if w1left <= w2left <= w1right and w1bottom <= w2bottom <= w1top \
                                and w1left <= w2right <= w1right and w1bottom <= w2top <= w1top:
                            continue
                        if widget2 not in collided_elements:
                            collided_elements.append(widget2)

        report_name = str(image_id) + '_collision_report'
        self.collided_element_list.append([report_name, collided_elements])
        image_report, element_list = get_report(report_name, image, collided_elements)
        return image_report, element_list

    def check_viewport_protrusion(self, image_id, image, element_list, max_width):
        protruded_elements = []
        for element in element_list:
            if element[1] > max_width or element[3] > max_width:
                protruded_elements.append(element)

        report_name = str(image_id) + '_viewport_protrusion_report'
        self.collided_element_list.append([report_name, protruded_elements])
        print_reports(report_name, image, protruded_elements)

    # def check_element_collision(self, image_id,  image, element_list):
    #     collided_widgets2 = []
    #     collided_elements = {}
    #     # widget_list = element_list.copy()
    #     # widget_list = ()
    #
    #     widget_list = element_list
    #
    #     # for widget1 in widget_list:
    #     #     print("Widgets")
    #     #     print(widget1)
    #     #     print("Widgets[0]")
    #     #     print(widget1[0])
    #
    #     for widget1 in widget_list:
    #         # print(widget1)w
    #         # bbox1 = widget1.get_boundaries()
    #         bbox1 = [widget1.bbox.boundary_left, widget1.bbox.boundary_bottom,
    #                  widget1.bbox.boundary_right, widget1.bbox.boundary_top]
    #         # print("#####################")
    #         # print(widget1)
    #         print(bbox1)
    #
    #         for widget2 in reversed(widget_list):
    #             # bbox2 = widget2.get_boundaries()
    #             bbox2 = [widget2.bbox.boundary_left, widget2.bbox.boundary_bottom,
    #                      widget2.bbox.boundary_right, widget2.bbox.boundary_top]
    #             print(bbox2)
    #             if bbox2 != bbox1:
    #                 # check for partial collision
    #                 if (bbox1[0] <= bbox2[0] <= bbox1[2] and bbox1[1] <= bbox2[1] <= bbox1[3]) \
    #                         or (bbox1[0] <= bbox2[2] <= bbox1[2] and bbox1[1] <= bbox2[1] <= bbox1[3]) \
    #                         or (bbox1[0] <= bbox2[2] <= bbox1[2] and bbox1[1] <= bbox2[3] <= bbox1[3]) \
    #                         or (bbox1[0] <= bbox2[0] <= bbox1[2] and bbox1[1] <= bbox2[3] <= bbox1[3]):
    #                     # check for full collision
    #                     if bbox1[0] <= bbox2[0] <= bbox1[2] and bbox1[1] <= bbox2[1] <= bbox1[3] \
    #                             and bbox1[0] <= bbox2[2] <= bbox1[2] and bbox1[1] <= bbox2[3] <= bbox1[3]:
    #                         continue
    #                     if bbox2 not in collided_widgets2:
    #                         collided_widgets2.append(bbox2)
    #
    #     report_name = str(image_id) + '_collision_report'
    #     self.layout_check_list.append([report_name, collided_widgets2])
    #     print_reports(report_name, image, collided_widgets2)
