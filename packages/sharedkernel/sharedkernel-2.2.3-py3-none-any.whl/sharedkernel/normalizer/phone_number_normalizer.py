import re
import itertools

"""
    Speech-to-Text Processing Systems for Iranian Dialects:

    Speech-to-text processing systems often struggle to accurately transcribe phone numbers spoken by Iranians. 
    As a result, phone numbers and sequential digits may not be written accurately. 
    This is because individuals sometimes read phone numbers in a shortened or rounded manner. 
    Therefore, it is necessary to design a module that considers all these variations, normalizes the text, 
    and constructs a correct phone number.

    Input and Output Specifications:

    Input: The input will be in str format.
    Output: The output will also be in str format.
    If a phone number is identified, it will be processed and replaced with a corrected version. 
    If no phone number is found, the text will be returned in its original format and structure.
"""


class DigitMapping:
    PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
    WESTERN_DIGITS = "0123456789"
    PHONE_NUMBER_LENGTH_FULL = 11
    PHONE_NUMBER_LENGTH_PARTIAL = 10
    SEVEN_DIGIT_PREFIX_LENGTH = 7
    MIN_NUMBER_FOR_CHECK = 8
    MIN_NUMBER_FOR_GENERATE = 5
    MAX_ITERATIONS_CHECK = 2
    PICK_FIRST_OR_LAST_LENGTH_NUMBER = 4
    MAX_CHAR_CHECK = 30
    MIN_CHAR_CHECK = 7
    FIND_MIN_REPEAT_NUM = 3
    GENERATIVE_VALID_NUMBER_COUNT = 1
    number_words = {
        # Persian
        "صفر": "0",
        "یک": "1",
        "دو": "2",
        "سه": "3",
        "چهار": "4",
        "پنج": "5",
        "شش": "6",
        "هفت": "7",
        "هشت": "8",
        "نه": "9",
    }




# Creating an instance of the DigitMapping class
digit_mapping = DigitMapping()


