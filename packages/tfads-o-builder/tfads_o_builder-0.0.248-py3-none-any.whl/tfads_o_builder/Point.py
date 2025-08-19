from tfads_o_builder.feature_types.ActiveDeletedCode import ActiveDeletedCode
from tfads_o_builder.feature_types.CompilationDate import CompilationDate
from tfads_o_builder.feature_types.ControlReleasabilityCode import (
    ControlReleasabilityCode,
)
from tfads_o_builder.feature_types.CoordinatePrecisionFlag import (
    CoordinatePrecisionFlag,
)
from tfads_o_builder.feature_types.CountryCode import CountryCode
from tfads_o_builder.feature_types.DeficiencyCode import DeficiencyCode
from tfads_o_builder.feature_types.DeletingOrganization import DeletingOrganization
from tfads_o_builder.feature_types.DerivingOrganization import DerivingOrganization
from tfads_o_builder.feature_types.FACCCode import FACCCode
from tfads_o_builder.feature_types.FACCName import FACCName
from tfads_o_builder.feature_types.FeatureTypeName import FeatureTypeName
from tfads_o_builder.feature_types.HeightAGLAccuracy import HeightAGLAccuracy
from tfads_o_builder.feature_types.HeightAMSLAccuracy import HeightAMSLAccuracy
from tfads_o_builder.feature_types.HorizontalAccuracy import HorizontalAccuracy
from tfads_o_builder.feature_types.HorizontalDatum import HorizontalDatum
from tfads_o_builder.feature_types.Latitude import Latitude
from tfads_o_builder.feature_types.Lights import Lights
from tfads_o_builder.feature_types.LocationElevation import LocationElevation
from tfads_o_builder.feature_types.LocationElevationAccuracy import (
    LocationElevationAccuracy,
)
from tfads_o_builder.feature_types.Longitude import Longitude
from tfads_o_builder.feature_types.MultipleNumber import MultipleNumber
from tfads_o_builder.feature_types.FeatureTypeCode import FeatureTypeCode
from tfads_o_builder.feature_types.ObstructionHeightAGL import ObstructionHeightAGL
from tfads_o_builder.feature_types.ObstructionHeightAMSL import ObstructionHeightAMSL
from tfads_o_builder.feature_types.OriginalID import OriginalID
from tfads_o_builder.feature_types.OutputRemarks import OutputRemarks
from tfads_o_builder.feature_types.PreviousVOIdentifierCode import (
    PreviousVOIdentifierCode,
)
from tfads_o_builder.feature_types.ProcessCode import ProcessCode
from tfads_o_builder.feature_types.ProvinceCode import ProvinceCode
from tfads_o_builder.feature_types.RevisionDate import RevisionDate
from tfads_o_builder.feature_types.SecurityClassification import SecurityClassification
from tfads_o_builder.feature_types.SingleMultipleFlag import SingleMultipleFlag
from tfads_o_builder.feature_types.SourceDate import SourceDate
from tfads_o_builder.feature_types.SurfaceMaterialCode import SurfaceMaterialCode
from tfads_o_builder.feature_types.TransactionType import TransactionType
from tfads_o_builder.feature_types.UUID import UUID
from tfads_o_builder.feature_types.VOIdentification import VOIdentification
from tfads_o_builder.feature_types.VOSequenceNumber import VOSequenceNumber
from tfads_o_builder.feature_types.ValidationCode import ValidationCode
from tfads_o_builder.feature_types.WACINNR import WACINNR
from tfads_o_builder.feature_types.WACNumber import WACNumber


class Point:
    # tab => class type
    # e.g. 1 => VOSequenceNumber
    tab_type_mapping = {
        1: VOSequenceNumber(),
        2: VOIdentification(),
        3: CountryCode(),
        4: ProvinceCode(),
        5: WACNumber(),
        6: Latitude(),
        7: Longitude(),
        8: FeatureTypeCode(),
        9: FeatureTypeName(),
        10: ObstructionHeightAGL(),
        11: ObstructionHeightAMSL(),
        12: LocationElevation(),
        13: HorizontalDatum(),
        14: HeightAGLAccuracy(),
        15: HeightAMSLAccuracy(),
        16: LocationElevationAccuracy(),
        17: HorizontalAccuracy(),
        18: DerivingOrganization(),
        19: SurfaceMaterialCode(),
        20: SingleMultipleFlag(),
        21: MultipleNumber(),
        22: ProcessCode(),
        23: Lights(),
        24: SourceDate(),
        25: RevisionDate(),
        26: CompilationDate(),
        27: SecurityClassification(),
        28: CoordinatePrecisionFlag(),
        29: ValidationCode(),
        30: TransactionType(),
        31: ControlReleasabilityCode(),
        32: DeletingOrganization(),
        33: ActiveDeletedCode(),
        34: DeficiencyCode(),
        35: PreviousVOIdentifierCode(),
        36: OriginalID(),
        37: WACINNR(),
        38: OutputRemarks(),
        39: FACCCode(),
        40: FACCName(),
        41: UUID(),
    }

    # class type => tab
    # e.g. VOSequenceNumber => 1
    type_tab_mapping = {}

    def __init__(self) -> None:
        # Initialize the self.type_tab_mapping setting it to the reverse of the self.tab_type_mapping but the key being the class name
        self.type_tab_mapping = {
            v.__class__.__name__: k for k, v in self.tab_type_mapping.items()
        }

    def __getattr__(self, called_prefix_fn_name=""):
        def default_function(*args, **kwargs):
            # If called_fn_name does not start with "set_", then return None
            if not called_prefix_fn_name.startswith("set") and not called_prefix_fn_name.startswith("get"):
                raise AttributeError(
                    f"The attribute {called_prefix_fn_name} must start with 'set' or 'get'"
                )

            # Trim the "set_" from the called_fn_name
            called_fn_name = called_prefix_fn_name[3:]

            # Check if called_fn_name is in self.remapped_mappings
            if called_fn_name not in self.type_tab_mapping:
                raise AttributeError(f"The attribute {called_fn_name} does not exist.")

            # Get the class from the self.tab_type_mapping
            class_instance = self.tab_type_mapping[
                self.type_tab_mapping[called_fn_name]
            ]

            if called_prefix_fn_name.startswith("get"):
                # Call the getValue function on the instance of the class
                return class_instance.getValue()
            
            if called_prefix_fn_name.startswith("set"):
            # Set the value on the instance of the class
                class_instance.setValue(*args, **kwargs)

        return default_function

    def getFieldNames(self) -> list:
        # Create a list to return
        return_list = []

        # For each tab in the tab_type_mapping, call the getValue function
        for tab, class_instance in self.tab_type_mapping.items():
            return_list.append(class_instance.getFieldName())

        # Return the list
        return return_list

    def getRowData(self):
        # Create a dictionary to return
        return_dict = {}

        # For each tab in the tab_type_mapping, call the getValue function
        for tab, class_instance in self.tab_type_mapping.items():
            return_dict[class_instance.getFieldName()] = class_instance.getValue()

        # Return the dictionary
        return return_dict
