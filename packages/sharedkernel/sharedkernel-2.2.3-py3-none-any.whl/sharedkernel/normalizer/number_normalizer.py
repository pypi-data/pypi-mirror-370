class NumberNormalizer:
    @staticmethod
    def persian_number(text):
        persian_numbers = "۰۱۲۳۴۵۶۷۸۹"
        english_numbers = "0123456789"
        translation_table = str.maketrans(persian_numbers, english_numbers)
        return text.translate(translation_table)

