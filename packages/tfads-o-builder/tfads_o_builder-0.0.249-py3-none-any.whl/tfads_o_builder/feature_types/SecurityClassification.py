from tfads_o_builder.feature_types._Base import _Base


class SecurityClassification(_Base):
    def __init__(self):
        super().__init__()
        self.field_name = "Security Classification"
        self.note = 'Always "U"'
        self.default_value = "U"

    def validateValue(self):
        # Assert that the value is "U"
        assert self.value in ["U"], 'The value must be "U".'
