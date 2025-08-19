from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BaseData(_message.Message):
    __slots__ = ("addons", "standards", "general_settings")
    class Addons(_message.Message):
        __slots__ = ("has_effective_section_properties_active",)
        HAS_EFFECTIVE_SECTION_PROPERTIES_ACTIVE_FIELD_NUMBER: _ClassVar[int]
        has_effective_section_properties_active: bool
        def __init__(self, has_effective_section_properties_active: bool = ...) -> None: ...
    class Standards(_message.Message):
        __slots__ = ("effective_section_standard",)
        class EffectiveSectionStandard(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            EFFECTIVE_SECTION_STANDARD_EN_1993_1_1_AND_EN_1993_1_5: _ClassVar[BaseData.Standards.EffectiveSectionStandard]
            EFFECTIVE_SECTION_STANDARD_EN_1993_1_3_COLD_FORMED: _ClassVar[BaseData.Standards.EffectiveSectionStandard]
            EFFECTIVE_SECTION_STANDARD_EN_1999_1_1_ALUMINUM: _ClassVar[BaseData.Standards.EffectiveSectionStandard]
        EFFECTIVE_SECTION_STANDARD_EN_1993_1_1_AND_EN_1993_1_5: BaseData.Standards.EffectiveSectionStandard
        EFFECTIVE_SECTION_STANDARD_EN_1993_1_3_COLD_FORMED: BaseData.Standards.EffectiveSectionStandard
        EFFECTIVE_SECTION_STANDARD_EN_1999_1_1_ALUMINUM: BaseData.Standards.EffectiveSectionStandard
        EFFECTIVE_SECTION_STANDARD_FIELD_NUMBER: _ClassVar[int]
        effective_section_standard: BaseData.Standards.EffectiveSectionStandard
        def __init__(self, effective_section_standard: _Optional[_Union[BaseData.Standards.EffectiveSectionStandard, str]] = ...) -> None: ...
    class GeneralSettings(_message.Message):
        __slots__ = ("tolerance_for_points", "tolerance_for_lines", "tolerance_for_planes", "tolerance_for_directions", "solver_model", "stress_position_on_element", "tolerance_for_straight_subpanels", "is_generated_curved_subpanels_ec9", "has_neglect_moments_due_to_centroid_shift", "effective_max_iteration_count", "maximum_difference_between_iterations", "has_consider_effective_section_annex_e", "has_consider_influence_of_transverse_weld", "has_material_definition_active", "has_plastic_capacity_design_active", "has_concrete_reinforcement", "buckling_curve_y", "buckling_curve_z", "type_of_welding", "us_spelling_of_properties", "stress_smoothing_to_avoid_singularities", "manufacturing_type")
        class SolverModel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            SOLVER_MODEL_FINITE_ELEMENT_ANALYSIS: _ClassVar[BaseData.GeneralSettings.SolverModel]
            SOLVER_MODEL_DEPRECATED_MASSIVE: _ClassVar[BaseData.GeneralSettings.SolverModel]
            SOLVER_MODEL_DEPRECATED_THIN_WALLED: _ClassVar[BaseData.GeneralSettings.SolverModel]
            SOLVER_MODEL_THIN_WALLED_ANALYSIS: _ClassVar[BaseData.GeneralSettings.SolverModel]
        SOLVER_MODEL_FINITE_ELEMENT_ANALYSIS: BaseData.GeneralSettings.SolverModel
        SOLVER_MODEL_DEPRECATED_MASSIVE: BaseData.GeneralSettings.SolverModel
        SOLVER_MODEL_DEPRECATED_THIN_WALLED: BaseData.GeneralSettings.SolverModel
        SOLVER_MODEL_THIN_WALLED_ANALYSIS: BaseData.GeneralSettings.SolverModel
        class StressPositionOnElement(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            STRESS_POSITION_ON_ELEMENT_UNFAVOURABLE_EDGE: _ClassVar[BaseData.GeneralSettings.StressPositionOnElement]
            STRESS_POSITION_ON_ELEMENT_CENTERLINE: _ClassVar[BaseData.GeneralSettings.StressPositionOnElement]
        STRESS_POSITION_ON_ELEMENT_UNFAVOURABLE_EDGE: BaseData.GeneralSettings.StressPositionOnElement
        STRESS_POSITION_ON_ELEMENT_CENTERLINE: BaseData.GeneralSettings.StressPositionOnElement
        class BucklingCurveY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            BUCKLING_CURVE_Y_A0: _ClassVar[BaseData.GeneralSettings.BucklingCurveY]
            BUCKLING_CURVE_Y_A: _ClassVar[BaseData.GeneralSettings.BucklingCurveY]
            BUCKLING_CURVE_Y_B: _ClassVar[BaseData.GeneralSettings.BucklingCurveY]
            BUCKLING_CURVE_Y_C: _ClassVar[BaseData.GeneralSettings.BucklingCurveY]
            BUCKLING_CURVE_Y_D: _ClassVar[BaseData.GeneralSettings.BucklingCurveY]
            BUCKLING_CURVE_Y_UNDEFINED: _ClassVar[BaseData.GeneralSettings.BucklingCurveY]
        BUCKLING_CURVE_Y_A0: BaseData.GeneralSettings.BucklingCurveY
        BUCKLING_CURVE_Y_A: BaseData.GeneralSettings.BucklingCurveY
        BUCKLING_CURVE_Y_B: BaseData.GeneralSettings.BucklingCurveY
        BUCKLING_CURVE_Y_C: BaseData.GeneralSettings.BucklingCurveY
        BUCKLING_CURVE_Y_D: BaseData.GeneralSettings.BucklingCurveY
        BUCKLING_CURVE_Y_UNDEFINED: BaseData.GeneralSettings.BucklingCurveY
        class BucklingCurveZ(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            BUCKLING_CURVE_Z_A0: _ClassVar[BaseData.GeneralSettings.BucklingCurveZ]
            BUCKLING_CURVE_Z_A: _ClassVar[BaseData.GeneralSettings.BucklingCurveZ]
            BUCKLING_CURVE_Z_B: _ClassVar[BaseData.GeneralSettings.BucklingCurveZ]
            BUCKLING_CURVE_Z_C: _ClassVar[BaseData.GeneralSettings.BucklingCurveZ]
            BUCKLING_CURVE_Z_D: _ClassVar[BaseData.GeneralSettings.BucklingCurveZ]
            BUCKLING_CURVE_Z_UNDEFINED: _ClassVar[BaseData.GeneralSettings.BucklingCurveZ]
        BUCKLING_CURVE_Z_A0: BaseData.GeneralSettings.BucklingCurveZ
        BUCKLING_CURVE_Z_A: BaseData.GeneralSettings.BucklingCurveZ
        BUCKLING_CURVE_Z_B: BaseData.GeneralSettings.BucklingCurveZ
        BUCKLING_CURVE_Z_C: BaseData.GeneralSettings.BucklingCurveZ
        BUCKLING_CURVE_Z_D: BaseData.GeneralSettings.BucklingCurveZ
        BUCKLING_CURVE_Z_UNDEFINED: BaseData.GeneralSettings.BucklingCurveZ
        class TypeOfWelding(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            TYPE_OF_WELDING_TUNGSTEN_INERT_GAS: _ClassVar[BaseData.GeneralSettings.TypeOfWelding]
            TYPE_OF_WELDING_METAL_INERT_GAS: _ClassVar[BaseData.GeneralSettings.TypeOfWelding]
        TYPE_OF_WELDING_TUNGSTEN_INERT_GAS: BaseData.GeneralSettings.TypeOfWelding
        TYPE_OF_WELDING_METAL_INERT_GAS: BaseData.GeneralSettings.TypeOfWelding
        class ManufacturingType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            MANUFACTURING_TYPE_UNKNOWN: _ClassVar[BaseData.GeneralSettings.ManufacturingType]
            MANUFACTURING_TYPE_COLD_FORMED: _ClassVar[BaseData.GeneralSettings.ManufacturingType]
            MANUFACTURING_TYPE_GLULAM: _ClassVar[BaseData.GeneralSettings.ManufacturingType]
            MANUFACTURING_TYPE_HOT_ROLLED: _ClassVar[BaseData.GeneralSettings.ManufacturingType]
            MANUFACTURING_TYPE_NONE: _ClassVar[BaseData.GeneralSettings.ManufacturingType]
            MANUFACTURING_TYPE_SAWN: _ClassVar[BaseData.GeneralSettings.ManufacturingType]
            MANUFACTURING_TYPE_WELDED: _ClassVar[BaseData.GeneralSettings.ManufacturingType]
        MANUFACTURING_TYPE_UNKNOWN: BaseData.GeneralSettings.ManufacturingType
        MANUFACTURING_TYPE_COLD_FORMED: BaseData.GeneralSettings.ManufacturingType
        MANUFACTURING_TYPE_GLULAM: BaseData.GeneralSettings.ManufacturingType
        MANUFACTURING_TYPE_HOT_ROLLED: BaseData.GeneralSettings.ManufacturingType
        MANUFACTURING_TYPE_NONE: BaseData.GeneralSettings.ManufacturingType
        MANUFACTURING_TYPE_SAWN: BaseData.GeneralSettings.ManufacturingType
        MANUFACTURING_TYPE_WELDED: BaseData.GeneralSettings.ManufacturingType
        TOLERANCE_FOR_POINTS_FIELD_NUMBER: _ClassVar[int]
        TOLERANCE_FOR_LINES_FIELD_NUMBER: _ClassVar[int]
        TOLERANCE_FOR_PLANES_FIELD_NUMBER: _ClassVar[int]
        TOLERANCE_FOR_DIRECTIONS_FIELD_NUMBER: _ClassVar[int]
        SOLVER_MODEL_FIELD_NUMBER: _ClassVar[int]
        STRESS_POSITION_ON_ELEMENT_FIELD_NUMBER: _ClassVar[int]
        TOLERANCE_FOR_STRAIGHT_SUBPANELS_FIELD_NUMBER: _ClassVar[int]
        IS_GENERATED_CURVED_SUBPANELS_EC9_FIELD_NUMBER: _ClassVar[int]
        HAS_NEGLECT_MOMENTS_DUE_TO_CENTROID_SHIFT_FIELD_NUMBER: _ClassVar[int]
        EFFECTIVE_MAX_ITERATION_COUNT_FIELD_NUMBER: _ClassVar[int]
        MAXIMUM_DIFFERENCE_BETWEEN_ITERATIONS_FIELD_NUMBER: _ClassVar[int]
        HAS_CONSIDER_EFFECTIVE_SECTION_ANNEX_E_FIELD_NUMBER: _ClassVar[int]
        HAS_CONSIDER_INFLUENCE_OF_TRANSVERSE_WELD_FIELD_NUMBER: _ClassVar[int]
        HAS_MATERIAL_DEFINITION_ACTIVE_FIELD_NUMBER: _ClassVar[int]
        HAS_PLASTIC_CAPACITY_DESIGN_ACTIVE_FIELD_NUMBER: _ClassVar[int]
        HAS_CONCRETE_REINFORCEMENT_FIELD_NUMBER: _ClassVar[int]
        BUCKLING_CURVE_Y_FIELD_NUMBER: _ClassVar[int]
        BUCKLING_CURVE_Z_FIELD_NUMBER: _ClassVar[int]
        TYPE_OF_WELDING_FIELD_NUMBER: _ClassVar[int]
        US_SPELLING_OF_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
        STRESS_SMOOTHING_TO_AVOID_SINGULARITIES_FIELD_NUMBER: _ClassVar[int]
        MANUFACTURING_TYPE_FIELD_NUMBER: _ClassVar[int]
        tolerance_for_points: float
        tolerance_for_lines: float
        tolerance_for_planes: float
        tolerance_for_directions: float
        solver_model: BaseData.GeneralSettings.SolverModel
        stress_position_on_element: BaseData.GeneralSettings.StressPositionOnElement
        tolerance_for_straight_subpanels: float
        is_generated_curved_subpanels_ec9: bool
        has_neglect_moments_due_to_centroid_shift: bool
        effective_max_iteration_count: int
        maximum_difference_between_iterations: float
        has_consider_effective_section_annex_e: bool
        has_consider_influence_of_transverse_weld: bool
        has_material_definition_active: bool
        has_plastic_capacity_design_active: bool
        has_concrete_reinforcement: bool
        buckling_curve_y: BaseData.GeneralSettings.BucklingCurveY
        buckling_curve_z: BaseData.GeneralSettings.BucklingCurveZ
        type_of_welding: BaseData.GeneralSettings.TypeOfWelding
        us_spelling_of_properties: bool
        stress_smoothing_to_avoid_singularities: bool
        manufacturing_type: BaseData.GeneralSettings.ManufacturingType
        def __init__(self, tolerance_for_points: _Optional[float] = ..., tolerance_for_lines: _Optional[float] = ..., tolerance_for_planes: _Optional[float] = ..., tolerance_for_directions: _Optional[float] = ..., solver_model: _Optional[_Union[BaseData.GeneralSettings.SolverModel, str]] = ..., stress_position_on_element: _Optional[_Union[BaseData.GeneralSettings.StressPositionOnElement, str]] = ..., tolerance_for_straight_subpanels: _Optional[float] = ..., is_generated_curved_subpanels_ec9: bool = ..., has_neglect_moments_due_to_centroid_shift: bool = ..., effective_max_iteration_count: _Optional[int] = ..., maximum_difference_between_iterations: _Optional[float] = ..., has_consider_effective_section_annex_e: bool = ..., has_consider_influence_of_transverse_weld: bool = ..., has_material_definition_active: bool = ..., has_plastic_capacity_design_active: bool = ..., has_concrete_reinforcement: bool = ..., buckling_curve_y: _Optional[_Union[BaseData.GeneralSettings.BucklingCurveY, str]] = ..., buckling_curve_z: _Optional[_Union[BaseData.GeneralSettings.BucklingCurveZ, str]] = ..., type_of_welding: _Optional[_Union[BaseData.GeneralSettings.TypeOfWelding, str]] = ..., us_spelling_of_properties: bool = ..., stress_smoothing_to_avoid_singularities: bool = ..., manufacturing_type: _Optional[_Union[BaseData.GeneralSettings.ManufacturingType, str]] = ...) -> None: ...
    ADDONS_FIELD_NUMBER: _ClassVar[int]
    STANDARDS_FIELD_NUMBER: _ClassVar[int]
    GENERAL_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    addons: BaseData.Addons
    standards: BaseData.Standards
    general_settings: BaseData.GeneralSettings
    def __init__(self, addons: _Optional[_Union[BaseData.Addons, _Mapping]] = ..., standards: _Optional[_Union[BaseData.Standards, _Mapping]] = ..., general_settings: _Optional[_Union[BaseData.GeneralSettings, _Mapping]] = ...) -> None: ...
