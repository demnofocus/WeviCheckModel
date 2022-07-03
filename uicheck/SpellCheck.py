from spellchecker import SpellChecker

import cv2

spell = SpellChecker()


def break_to_words(list):
    only_word_list = {}
    filtered = {}
    for text in list:
        only_word_list.setdefault(text.id, [])
        split_list = text.content.split()
        for one_word in split_list:
            if len(one_word) > 1 or one_word == "i":
                only_word_list[text.id].append(one_word)

    for set_id in only_word_list:
        filtered.setdefault(set_id, [])
        for one_word in only_word_list[set_id]:
            special = '-_,.!?$%:&+#(^)\'""_;|\\/~*0123456789'
            for value in special:
                one_word = one_word.replace(value, "")
            filtered[set_id].append(one_word)
    return filtered


class SpellCheck:
    def __init__(self):
        self.word_list = []

    def spell_check(self, org_image, text_list):
        words_dic = break_to_words(text_list)

        wrong_words_dic = {}
        wrong_ids = []

        if len(words_dic) > 0:
            for set_id in words_dic:
                wrong_words_dic.setdefault(set_id, {})
                misspelled = spell.unknown(words_dic[set_id])
                for wrong_word in misspelled:
                    corrected = spell.correction(wrong_word)
                    suggested = spell.candidates(wrong_word)
                    suggestions = str(suggested).replace("{", "").replace("}", "")
                    value = {"word": wrong_word, "corrected": corrected,
                             "suggestions": suggestions,
                             "test": "fail"}

                    wrong_words_dic[set_id] = value

                    if set_id not in wrong_ids:
                        wrong_ids.append(set_id)

        image = org_image.copy()

        if len(text_list) > 0:
            for element in text_list:
                if element.id in wrong_ids:
                    cv2.rectangle(image, (element.boundary['left'], element.boundary['top']),
                                  (element.boundary['right'], element.boundary['bottom']), (0, 0, 255), 2)

        return image, wrong_words_dic