class PhoneNumberNormalizer:
    # Iranian mobile phone number area code

    def __replace_number_words(self, text):
        pattern = r"(\d+)([a-zA-Z]+)"
        text = re.sub(pattern, r"\1 \2", text)
        for word, digit in digit_mapping.number_words.items():
            text = re.sub(r"\b" + word + r"\b", digit, text, flags=re.IGNORECASE)
        return text

    def __first_to_in_phone_number(self, number_str):
        """
        Identify patterns where a number is followed by "تا" and another number.
        Generate all combinations for numbers preceding and following "تا"
        and return them as a list.
        """
        generated_numbers = []
        ta_pattern = re.compile(r"(\d)(?=\s*تا\s*(\d+))")
        matches = ta_pattern.findall(number_str)

        if matches:
            num1, num2 = matches[0]  # Extract the first match
            combinations = self.__generate_prefix_combinations(num1, num2)
            for combo in combinations:
                repeated_number = combo[1] * int(combo[0])
                pattern = re.escape(f"{combo[0]} تا {combo[1]}")
                generated_numbers.append(re.sub(pattern, repeated_number, number_str))
            return generated_numbers
        return number_str
        
    def __ensureLeadingZero(self, number_string):
        if not number_string.startswith('0'):
            return '0' + number_string
        return number_string

    def __process_to_constructions(self, number_str):
        """
        Process occurrences of 'تا' in the input string to generate possible number combinations.
        This function calls `__first_to_in_phone_number` to handle the first 'تا' occurrence and
        iteratively processes further occurrences if necessary.
        """
        # Start processing the first 'تا'
        #add version 1.6.2 check zero
        number_str = self.__ensureLeadingZero(number_str)
        generated_numbers = self.__first_to_in_phone_number(number_str)

        if isinstance(generated_numbers, str):
            return generated_numbers

        ta_pattern = re.compile(r"(\d+)(?=\s*تا\s*(\d+))")

        i = 0
        while i < digit_mapping.MAX_ITERATIONS_CHECK and len(generated_numbers) >= 2:
            current_number = generated_numbers[i]
            if ta_pattern.search(current_number):
                new_combinations = self.__first_to_in_phone_number(current_number)
                generated_numbers.pop(i)
                generated_numbers[i:i] = new_combinations
            else:
                i += 1
        # Select the appropriate number from the generated list
        #edit version 1.16.2 (dont have zero first)

        selected_number = next(
            (
                num
                for num in generated_numbers
                if len("".join(num.split())) == digit_mapping.PHONE_NUMBER_LENGTH_FULL
            ),
            next(
                (
                    num
                    for num in generated_numbers
                    if len("".join(num.split()))
                    == digit_mapping.PHONE_NUMBER_LENGTH_PARTIAL
                ),
                None,
            ),
        )
        return "".join(selected_number.split()) if selected_number else number_str

    def __generate_prefix_combinations(self, prefix1: str, prefix2: str):
        """
        Generate all possible combinations of the prefixes of `prefix1` and `prefix2`
        using itertools to avoid explicit loops.
        """
        len1, len2 = len(prefix1), len(prefix2)
        indices_product = itertools.product(range(1, len1 + 1), range(1, len2 + 1))

        # Generate the combinations using the indices
        return [(prefix1[:i], prefix2[:j]) for i, j in indices_product]

    def __add_spaces_around_to(self, input_text):
        """
        Ensure "تا" has spaces around it and remove any redundant spaces.
        """
        # Use regular expressions to add spaces around "تا"
        modified_text = re.sub(r"\s*تا\s*", " تا ", input_text)

        return modified_text

    def __generate_next_numbers(self, num):
        str_num = str(num)
        next_numbers = set()
        for i in range(len(str_num) - 1):
            if  i <= digit_mapping.SEVEN_DIGIT_PREFIX_LENGTH :
                current_digit = int(str_num[i])
                next_digit = int(str_num[i + 1])
                new_num = (
                    str_num[:i]
                    + str(int(current_digit) * str(next_digit))
                    + str_num[i + 2 :]
                )
                if digit_mapping.MIN_NUMBER_FOR_GENERATE <= len(new_num) <= digit_mapping.SEVEN_DIGIT_PREFIX_LENGTH:
                    next_numbers.add(str(new_num))       
        return next_numbers

    def __find_seven_chain_numbers(self, start_num):
        current_numbers = {start_num}
        all_numbers = set(current_numbers)
        while len(all_numbers) < digit_mapping.SEVEN_DIGIT_PREFIX_LENGTH:
            next_numbers = set()

            # Using a for loop to generate new numbers
            for num in current_numbers:
                generated_numbers = self.__generate_next_numbers(num)
                new_numbers = generated_numbers - all_numbers
                next_numbers.update(new_numbers)

            if not next_numbers:  # Exit loop if no new numbers are generated
                break

            all_numbers.update(next_numbers)
            current_numbers = next_numbers

            # Early exit if we find any 7-digit number
            if any(
                len(str(num)) == digit_mapping.SEVEN_DIGIT_PREFIX_LENGTH
                for num in next_numbers
            ):
                break
        # Collect all 7-digit numbers and return them sorted
        seven_digit_numbers = sorted(
            num
            for num in all_numbers
            if len(str(num)) == digit_mapping.SEVEN_DIGIT_PREFIX_LENGTH
        )
        return seven_digit_numbers
    #remove 1.6.x
    #def __apply_filter(self, numbers, index, condition):
     #   return (
      #      [num for num in numbers if condition(num)] if len(numbers) >= 2 else numbers
       # )

    def __generate_valid_numbers(self, start_num):
        numbers_list = self.__find_seven_chain_numbers(start_num)
        # If the number list length matches the valid criteria, return the first number
        if len(numbers_list) == digit_mapping.GENERATIVE_VALID_NUMBER_COUNT:
            return numbers_list[0] if numbers_list else start_num

        #start_num_str = str(start_num)
        #unique_count = len(set(start_num_str))
        # Step 1: Filter numbers with the same or one less unique digit count
        # Remove version 1.6.x
        # Apply additional filters only if there are at least 2 candidates remaining

        # Return the first valid number or fallback
        # version 1.16.x remove two generate number
        return (
            numbers_list[0]
            if (numbers_list and len(numbers_list) == 1)
            else start_num)

       

    def __check_area_code(self, input_text):
        """
        Processes the input Persian text to ensure it has a valid area
            code and valid number format.
        """
        # Remove all non-digit characters from the input
        digits_only = re.sub(r"\D", "", input_text)

        # Ensure there are enough digits to process
        if len(digits_only) <= digit_mapping.PICK_FIRST_OR_LAST_LENGTH_NUMBER:
            return digits_only

        # Extract the area code (first 4 digits) and the remaining number
        area_code = digits_only[: digit_mapping.PICK_FIRST_OR_LAST_LENGTH_NUMBER]
        number_part = digits_only[digit_mapping.PICK_FIRST_OR_LAST_LENGTH_NUMBER :]

        # Generate valid number formats based on the remaining part
        valid_number = self.__generate_valid_numbers(number_part)
        # Return the formatted result
        if not valid_number:
            return digits_only
        return f"{area_code}{valid_number}"
   #Remove faction version 1.6.2
   #def __insert_repeated_number(self, number_str):
        """
        Finds the longest repeated sequence in the string and inserts one more instance of the repeated number
        to extend the sequence, without using explicit `for` loops.
        """


    def __add_single_repeating_digit_between_repeats(self, number_str):
        # If the input string is already longer than the partial phone number length, return it as is
        if len(number_str) > digit_mapping.PHONE_NUMBER_LENGTH_PARTIAL:
            return number_str

        # Split the string into two parts: the prefix (e.g., area code) and the remainder
        prefix = number_str[: digit_mapping.PICK_FIRST_OR_LAST_LENGTH_NUMBER]
        number_str = number_str[digit_mapping.PICK_FIRST_OR_LAST_LENGTH_NUMBER :]

        result = []
        i = 0
        repeat_count = 1  # Track the count of consecutive repeating digits

        while i < len(number_str):
            # Check if the next digit is the same as the current one
            if i > 0 and number_str[i] == number_str[i - 1] and int(number_str[i]) != 0:
                repeat_count += 1
            else:
                repeat_count = 1  # Reset the repeat count if the digit changes

            # If we have a sequence of three or more repeating digits
            if repeat_count == digit_mapping.FIND_MIN_REPEAT_NUM:
                # Add a single extra repeating digit and then reset the counter
                result.append(number_str[i])
                repeat_count = 1

            # Add the current digit to the result
            result.append(number_str[i])
            i += 1

        # Concatenate the prefix with the processed result and return the final string
        return prefix + "".join(result)

    def __process_phone_number(self, phone_number):
        """
        Process the Persian phone number string by adding a leading zero if missing,
        removing spaces, and checking the area code.
        """
        # Add leading zero to the area code if it's missing
        phone_number = self.__ensureLeadingZero(phone_number)
        # Remove any spaces from the phone number
        phone_number = "".join(phone_number.split())

        # If the phone number is 10 digits or fewer, validate the area code
        if len(phone_number) <= digit_mapping.PHONE_NUMBER_LENGTH_PARTIAL:
            validated_number = self.__check_area_code(phone_number)
            return validated_number, phone_number

        # If the phone number is longer than expected, return it as-is
        return phone_number, phone_number

    def __clean_and_concatenate_numbers(self, text):
        """
        Process the input text by adding spaces around specific constructions,
        removing unnecessary spaces, handling special constructions, and concatenating numbers.
        """
        # Add spaces around the Persian word "تا"
        text = self.__add_spaces_around_to(text)
        # Remove spaces between numbers
        text = self.__remove_spaces_between_numbers(text)
        """ Handle special constructions like replacing "تا" 
            with corresponding numbers and removing it"""
        text = self.__process_to_constructions(text)
        # Concatenate digits without any spaces between them
        text = re.sub(r"(\d)\s+(\d)", r"\1\2", text)

        return text

    def __english_to_persian(self, text):
        farsi_to_latin = str.maketrans(
            digit_mapping.WESTERN_DIGITS, digit_mapping.PERSIAN_DIGITS
        )
        return text.translate(farsi_to_latin)

    def __persian_to_western(self, persian_number):
        translation_table = str.maketrans(
            digit_mapping.PERSIAN_DIGITS, digit_mapping.WESTERN_DIGITS
        )
        return persian_number.translate(translation_table)

    def __remove_spaces_between_numbers(self, text):
        # This regex will match spaces that are between two digits
        return re.sub(r"(\d)\s+(\d)", r"\1\2", text)

    def __process_patterned_numbers(self, number_sequence):
        if number_sequence is None:
            return number_sequence  
        # Convert Persian numbers to Western (English) numbers
        western_number_sequence = self.__persian_to_western(number_sequence)

        # Remove spaces between numbers to form a continuous sequence
        contiguous_numbers = self.__remove_spaces_between_numbers(western_number_sequence)

        # Clean up any remaining spaces
        clean_number_sequence = "".join(contiguous_numbers.split())

        # Clean and concatenate numbers to form the phone number
        concatenated_numbers = self.__clean_and_concatenate_numbers(clean_number_sequence)
        # Add single repeating digit between repeats in the phone number

        # Process and validate the phone number
        final_number, original_sequence = self.__process_phone_number(concatenated_numbers)
        # Handle case when final_number is a list
        if not isinstance(final_number, list):
            processed_sequence = self.__add_single_repeating_digit_between_repeats(
                final_number
            )   
            return processed_sequence
        processed_sequence = self.__add_single_repeating_digit_between_repeats(
            final_number[0]
        ) 

        return processed_sequence

    def __update_text_with_number(self, text, new_number, old_prefix, new_prefix):
        """
        Update the text by replacing the old prefix with the new prefix and converting it to Persian.
        """
        processed_text = self.__process_patterned_numbers(new_number)
        if len(processed_text) != 11:
            phone_number_proc = "".join(new_number.split())
            processed_text = phone_number_proc
        persian_text = self.__english_to_persian(processed_text)
        #remove v.1.6.2
        #text = re.sub(old_prefix, new_prefix, text, count=1)
        return re.sub(re.escape(' ' * 8), persian_text, text)

    def __update_general_case(self, text, number):
        """
        Handle general number replacement cases and update the text.
        """
        processed_text = self.__process_patterned_numbers(number)
        if len(processed_text) != 11:
            phone_number_proc = "".join(number.split())
            processed_text = phone_number_proc        
        persian_text = self.__english_to_persian(processed_text)
        return re.sub(re.escape(' ' * 8), persian_text, text)

    def __process_number_replacement(self, text, number):
        """
        Process specific number patterns like '۰۹۹' and '۹۹' and replace them with correct forms.
        """
        if ((number[:3]  == "۰۹۹")): #and (number[:4] != "۰۹۹۹")):
            new_number = number.replace("۰۹۹", "۰۹۹۹", 1)
            return self.__update_text_with_number(text, new_number, "۰۹۹", "۰۹۹۹")        
        if ((number[:3]  == "099")): #and (number[:4] != "0999")):
            new_number = number.replace("099", "0999", 1)
            return self.__update_text_with_number(text, new_number, "099", "0999")
        return self.__update_general_case(text, number)
        
    def __normalize_format_text(self, text):
        # اضافه کردن فاصله قبل و بعد از اعداد
        text_with_spaces = re.sub(r'(\d+)', r' \1 ', text)
        # حذف فضاهای اضافی
        formatted_text = re.sub(r'\s+', ' ', text_with_spaces).strip()
        return formatted_text
    @staticmethod
    def normalize(text):
        """
        Normalize phone numbers in the input Persian text by handling specific patterns
        and replacing them with the correct numeric forms.
        """

        # Compile regex pattern to match number patterns
        pattern_regex = re.compile(
            r"((0?[1-9][0-9]{1,3})|(۰?[۱-۹][۰-۹]{1,3}))[\s۰-۹0-9تا]*"
        )

        # Clean up text by removing extra spaces
        cleaned_text = re.sub(r"\s{2,}", " ", text)

        processor = PhoneNumberNormalizer()

        # Replace Persian number words with numeric equivalents
        cleaned_text = processor.__replace_number_words(cleaned_text)
        
        # Find all matching number patterns
        matches = pattern_regex.finditer(cleaned_text)
        
        results = [
            match.group()
            for match in matches
            if digit_mapping.MIN_CHAR_CHECK
            <= len(match.group())
            <= digit_mapping.MAX_CHAR_CHECK
        ]
        # Process each match to handle specific cases
        for result in results:
            digits = re.findall(r"\d", result)
            if (
                digit_mapping.MIN_NUMBER_FOR_GENERATE
                <= len(digits)
                <= digit_mapping.PHONE_NUMBER_LENGTH_PARTIAL
            ):

                cleaned_text = cleaned_text.replace(result, ' ' * 8)
                cleaned_text = processor.__process_number_replacement(cleaned_text, result)
                #new_version 2.0 fixed bug space between number and word
        cleaned_text = processor.__normalize_format_text(cleaned_text)
        return cleaned_text if results else text