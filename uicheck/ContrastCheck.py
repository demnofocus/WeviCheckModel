import cv2
import pandas as pd

index = ["color", "color_name", "hex", "R", "G", "B"]
csv = pd.read_csv('data/colors.csv', names=index, header=None)


def get_relative_luminance(red, green, blue):

    R, G, B = float(red) / 255, float(green) / 255, float(blue) / 255

    if R <= 0.03928:
        r = R/12.92
    else:
        r = ((R+0.055)/1.055) ** 2.4

    if G <= 0.03928:
        g = G/12.92
    else:
        g = ((G+0.055)/1.055) ** 2.4

    if B <= 0.03928:
        b = B/12.92
    else:
        b = ((R+0.055)/1.055) ** 2.4

    return 0.2126*r + 0.7152*g + 0.0722*b


def get_color(R, G, B):
    minimum = 10000
    cname = ""
    for i in range(len(csv)):
        d = abs(R - int(csv.loc[i, "R"])) + abs(G - int(csv.loc[i, "G"])) + abs(B - int(csv.loc[i, "B"]))
        if d <= minimum:
            minimum = d
            cname = csv.loc[i, "color_name"]
    return cname


class ContrastCheck:
    def __init__(self):
        self.contrast_check_list = {}
        self.report_image_list = []

    def check_text_contrast(self, image_id, text_list, image_org):
        image = image_org.copy()
        text_dic = {}

        if len(text_list) > 0:
            count = 1
            for element in text_list:
                text_dic.setdefault(element.id, {})
                x_min = element.boundary['left']
                y_min = element.boundary['bottom']
                x_max = element.boundary['right']
                y_max = element.boundary['top']
                img = image[y_min:y_max, x_min:x_max]

                b_min = img[..., 0].min()
                g_min = img[..., 1].min()
                r_min = img[..., 2].min()

                b_max = img[..., 0].max()
                g_max = img[..., 1].max()
                r_max = img[..., 2].max()

                content = element.content
                min_color = get_color(r_min, g_min, b_min)
                max_color = get_color(r_max, g_max, b_max)

                l1 = get_relative_luminance(r_max, g_max, b_max)
                l2 = get_relative_luminance(r_min, g_min, b_min)
                contrast_level = (l1 + 0.05) / (l2 + 0.05)
                # "position": (x_max, y_max), "min_rgb": (r_min, g_min, b_min),
                # "max_rgb": (r_max, g_max, b_max),
                value = {"content": content, "min_color": min_color,
                         "max_color": max_color, "contrast_lvl": contrast_level, "expected": 4.5, "test": "pass"}

                text_dic[element.id] = value
                if contrast_level < 4.5:
                    cv2.putText(image, str(count) + "(lvl" + str(contrast_level) + " min:" + min_color + " max:"
                                + max_color + ")", (x_min, y_min), 2, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
                    cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)
                    print(text_dic[element.id]["content"])
                    text_dic[element.id]["test"] = "fail"

                count += 1

        self.contrast_check_list = text_dic.copy()

        return image, text_dic
