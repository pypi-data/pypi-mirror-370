from tfads_o_builder.feature_types._Base import _Base


class TransactionType(_Base):
    code_list = ["D", "N", "R", "S", "V", "X"]

    def __init__(self):
        super().__init__()
        self.field_name = "Transaction Type / Code"

    def validateValue(self):
        # If the value is not None then assert that it is in the code list
        if self.value is not None:
            assert (
                self.value in self.code_list
            ), f"The value {self.value} must be in the Transaction Type / Code list {self.code_list}."
