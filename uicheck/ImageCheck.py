import cv2
import csv
import preprocess as pre


def print_report(report_name, image, element_list):
    write_path = 'data/reports/images/' + report_name + '.jpg'

    # with open('data/reports/images/' + report_name + '.csv', 'w', encoding='UTF8', newline='') as f:
    #     writer = csv.writer(f)
    #     writer.writerows(element_list)

    # cv2.imwrite(write_path, image)
    # scaled_img = pre.get_resize_img(image, 1 / 3)
    # cv2.imshow(report_name, scaled_img)
    # cv2.waitKey(0)


class ImageCheck:
    def __init__(self):
        self.image_check_list = []

    def check_blured(self, image_id, image, elements, threshold):
        img = image.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # blured_list = []
        blur_check_dic = {}
        for element in elements:
            blur_check_dic.setdefault(element.id, {})
            clip = gray[element.bbox.boundary_bottom:element.bbox.boundary_top,
                        element.bbox.boundary_left:element.bbox.boundary_right]
            vl = cv2.Laplacian(clip, cv2.CV_64F).var()
            result = "pass"
            if vl < threshold:
                result = "fail"
                cv2.putText(img, "{}: {:.2f}".format("Blurred", vl),
                            (element.bbox.boundary_left, element.bbox.boundary_bottom),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
                cv2.rectangle(img, (element.bbox.boundary_left, element.bbox.boundary_bottom),
                              (element.bbox.boundary_right, element.bbox.boundary_top), (255, 0, 0), 2)
                # blured_list.append(element)
            value = {"threshold": threshold,
                     "laplacian": vl, "test": result}
            blur_check_dic[element.id] = value
        report_name = str(image_id) + '_blured_check'
        self.image_check_list.append([report_name, blur_check_dic])
        # print_report(report_name, img, elements)
        return img, blur_check_dic
