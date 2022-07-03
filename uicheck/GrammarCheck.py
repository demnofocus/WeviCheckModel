import language_tool_python
import cv2

tool = language_tool_python.LanguageTool('en-US')


class GrammarCheck:
    def __init__(self):
        self.word_list = []

    def grammar_check(self, org_image, text_list):
        print("running grammar checker")
        image = org_image.copy()
        text_dic = {}

        if len(text_list) > 0:
            for element in text_list:
                text_dic.setdefault(element.id, {})
                print("LOOP 1")
                print(element.content)
                match_list = tool.check(element.content)
                print(match_list)
                mistakes = []
                corrections = []
                result = "pass"
                if len(match_list) > 0:
                    text = match_list[0].context
                    mistakes = text[match_list[0].offset:match_list[0].errorLength + match_list[0].offset]
                    corrections.append(match_list[0].replacements[0])
                    if len(mistakes) > 0:
                        result = "fail"
                        cv2.rectangle(image, (element.boundary['left'], element.boundary['top']),
                                      (element.boundary['right'], element.boundary['bottom']), (0, 0, 255), 2)

                value = {"content": element.content, "mistakes": mistakes,
                         "corrections": corrections, "test": result}
                text_dic[element.id] = value

        return image, text_dic
