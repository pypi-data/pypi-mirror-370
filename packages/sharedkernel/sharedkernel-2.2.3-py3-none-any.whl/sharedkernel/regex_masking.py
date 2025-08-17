import re
from persian_tools import national_id, phone_number
from persian_tools.bank import card_number, sheba

class RegexMaskingBuilder:
    def __init__(self, message: str, replace_str: str = ""):
        self.message = message
        self.replace_str = replace_str
    
    def with_card_no(self):
        pattern_16_digits = r'(?<!\d)\d{16}(?!\d)'
        pattern_4_4_4_4 = r'(?<!\d)\d{4}\W?\d{4}\W?\d{4}\W?\d{4}(?!\d)'

        find_patterns = re.findall(f"{pattern_16_digits}|{pattern_4_4_4_4}", self.message)

        for matched_pattern in find_patterns:
            clean_pattern = matched_pattern.replace("-", "") if "-" in matched_pattern else matched_pattern
            if len(clean_pattern) == 16 and card_number.validate(clean_pattern):
                self.message = re.sub(re.escape(matched_pattern), self.replace_str, self.message)
            elif card_number.validate(clean_pattern):
                self.message = re.sub(re.escape(matched_pattern), self.message_sub(len(clean_pattern)), self.message)

        return self
    
    def with_national_id(self):
        pattern_10_digits = r'(?<!\d)\d{10}(?!\d)'

        id_matches = re.findall(pattern_10_digits, self.message)
        if not id_matches:
            return self
        
        for matched_id in id_matches:
            if national_id.validate(matched_id):
                self.message = re.sub(re.escape(matched_id), self.replace_str, self.message)
        
        return self

    def with_mobile_no(self):
        pattern = r'(?<!\d)\d{10,12}(?!\d)'

        matches = re.findall(pattern, self.message)

        if not matches:
            return self

        for match in matches:
            if phone_number.validate(match):
                self.message = re.sub(re.escape(match), self.replace_str, self.message)
        
        return self
    
    def with_sheba(self):
        sheba_patterns = [r'(?<!\d)\d{24}(?!\d)', r'IR\d{24}(?!\d)']
        sheba_matches = re.findall('|'.join(sheba_patterns), self.message)

        if not sheba_matches:
            return self

        for sheba_number in sheba_matches:
            if sheba.validate(sheba_number):
                message = re.sub(re.escape(sheba_number), self.replace_str, message)

        return self
    
    def with_phone_no(self):
        phone_number_pattern1 = r"(?<!\d)^0[0-9]{2,}-[0-9]{8}$(?!\d)"
        phone_number_pattern2 = r"(?<!\d)^0[0-9]{2,}[0-9]{8}$(?!\d)"
        combined_pattern = re.compile(f"{phone_number_pattern1}|{phone_number_pattern2}")
        self.message = combined_pattern.sub(self.replace_str, self.message)
        return self
    
    def with_cvv2(self):
        self.message = re.sub(r'(?<!\d)\d{3}(?!\d)', self.replace_str, self.message)
        return self

    def with_peigiri_no(self):
        patterns = [
            r'(?<!\d)\d{6}(?!\d)',
            r'(?<!\d)\d{12}(?!\d)',
            r'(?<!\d)\d{20}(?!\d)'
        ]
        for pattern in patterns:
            self.message = re.sub(pattern, self.replace_str, self.message)
        return self
    
    def with_account_no(self):
        pattern = r'(?<!\d)\d{12,16}(?!\d)'
        
        self.message = re.sub(pattern, self.replace_str, self.message)
        return self
    
    def build(self):
        return self.message