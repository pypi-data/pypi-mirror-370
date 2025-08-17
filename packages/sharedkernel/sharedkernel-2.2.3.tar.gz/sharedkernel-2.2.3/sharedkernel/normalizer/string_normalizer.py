class StringNormalizer:
    @staticmethod
    def persian_string_normalizer(text):
        arabic_to_persian_map = {
            "ا": "ا", "ب": "ب", "ت": "ت", "ث": "ث", "ج": "ج", "ح": "ح", "خ": "خ", "د": "د",
            "ذ": "ذ", "ر": "ر", "ز": "ز", "ژ": "ژ", "س": "س", "ش": "ش", "ص": "ص", "ض": "ض",
            "ط": "ط", "ظ": "ظ", "ع": "ع", "غ": "غ", "ف": "ف", "ق": "ق", "ک": "ک", "گ": "گ",
            "ل": "ل", "م": "م", "ن": "ن", "و": "و", "ه": "ه", "ی": "ی", "ء": "ء", "ؤ": "ؤ",
            "إ": "ا", "أ": "ا", "آ": "آ", "ئ": "ی", "ى": "ی", "ة": "ه", "ة": "ه",  "ي" : "ی" ,"ك" : "ک"
        }

        for arabic_char, persian_char in arabic_to_persian_map.items():
            text = text.replace(arabic_char, persian_char)
        
        return text