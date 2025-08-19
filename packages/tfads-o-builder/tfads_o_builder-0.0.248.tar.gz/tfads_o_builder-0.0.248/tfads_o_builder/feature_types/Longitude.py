from tfads_o_builder.feature_types._Base import _Base


class Longitude(_Base):
    def __init__(self):
        super().__init__()
        self.field_name = "Longitude"
        self.note = "(-)Decimal Degrees (example = 177.30485762)"

    def castValue(self):
        # Cast the value as a float
        return float(self.value)

    def validateValue(self):
        # Assert the value is a longitude
        assert -180 <= self.value <= 180, "The value must be a valid longitude."
