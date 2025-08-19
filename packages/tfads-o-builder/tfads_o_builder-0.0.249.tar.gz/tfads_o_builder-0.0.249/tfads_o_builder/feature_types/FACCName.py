from tfads_o_builder.feature_types._Base import _Base


class FACCName(_Base):
    name_list = [
        "AERIAL CABLE",
        "AMUS PARK STR",
        "ARCH",
        "BUILDING",
        "BUILDING (HANGAR)",
        "COOLING TOWER",
        "CONDUIT",
        "CRANE",
        "DAM",
        "INDUS PLANT",
        "INDUS STRUCTURE",
        "LIGHTHOUSE",
        "LIGHTSHIP",
        "MINING STRUCTURE",
        "MISC NATURAL",
        "MISC MAN-MADE",
        "OPEN STORAGE",
        "PLATFORM",
        "PYLON",
        "PYRAMID",
        "RADAR ANTENNA",
        "SHIP STORAGE",
        "SIGN",
        "SKI JUMP",
        "SMOKESTACK",
        "STADIUM",
        "STORAGE STRUC",
        "TETHERED BALLOON",
        "TANK",
        "TRAN STRUCTURE",
        "TOWER",
        "WASTE PILE",
        "WINDMILL",
    ]

    def __init__(self):
        super().__init__()
        self.field_name = "FACC Name"

    def validateValue(self):
        # If the value is not None then assert that it is in the name list
        if self.value is not None:
            assert (
                self.value in self.name_list
            ), f"The value {self.value} must be in the FACC name list {self.name_list}."
