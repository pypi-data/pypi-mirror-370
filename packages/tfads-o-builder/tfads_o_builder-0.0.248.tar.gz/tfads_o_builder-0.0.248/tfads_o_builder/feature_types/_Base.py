class _Base:
    def __init__(self):
        self.format = "Char"
        self.field_name = None
        self.note = None
        self.value = None
        self.default_value = None

    """
    Sets the value of the feature type.
    """

    def setValue(self, value):
        # Set the value
        self.value = value

        # Set the default value using the __setDefaultValue function
        self.__setDefaultValue()

        # Cast the value using the castValue function
        self.castValue()

        # Validate the value using the validateValue function
        self.validateValue()

        # Return self
        return self

    """
    Returns the value of the feature type.
    """

    def getValue(self):
        # Set the default value using the __setDefaultValue function
        self.__setDefaultValue()

        # Validate the value using the validateValue function
        self.validateValue()

        # If the value is None, then return an empty string
        if self.value is None:
            return ""

        # Else return the value
        return self.value

    """
    Sets the default value of the feature type.
    """

    def __setDefaultValue(self):
        # If the value is None, then set the value to an empty string
        if self.value is None:
            self.value = self.default_value

    """
    Casts the value of the feature type.
    """

    def castValue(self):
        return str(self.value)

    """
    Validates the value of the feature type.
    """

    def validateValue(self):
        assert True == True

    """
    Returns the field name of the feature type.
    """

    def getFieldName(self):
        # If field_name is None, then raise an error
        if self.field_name is None:
            raise AttributeError("The field_name must be set.")

        return self.field_name
