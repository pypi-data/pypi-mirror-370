from tfads_o_builder.feature_types._Base import _Base


class ObstructionHeightAGL(_Base):
    def __init__(self):
        super().__init__()
        self.field_name = "Obstruction Height AGL"
        self.note = "In Feet"
