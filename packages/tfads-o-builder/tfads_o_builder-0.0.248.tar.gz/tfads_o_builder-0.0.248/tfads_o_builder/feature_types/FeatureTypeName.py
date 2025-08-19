from tfads_o_builder.feature_types._Base import _Base


class FeatureTypeName(_Base):
    name_list = [
        "Aerial Cable",
        "Amus Park Str",
        "Arch",
        "Building",
        "Building (Hangar)",
        "Bridge",
        "Cooling Tower",
        "Conduit",
        "Crane",
        "Dam",
        "Indus Plant",
        "Indus Structure",
        "Lightship",
        "Lighthouse",
        "Mining Structure",
        "Misc Man-Made",
        "Misc Natural",
        "Open Storage",
        "Platform",
        "Pylon",
        "Pyramid",
        "Radar Antenna",
        "Ship Storage",
        "Sign",
        "Ski Jump",
        "Smokestack",
        "Stadium",
        "Storage Struc",
        "Tank",
        "Tethered Balloon",
        "Tower",
        "Tran Structure",
        "Waste Pile",
        "Windmill",
    ]

    def __init__(self):
        super().__init__()
        self.field_name = "Feature Type Name"

    def validateValue(self):
        # If the value is not None then assert that it is in the name list
        if self.value is not None:
            assert (
                self.value in self.name_list
            ), f"The value {self.value} must be in the FACC name list {self.name_list}."
