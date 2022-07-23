import cv2


class ImageCheck:
    def __init__(self):
        self.image_check_list = []

    def check_blured(self, image_id, image, elements, threshold):
        img = image.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur_check_dic = {}
        count = 1
        test_result = "pass"
        for element in elements:
            blur_check_dic.setdefault(element.id, {})
            clip = gray[element.bbox.boundary_bottom:element.bbox.boundary_top,
                        element.bbox.boundary_left:element.bbox.boundary_right]
            vl = cv2.Laplacian(clip, cv2.CV_64F).var()
            result = "pass"
            num = 0
            if vl < threshold:
                result = "fail"
                test_result = "fail"
                cv2.putText(img, "{}: {}".format("Issue", count),
                            (element.bbox.boundary_left, element.bbox.boundary_bottom),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 3)
                cv2.rectangle(img, (element.bbox.boundary_left, element.bbox.boundary_bottom),
                              (element.bbox.boundary_right, element.bbox.boundary_top), (255, 0, 0), 2)
                num = count
                count = count + 1
            value = {"num": num, "threshold": threshold,
                     "laplacian": vl, "test": result}
            blur_check_dic[element.id] = value
        report_name = str(image_id) + '_blured_check'
        self.image_check_list.append([report_name, blur_check_dic])

        return img, blur_check_dic, test_result
