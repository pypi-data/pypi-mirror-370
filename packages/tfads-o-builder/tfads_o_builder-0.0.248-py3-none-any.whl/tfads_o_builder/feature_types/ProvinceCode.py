from tfads_o_builder.feature_types._Base import _Base


class ProvinceCode(_Base):
    code_list = [
        1,
        2,
        4,
        5,
        6,
        8,
        9,
        10,
        11,
        12,
        13,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
        28,
        29,
        30,
        31,
        32,
        33,
        34,
        35,
        36,
        37,
        38,
        39,
        40,
        41,
        42,
        44,
        45,
        46,
        47,
        48,
        49,
        50,
        51,
        53,
        54,
        55,
        56,
    ]

    def __init__(self):
        super().__init__()
        self.field_name = "Province Code"

    def validateValue(self):
        # If the value is not None then assert that it is in the code list
        if self.value is not None:
            assert (
                self.value in self.code_list
            ), f"The value {self.value} must be in the Province Code list {self.code_list}."
