from tfads_o_builder.feature_types._Base import _Base
import re


# "f47ac10b-58cc-4372-a567-0e02b2c3d479",
# "f47ac10b-58cc-4372-a567-0e02b2c3d4791",
# "f47ac10b58cc4372a5670e02b2c3d479",
# "12345678-1234-1234-1234-123456789012"
class UUID(_Base):
    def __init__(self):
        super().__init__()
        self.field_name = "UUID"
        self.note = "UUID consists of 32 hexadecimal digits, displayed in 5 groups separated by hyphens, in the form 8-4-4-4-12 for a total of 36 characters (32 digits and 4 hyphens)."

    def validateValue(self):
        # If the value is not None then assert
        if self.value is not None:
            # Regular expression pattern for UUID matching
            pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

            # Check if the string matches the pattern
            assert re.match(pattern, self.value), f"{self.value} is not a valid UUID."
