from tfads_o_builder.feature_types._Base import _Base


class SingleMultipleFlag(_Base):
    def __init__(self):
        super().__init__()
        self.field_name = "Single Multiple Flag"
        self.note = '"S" or "M"'
        self.default_value = "S"

    def validateValue(self):
        # Assert that the value is either "S" or "M"
        assert self.value in ["S", "M"], 'The value must be either "S" or "M".'
