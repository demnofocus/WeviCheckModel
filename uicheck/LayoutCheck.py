import cv2


def get_report(name, org_image, element_list):
    image = org_image.copy()
    count = 1
    for widget in element_list:
        cv2.putText(image, "{}: {}".format("Issue", count),
                    (widget.bbox.boundary_left, widget.bbox.boundary_bottom),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
        cv2.rectangle(image, (widget.bbox.boundary_left, widget.bbox.boundary_bottom),
                      (widget.bbox.boundary_right, widget.bbox.boundary_top), (0, 0, 255), 2)
        count = count + 1

    return image, element_list


class LayoutCheck:
    def __init__(self):
        self.collided_element_list = []

    def check_element_collision(self, image_id,  image, element_list):
        collided_elements = []
        test_result = "pass"
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
                            test_result = "fail"
                            collided_elements.append(widget2)

        report_name = str(image_id) + '_collision_report'
        self.collided_element_list.append([report_name, collided_elements])
        image_report, element_list = get_report(report_name, image, collided_elements)
        return image_report, element_list, test_result

    def check_viewport_protrusion(self, image_id, image, element_list, max_width):
        protruded_elements = []
        for element in element_list:
            if element[1] > max_width or element[3] > max_width:
                protruded_elements.append(element)

        report_name = str(image_id) + '_viewport_protrusion_report'
        self.collided_element_list.append([report_name, protruded_elements])

