from datetime import datetime
from tfads_o_builder.feature_types._Base import _Base


class CompilationDate(_Base):
    def __init__(self):
        super().__init__()
        self.field_name = "Compilation Date / Initial Record Date"
        self.note = '"YYYYMMDD" (example=19990204)'

    def validateValue(self):
        # Assert that self.value is not None
        assert self.value is not None, "The CompilationDate is required."

        # Assert that the length of the value is 8
        assert len(self.value) == 8, "The value must be 8 characters in length."

        # Assert that the value is a valid date
        try:
            datetime.strptime(self.value, "%Y%m%d")
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYYMMDD")
