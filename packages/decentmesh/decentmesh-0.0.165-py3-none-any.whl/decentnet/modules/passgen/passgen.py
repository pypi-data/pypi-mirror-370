import secrets
import string

from decentnet.consensus.byte_conversion_constants import ENDIAN_TYPE


class SecurePasswordGenerator:
    def __init__(self, length=40, digits=True, upper=True, lower=True, special=True):
        self.length = length
        self.digits = digits
        self.upper = upper
        self.lower = lower
        self.special = special

    def generate(self):
        # Validate length
        if not isinstance(self.length, int) or self.length <= 0:
            raise ValueError("Password length must be a positive integer")

        char_sets = []

        # Collect possible character sets based on flags
        if self.digits:
            char_sets.append(string.digits)
        if self.upper:
            char_sets.append(string.ascii_uppercase)
        if self.lower:
            char_sets.append(string.ascii_lowercase)
        if self.special:
            char_sets.append(string.punctuation)

        if not char_sets:
            raise ValueError("At least one character type must be selected")

        # Flatten all characters into a single pool for random selection
        all_characters = ''.join(char_sets)

        # Ensure we can meet the requirement of including at least one char from each chosen set
        if self.length < len(char_sets):
            raise ValueError("Password length too short to include all chosen character types")

        # Introduce a random seed step: get a random seed from secrets
        # and use it to rotate the all_characters string
        seed_data = secrets.token_bytes(64)  # 512 bits of randomness
        seed_int = int.from_bytes(seed_data, ENDIAN_TYPE)
        # Rotate the character pool by a random offset
        offset = seed_int % len(all_characters)
        all_characters = all_characters[offset:] + all_characters[:offset]

        # Pick one guaranteed character from each selected set to ensure complexity
        password_chars = [secrets.choice(cset) for cset in char_sets]

        # Fill the rest with random characters from the entire pool
        remaining_length = self.length - len(password_chars)
        password_chars.extend(secrets.choice(all_characters) for _ in range(remaining_length))

        # Shuffle the resulting list of characters to ensure no pattern
        # SystemRandom is inherently cryptographically secure
        secrets.SystemRandom().shuffle(password_chars)

        # Join and return the final password
        password = ''.join(password_chars)
        return password
