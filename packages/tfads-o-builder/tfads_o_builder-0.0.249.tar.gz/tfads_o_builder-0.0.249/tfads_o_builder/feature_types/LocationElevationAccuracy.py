from tfads_o_builder.feature_types._Base import _Base


class LocationElevationAccuracy(_Base):
    def __init__(self):
        super().__init__()
        self.field_name = "Location Elevation Accuracy"
        self.note = "In Feet"
