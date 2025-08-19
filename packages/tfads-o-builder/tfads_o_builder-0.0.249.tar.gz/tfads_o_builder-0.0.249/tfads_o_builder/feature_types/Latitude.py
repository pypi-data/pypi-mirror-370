from tfads_o_builder.feature_types._Base import _Base


class Latitude(_Base):
    def __init__(self):
        super().__init__()
        self.field_name = "Latitude"
        self.note = "(-)Decimal Degrees (example= -17.50982743)"

    def castValue(self):
        # Cast the value as a float
        return float(self.value)

    def validateValue(self):
        # Assert the value is a latitude
        assert -90 <= self.value <= 90, "The value must be a valid latitude."
