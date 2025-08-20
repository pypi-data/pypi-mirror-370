import math
import string
import unittest

from decentnet.modules.passgen.passgen import SecurePasswordGenerator


class TestPasswordGenerator(unittest.TestCase):
    def test_password_content(self):
        # Test parameters
        length = 40
        has_digits = True
        has_upper = True
        has_lower = True
        has_special = True

        # Instantiate the password generator
        generator = SecurePasswordGenerator(length, has_digits, has_upper, has_lower,
                                            has_special)

        # Generate the password
        password = generator.generate()

        # Assert conditions
        if has_digits:
            self.assertTrue(any(char in string.digits for char in password),
                            "Password lacks digits")
        if has_upper:
            self.assertTrue(any(char in string.ascii_uppercase for char in password),
                            "Password lacks uppercase letters")
        if has_lower:
            self.assertTrue(any(char in string.ascii_lowercase for char in password),
                            "Password lacks lowercase letters")
        if has_special:
            self.assertTrue(any(char in string.punctuation for char in password),
                            "Password lacks special characters")

        # Assert length
        self.assertEqual(len(password), length,
                         "Password length does not match the specified length")
        print(password)

    def test_password_entropy(self):
        # Test parameters
        length = 40
        has_digits = True
        has_upper = True
        has_lower = True
        has_special = True

        # Instantiate the password generator
        generator = SecurePasswordGenerator(length, has_digits, has_upper, has_lower,
                                            has_special)
        password = generator.generate()

        # Determine character set size based on selected parameters
        char_pool = ''
        if has_digits:
            char_pool += string.digits
        if has_upper:
            char_pool += string.ascii_uppercase
        if has_lower:
            char_pool += string.ascii_lowercase
        if has_special:
            char_pool += string.punctuation

        actual_charset = set(password)
        charset_size = len(set(char_pool))
        actual_charset_size = len(actual_charset)

        # Theoretical entropy (assuming uniform distribution)
        theoretical_entropy = length * math.log2(charset_size)

        # Actual entropy approximation based on character diversity
        actual_entropy = length * math.log2(actual_charset_size) if actual_charset_size > 1 else 0

        # Assert that theoretical entropy meets the threshold
        self.assertTrue(theoretical_entropy >= 128,
                        f"Theoretical password entropy too low: {theoretical_entropy:.2f} bits, should be >= 128 bits")

        # Assert that actual entropy meets the threshold
        self.assertTrue(actual_entropy >= 128,
                        f"Actual password entropy too low: {actual_entropy:.2f} bits, should be >= 128 bits")

        charset_size = len(set(char_pool))
        # Theoretical entropy (assuming uniform distribution)
        entropy = length * math.log2(charset_size)

        # Assert that entropy is above a strong threshold, for example 128 bits
        self.assertTrue(entropy >= 128,
                        f"Password entropy too low: {entropy:.2f} bits, should be >= 128 bits")

    def test_password_strength_heuristics(self):
        # Test parameters
        length = 40
        has_digits = True
        has_upper = True
        has_lower = True
        has_special = True

        # Instantiate the password generator
        generator = SecurePasswordGenerator(length, has_digits, has_upper, has_lower,
                                            has_special)
        password = generator.generate()
        # Check for no long runs of the same character
        current_run_char = None
        current_run_length = 0

        for ch in password:
            if ch == current_run_char:
                current_run_length += 1
            else:
                current_run_char = ch
                current_run_length = 1

            if current_run_length > 5:  # Arbitrary threshold: no more than 5 identical chars in a row
                self.fail(
                    "Password contains a long run of identical characters, potentially reducing strength")

        # Additional heuristic checks could be added here.
        # For now, we'll just ensure that we have at least 3 different character types present
        # when we've requested all four. This should be guaranteed by previous tests, but let's assert it:
        types_count = sum([
            any(c in string.digits for c in password) if has_digits else 0,
            any(c in string.ascii_uppercase for c in password) if has_upper else 0,
            any(c in string.ascii_lowercase for c in password) if has_lower else 0,
            any(c in string.punctuation for c in password) if has_special else 0
        ])

        self.assertTrue(types_count >= 3,
                        "Password does not contain at least three of the required character sets, reducing its complexity")


if __name__ == '__main__':
    unittest.main()
