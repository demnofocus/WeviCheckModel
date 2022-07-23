import language_tool_python
import cv2

tool = language_tool_python.LanguageTool('en-US')


class GrammarCheck:
    def __init__(self):
        self.word_list = []

    def grammar_check(self, org_image, text_list):
        image = org_image.copy()
        text_dic = {}
        count = 1
        test_result = "pass"
        if len(text_list) > 0:
            for element in text_list:
                text_dic.setdefault(element.id, {})

                match_list = tool.check(element.content)
                mistakes = []
                corrections = []
                result = "pass"

                num = 0
                if len(match_list) > 0:
                    text = match_list[0].context
                    mistakes = text[match_list[0].offset:match_list[0].errorLength + match_list[0].offset]
                    corrections.append(match_list[0].replacements[0])
                    if len(mistakes) > 0:
                        result = "fail"
                        test_result = "fail"
                        cv2.putText(image, "{}: {}".format("Issue", count),
                                    (element.boundary['left'], element.boundary['bottom']),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
                        cv2.rectangle(image, (element.boundary['left'], element.boundary['top']),
                                      (element.boundary['right'], element.boundary['bottom']), (0, 0, 255), 2)
                        num = count
                        count = count + 1

                value = {"num": num, "content": element.content, "mistakes": mistakes,
                         "corrections": corrections, "test": result}
                text_dic[element.id] = value

        return image, text_dic, test_result
