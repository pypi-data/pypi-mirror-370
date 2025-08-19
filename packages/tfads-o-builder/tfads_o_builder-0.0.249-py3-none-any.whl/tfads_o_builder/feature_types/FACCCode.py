from tfads_o_builder.feature_types._Base import _Base


class FACCCode(_Base):
    code_list = [
        "AA040",
        "AB000",
        "AC000",
        "AC010",
        "AC020",
        "AD010",
        "AD020",
        "AD030",
        "AF010",
        "AF020",
        "AF030",
        "AF040",
        "AF050",
        "AF070",
        "AF080",
        "AH050",
        "AJ050",
        "AJ051",
        "AK020",
        "AK150",
        "AK160",
        "AL015",
        "AL050",
        "AL073",
        "AL110",
        "AL130",
        "AL240",
        "AL241",
        "AM010",
        "AM020",
        "AM030",
        "AM070",
        "AM080",
        "AQ020",
        "AQ040",
        "AQ050",
        "AQ055",
        "AQ060",
        "AQ110",
        "AQ113",
        "AT005",
        "AT006",
        "AT010",
        "AT040",
        "AT041",
        "AT050",
        "AT070",
        "AT080",
        "BB020",
        "BC050",
        "BC070",
        "BD110",
        "BH010",
        "BI020",
        "BI050",
        "GA035",
        "GB040",
        "GB220",
        "GB221",
        "GB230",
    ]

    def __init__(self):
        super().__init__()
        self.field_name = "FACC"

    def validateValue(self):
        # If the value is not None then assert that it is in the code list
        if self.value is not None:
            assert (
                self.value in self.code_list
            ), f"The value {self.value} must be in the FACC code list {self.code_list}."
