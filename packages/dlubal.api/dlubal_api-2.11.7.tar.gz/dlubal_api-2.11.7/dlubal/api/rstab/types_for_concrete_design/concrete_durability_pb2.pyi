from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConcreteDurability(_message.Message):
    __slots__ = ("no", "user_defined_name_enabled", "name", "members", "member_sets", "no_risk_of_corrosion_or_attack_enabled", "no_risk_of_corrosion_or_attack", "corrosion_induced_by_carbonation_enabled", "corrosion_induced_by_carbonation", "corrosion_induced_by_chlorides_enabled", "corrosion_induced_by_chlorides", "corrosion_induced_by_chlorides_from_sea_water_enabled", "corrosion_induced_by_chlorides_from_sea_water", "freeze_thaw_attack_enabled", "freeze_thaw_attack", "chemical_attack_enabled", "chemical_attack", "concrete_corrosion_induced_by_wear_enabled", "concrete_corrosion_induced_by_wear", "structural_class_type", "userdefined_structural_class", "design_working_life", "increase_design_working_life_from_50_to_100_years_enabled", "position_of_reinforcement_not_affected_by_construction_process_enabled", "special_quality_control_of_production_enabled", "nature_of_binder_without_fly_ash_enabled", "air_entrainment_of_more_than_4_percent_enabled", "compact_coating_enabled", "adequate_cement_enabled", "maximum_equivalent_water_to_cement_ratio", "strength_class_of_the_concrete_enabled", "increase_of_minimum_concrete_cover_type", "increase_of_minimum_concrete_cover_factor", "stainless_steel_enabled", "stainless_steel_type", "stainless_steel_factor", "additional_protection_enabled", "additional_protection_type", "additional_protection_factor", "allowance_of_deviation_type", "userdefined_allowance_of_deviation_factor", "relaxed_quality_control_enabled", "concrete_cast_enabled", "concrete_cast", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class NoRiskOfCorrosionOrAttack(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NO_RISK_OF_CORROSION_OR_ATTACK_VERY_DRY: _ClassVar[ConcreteDurability.NoRiskOfCorrosionOrAttack]
    NO_RISK_OF_CORROSION_OR_ATTACK_VERY_DRY: ConcreteDurability.NoRiskOfCorrosionOrAttack
    class CorrosionInducedByCarbonation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CORROSION_INDUCED_BY_CARBONATION_DRY_OR_PERMANENTLY_WET: _ClassVar[ConcreteDurability.CorrosionInducedByCarbonation]
        CORROSION_INDUCED_BY_CARBONATION_CYCLIC_WET_AND_DRY: _ClassVar[ConcreteDurability.CorrosionInducedByCarbonation]
        CORROSION_INDUCED_BY_CARBONATION_MODERATE_HUMIDITY: _ClassVar[ConcreteDurability.CorrosionInducedByCarbonation]
        CORROSION_INDUCED_BY_CARBONATION_WET_RARELY_DRY: _ClassVar[ConcreteDurability.CorrosionInducedByCarbonation]
    CORROSION_INDUCED_BY_CARBONATION_DRY_OR_PERMANENTLY_WET: ConcreteDurability.CorrosionInducedByCarbonation
    CORROSION_INDUCED_BY_CARBONATION_CYCLIC_WET_AND_DRY: ConcreteDurability.CorrosionInducedByCarbonation
    CORROSION_INDUCED_BY_CARBONATION_MODERATE_HUMIDITY: ConcreteDurability.CorrosionInducedByCarbonation
    CORROSION_INDUCED_BY_CARBONATION_WET_RARELY_DRY: ConcreteDurability.CorrosionInducedByCarbonation
    class CorrosionInducedByChlorides(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CORROSION_INDUCED_BY_CHLORIDES_MODERATE_HUMIDITY: _ClassVar[ConcreteDurability.CorrosionInducedByChlorides]
        CORROSION_INDUCED_BY_CHLORIDES_CYCLIC_WET_AND_DRY: _ClassVar[ConcreteDurability.CorrosionInducedByChlorides]
        CORROSION_INDUCED_BY_CHLORIDES_WET_RARELY_DRY: _ClassVar[ConcreteDurability.CorrosionInducedByChlorides]
    CORROSION_INDUCED_BY_CHLORIDES_MODERATE_HUMIDITY: ConcreteDurability.CorrosionInducedByChlorides
    CORROSION_INDUCED_BY_CHLORIDES_CYCLIC_WET_AND_DRY: ConcreteDurability.CorrosionInducedByChlorides
    CORROSION_INDUCED_BY_CHLORIDES_WET_RARELY_DRY: ConcreteDurability.CorrosionInducedByChlorides
    class CorrosionInducedByChloridesFromSeaWater(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CORROSION_INDUCED_BY_CHLORIDES_FROM_SEA_WATER_EXPOSED_TO_AIRBORNE_SALT: _ClassVar[ConcreteDurability.CorrosionInducedByChloridesFromSeaWater]
        CORROSION_INDUCED_BY_CHLORIDES_FROM_SEA_WATER_PERMANENTLY_SUBMERGED: _ClassVar[ConcreteDurability.CorrosionInducedByChloridesFromSeaWater]
        CORROSION_INDUCED_BY_CHLORIDES_FROM_SEA_WATER_TIDAL_SPLASH_AND_SPRAY_ZONES: _ClassVar[ConcreteDurability.CorrosionInducedByChloridesFromSeaWater]
    CORROSION_INDUCED_BY_CHLORIDES_FROM_SEA_WATER_EXPOSED_TO_AIRBORNE_SALT: ConcreteDurability.CorrosionInducedByChloridesFromSeaWater
    CORROSION_INDUCED_BY_CHLORIDES_FROM_SEA_WATER_PERMANENTLY_SUBMERGED: ConcreteDurability.CorrosionInducedByChloridesFromSeaWater
    CORROSION_INDUCED_BY_CHLORIDES_FROM_SEA_WATER_TIDAL_SPLASH_AND_SPRAY_ZONES: ConcreteDurability.CorrosionInducedByChloridesFromSeaWater
    class FreezeThawAttack(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FREEZE_THAW_ATTACK_MODERATE_WATER_SATURATION_NO_DEICING: _ClassVar[ConcreteDurability.FreezeThawAttack]
        FREEZE_THAW_ATTACK_HIGH_WATER_SATURATION_DEICING: _ClassVar[ConcreteDurability.FreezeThawAttack]
        FREEZE_THAW_ATTACK_HIGH_WATER_SATURATION_NO_DEICING: _ClassVar[ConcreteDurability.FreezeThawAttack]
        FREEZE_THAW_ATTACK_MODERATE_WATER_SATURATION_DEICING: _ClassVar[ConcreteDurability.FreezeThawAttack]
    FREEZE_THAW_ATTACK_MODERATE_WATER_SATURATION_NO_DEICING: ConcreteDurability.FreezeThawAttack
    FREEZE_THAW_ATTACK_HIGH_WATER_SATURATION_DEICING: ConcreteDurability.FreezeThawAttack
    FREEZE_THAW_ATTACK_HIGH_WATER_SATURATION_NO_DEICING: ConcreteDurability.FreezeThawAttack
    FREEZE_THAW_ATTACK_MODERATE_WATER_SATURATION_DEICING: ConcreteDurability.FreezeThawAttack
    class ChemicalAttack(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CHEMICAL_ATTACK_SLIGHTLY_AGGRESSIVE: _ClassVar[ConcreteDurability.ChemicalAttack]
        CHEMICAL_ATTACK_HIGHLY_AGGRESSIVE: _ClassVar[ConcreteDurability.ChemicalAttack]
        CHEMICAL_ATTACK_MODERATELY_AGGRESSIVE: _ClassVar[ConcreteDurability.ChemicalAttack]
    CHEMICAL_ATTACK_SLIGHTLY_AGGRESSIVE: ConcreteDurability.ChemicalAttack
    CHEMICAL_ATTACK_HIGHLY_AGGRESSIVE: ConcreteDurability.ChemicalAttack
    CHEMICAL_ATTACK_MODERATELY_AGGRESSIVE: ConcreteDurability.ChemicalAttack
    class ConcreteCorrosionInducedByWear(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CONCRETE_CORROSION_INDUCED_BY_WEAR_MODERATE: _ClassVar[ConcreteDurability.ConcreteCorrosionInducedByWear]
        CONCRETE_CORROSION_INDUCED_BY_WEAR_HIGH: _ClassVar[ConcreteDurability.ConcreteCorrosionInducedByWear]
        CONCRETE_CORROSION_INDUCED_BY_WEAR_VERY_HIGH: _ClassVar[ConcreteDurability.ConcreteCorrosionInducedByWear]
    CONCRETE_CORROSION_INDUCED_BY_WEAR_MODERATE: ConcreteDurability.ConcreteCorrosionInducedByWear
    CONCRETE_CORROSION_INDUCED_BY_WEAR_HIGH: ConcreteDurability.ConcreteCorrosionInducedByWear
    CONCRETE_CORROSION_INDUCED_BY_WEAR_VERY_HIGH: ConcreteDurability.ConcreteCorrosionInducedByWear
    class StructuralClassType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STRUCTURAL_CLASS_TYPE_STANDARD: _ClassVar[ConcreteDurability.StructuralClassType]
        STRUCTURAL_CLASS_TYPE_DEFINED: _ClassVar[ConcreteDurability.StructuralClassType]
    STRUCTURAL_CLASS_TYPE_STANDARD: ConcreteDurability.StructuralClassType
    STRUCTURAL_CLASS_TYPE_DEFINED: ConcreteDurability.StructuralClassType
    class UserdefinedStructuralClass(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        USERDEFINED_STRUCTURAL_CLASS_UNKNOWN: _ClassVar[ConcreteDurability.UserdefinedStructuralClass]
        USERDEFINED_STRUCTURAL_CLASS_S1: _ClassVar[ConcreteDurability.UserdefinedStructuralClass]
        USERDEFINED_STRUCTURAL_CLASS_S2: _ClassVar[ConcreteDurability.UserdefinedStructuralClass]
        USERDEFINED_STRUCTURAL_CLASS_S3: _ClassVar[ConcreteDurability.UserdefinedStructuralClass]
        USERDEFINED_STRUCTURAL_CLASS_S4: _ClassVar[ConcreteDurability.UserdefinedStructuralClass]
        USERDEFINED_STRUCTURAL_CLASS_S5: _ClassVar[ConcreteDurability.UserdefinedStructuralClass]
        USERDEFINED_STRUCTURAL_CLASS_S6: _ClassVar[ConcreteDurability.UserdefinedStructuralClass]
    USERDEFINED_STRUCTURAL_CLASS_UNKNOWN: ConcreteDurability.UserdefinedStructuralClass
    USERDEFINED_STRUCTURAL_CLASS_S1: ConcreteDurability.UserdefinedStructuralClass
    USERDEFINED_STRUCTURAL_CLASS_S2: ConcreteDurability.UserdefinedStructuralClass
    USERDEFINED_STRUCTURAL_CLASS_S3: ConcreteDurability.UserdefinedStructuralClass
    USERDEFINED_STRUCTURAL_CLASS_S4: ConcreteDurability.UserdefinedStructuralClass
    USERDEFINED_STRUCTURAL_CLASS_S5: ConcreteDurability.UserdefinedStructuralClass
    USERDEFINED_STRUCTURAL_CLASS_S6: ConcreteDurability.UserdefinedStructuralClass
    class DesignWorkingLife(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DESIGN_WORKING_LIFE_50_YEARS: _ClassVar[ConcreteDurability.DesignWorkingLife]
        DESIGN_WORKING_LIFE_100_YEARS: _ClassVar[ConcreteDurability.DesignWorkingLife]
        DESIGN_WORKING_LIFE_20_YEARS: _ClassVar[ConcreteDurability.DesignWorkingLife]
        DESIGN_WORKING_LIFE_25_YEARS: _ClassVar[ConcreteDurability.DesignWorkingLife]
        DESIGN_WORKING_LIFE_30_YEARS: _ClassVar[ConcreteDurability.DesignWorkingLife]
        DESIGN_WORKING_LIFE_75_YEARS: _ClassVar[ConcreteDurability.DesignWorkingLife]
        DESIGN_WORKING_LIFE_80_YEARS: _ClassVar[ConcreteDurability.DesignWorkingLife]
    DESIGN_WORKING_LIFE_50_YEARS: ConcreteDurability.DesignWorkingLife
    DESIGN_WORKING_LIFE_100_YEARS: ConcreteDurability.DesignWorkingLife
    DESIGN_WORKING_LIFE_20_YEARS: ConcreteDurability.DesignWorkingLife
    DESIGN_WORKING_LIFE_25_YEARS: ConcreteDurability.DesignWorkingLife
    DESIGN_WORKING_LIFE_30_YEARS: ConcreteDurability.DesignWorkingLife
    DESIGN_WORKING_LIFE_75_YEARS: ConcreteDurability.DesignWorkingLife
    DESIGN_WORKING_LIFE_80_YEARS: ConcreteDurability.DesignWorkingLife
    class MaximumEquivalentWaterToCementRatio(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MAXIMUM_EQUIVALENT_WATER_TO_CEMENT_RATIO_0_350: _ClassVar[ConcreteDurability.MaximumEquivalentWaterToCementRatio]
        MAXIMUM_EQUIVALENT_WATER_TO_CEMENT_RATIO_0_000: _ClassVar[ConcreteDurability.MaximumEquivalentWaterToCementRatio]
        MAXIMUM_EQUIVALENT_WATER_TO_CEMENT_RATIO_0_400: _ClassVar[ConcreteDurability.MaximumEquivalentWaterToCementRatio]
        MAXIMUM_EQUIVALENT_WATER_TO_CEMENT_RATIO_0_450: _ClassVar[ConcreteDurability.MaximumEquivalentWaterToCementRatio]
        MAXIMUM_EQUIVALENT_WATER_TO_CEMENT_RATIO_0_500: _ClassVar[ConcreteDurability.MaximumEquivalentWaterToCementRatio]
        MAXIMUM_EQUIVALENT_WATER_TO_CEMENT_RATIO_0_550: _ClassVar[ConcreteDurability.MaximumEquivalentWaterToCementRatio]
        MAXIMUM_EQUIVALENT_WATER_TO_CEMENT_RATIO_0_600: _ClassVar[ConcreteDurability.MaximumEquivalentWaterToCementRatio]
        MAXIMUM_EQUIVALENT_WATER_TO_CEMENT_RATIO_0_900: _ClassVar[ConcreteDurability.MaximumEquivalentWaterToCementRatio]
    MAXIMUM_EQUIVALENT_WATER_TO_CEMENT_RATIO_0_350: ConcreteDurability.MaximumEquivalentWaterToCementRatio
    MAXIMUM_EQUIVALENT_WATER_TO_CEMENT_RATIO_0_000: ConcreteDurability.MaximumEquivalentWaterToCementRatio
    MAXIMUM_EQUIVALENT_WATER_TO_CEMENT_RATIO_0_400: ConcreteDurability.MaximumEquivalentWaterToCementRatio
    MAXIMUM_EQUIVALENT_WATER_TO_CEMENT_RATIO_0_450: ConcreteDurability.MaximumEquivalentWaterToCementRatio
    MAXIMUM_EQUIVALENT_WATER_TO_CEMENT_RATIO_0_500: ConcreteDurability.MaximumEquivalentWaterToCementRatio
    MAXIMUM_EQUIVALENT_WATER_TO_CEMENT_RATIO_0_550: ConcreteDurability.MaximumEquivalentWaterToCementRatio
    MAXIMUM_EQUIVALENT_WATER_TO_CEMENT_RATIO_0_600: ConcreteDurability.MaximumEquivalentWaterToCementRatio
    MAXIMUM_EQUIVALENT_WATER_TO_CEMENT_RATIO_0_900: ConcreteDurability.MaximumEquivalentWaterToCementRatio
    class IncreaseOfMinimumConcreteCoverType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        INCREASE_OF_MINIMUM_CONCRETE_COVER_TYPE_STANDARD: _ClassVar[ConcreteDurability.IncreaseOfMinimumConcreteCoverType]
        INCREASE_OF_MINIMUM_CONCRETE_COVER_TYPE_DEFINED: _ClassVar[ConcreteDurability.IncreaseOfMinimumConcreteCoverType]
    INCREASE_OF_MINIMUM_CONCRETE_COVER_TYPE_STANDARD: ConcreteDurability.IncreaseOfMinimumConcreteCoverType
    INCREASE_OF_MINIMUM_CONCRETE_COVER_TYPE_DEFINED: ConcreteDurability.IncreaseOfMinimumConcreteCoverType
    class StainlessSteelType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STAINLESS_STEEL_TYPE_STANDARD: _ClassVar[ConcreteDurability.StainlessSteelType]
        STAINLESS_STEEL_TYPE_DEFINED: _ClassVar[ConcreteDurability.StainlessSteelType]
    STAINLESS_STEEL_TYPE_STANDARD: ConcreteDurability.StainlessSteelType
    STAINLESS_STEEL_TYPE_DEFINED: ConcreteDurability.StainlessSteelType
    class AdditionalProtectionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ADDITIONAL_PROTECTION_TYPE_STANDARD: _ClassVar[ConcreteDurability.AdditionalProtectionType]
        ADDITIONAL_PROTECTION_TYPE_DEFINED: _ClassVar[ConcreteDurability.AdditionalProtectionType]
    ADDITIONAL_PROTECTION_TYPE_STANDARD: ConcreteDurability.AdditionalProtectionType
    ADDITIONAL_PROTECTION_TYPE_DEFINED: ConcreteDurability.AdditionalProtectionType
    class AllowanceOfDeviationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ALLOWANCE_OF_DEVIATION_TYPE_STANDARD: _ClassVar[ConcreteDurability.AllowanceOfDeviationType]
        ALLOWANCE_OF_DEVIATION_TYPE_DEFINED: _ClassVar[ConcreteDurability.AllowanceOfDeviationType]
    ALLOWANCE_OF_DEVIATION_TYPE_STANDARD: ConcreteDurability.AllowanceOfDeviationType
    ALLOWANCE_OF_DEVIATION_TYPE_DEFINED: ConcreteDurability.AllowanceOfDeviationType
    class ConcreteCast(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CONCRETE_CAST_AGAINST_PREPARED_GROUND: _ClassVar[ConcreteDurability.ConcreteCast]
        CONCRETE_CAST_DIRECTLY_AGAINST_SOIL: _ClassVar[ConcreteDurability.ConcreteCast]
    CONCRETE_CAST_AGAINST_PREPARED_GROUND: ConcreteDurability.ConcreteCast
    CONCRETE_CAST_DIRECTLY_AGAINST_SOIL: ConcreteDurability.ConcreteCast
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    NO_RISK_OF_CORROSION_OR_ATTACK_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NO_RISK_OF_CORROSION_OR_ATTACK_FIELD_NUMBER: _ClassVar[int]
    CORROSION_INDUCED_BY_CARBONATION_ENABLED_FIELD_NUMBER: _ClassVar[int]
    CORROSION_INDUCED_BY_CARBONATION_FIELD_NUMBER: _ClassVar[int]
    CORROSION_INDUCED_BY_CHLORIDES_ENABLED_FIELD_NUMBER: _ClassVar[int]
    CORROSION_INDUCED_BY_CHLORIDES_FIELD_NUMBER: _ClassVar[int]
    CORROSION_INDUCED_BY_CHLORIDES_FROM_SEA_WATER_ENABLED_FIELD_NUMBER: _ClassVar[int]
    CORROSION_INDUCED_BY_CHLORIDES_FROM_SEA_WATER_FIELD_NUMBER: _ClassVar[int]
    FREEZE_THAW_ATTACK_ENABLED_FIELD_NUMBER: _ClassVar[int]
    FREEZE_THAW_ATTACK_FIELD_NUMBER: _ClassVar[int]
    CHEMICAL_ATTACK_ENABLED_FIELD_NUMBER: _ClassVar[int]
    CHEMICAL_ATTACK_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_CORROSION_INDUCED_BY_WEAR_ENABLED_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_CORROSION_INDUCED_BY_WEAR_FIELD_NUMBER: _ClassVar[int]
    STRUCTURAL_CLASS_TYPE_FIELD_NUMBER: _ClassVar[int]
    USERDEFINED_STRUCTURAL_CLASS_FIELD_NUMBER: _ClassVar[int]
    DESIGN_WORKING_LIFE_FIELD_NUMBER: _ClassVar[int]
    INCREASE_DESIGN_WORKING_LIFE_FROM_50_TO_100_YEARS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    POSITION_OF_REINFORCEMENT_NOT_AFFECTED_BY_CONSTRUCTION_PROCESS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_QUALITY_CONTROL_OF_PRODUCTION_ENABLED_FIELD_NUMBER: _ClassVar[int]
    NATURE_OF_BINDER_WITHOUT_FLY_ASH_ENABLED_FIELD_NUMBER: _ClassVar[int]
    AIR_ENTRAINMENT_OF_MORE_THAN_4_PERCENT_ENABLED_FIELD_NUMBER: _ClassVar[int]
    COMPACT_COATING_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ADEQUATE_CEMENT_ENABLED_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_EQUIVALENT_WATER_TO_CEMENT_RATIO_FIELD_NUMBER: _ClassVar[int]
    STRENGTH_CLASS_OF_THE_CONCRETE_ENABLED_FIELD_NUMBER: _ClassVar[int]
    INCREASE_OF_MINIMUM_CONCRETE_COVER_TYPE_FIELD_NUMBER: _ClassVar[int]
    INCREASE_OF_MINIMUM_CONCRETE_COVER_FACTOR_FIELD_NUMBER: _ClassVar[int]
    STAINLESS_STEEL_ENABLED_FIELD_NUMBER: _ClassVar[int]
    STAINLESS_STEEL_TYPE_FIELD_NUMBER: _ClassVar[int]
    STAINLESS_STEEL_FACTOR_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_PROTECTION_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_PROTECTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_PROTECTION_FACTOR_FIELD_NUMBER: _ClassVar[int]
    ALLOWANCE_OF_DEVIATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    USERDEFINED_ALLOWANCE_OF_DEVIATION_FACTOR_FIELD_NUMBER: _ClassVar[int]
    RELAXED_QUALITY_CONTROL_ENABLED_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_CAST_ENABLED_FIELD_NUMBER: _ClassVar[int]
    CONCRETE_CAST_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    user_defined_name_enabled: bool
    name: str
    members: _containers.RepeatedScalarFieldContainer[int]
    member_sets: _containers.RepeatedScalarFieldContainer[int]
    no_risk_of_corrosion_or_attack_enabled: bool
    no_risk_of_corrosion_or_attack: ConcreteDurability.NoRiskOfCorrosionOrAttack
    corrosion_induced_by_carbonation_enabled: bool
    corrosion_induced_by_carbonation: ConcreteDurability.CorrosionInducedByCarbonation
    corrosion_induced_by_chlorides_enabled: bool
    corrosion_induced_by_chlorides: ConcreteDurability.CorrosionInducedByChlorides
    corrosion_induced_by_chlorides_from_sea_water_enabled: bool
    corrosion_induced_by_chlorides_from_sea_water: ConcreteDurability.CorrosionInducedByChloridesFromSeaWater
    freeze_thaw_attack_enabled: bool
    freeze_thaw_attack: ConcreteDurability.FreezeThawAttack
    chemical_attack_enabled: bool
    chemical_attack: ConcreteDurability.ChemicalAttack
    concrete_corrosion_induced_by_wear_enabled: bool
    concrete_corrosion_induced_by_wear: ConcreteDurability.ConcreteCorrosionInducedByWear
    structural_class_type: ConcreteDurability.StructuralClassType
    userdefined_structural_class: ConcreteDurability.UserdefinedStructuralClass
    design_working_life: ConcreteDurability.DesignWorkingLife
    increase_design_working_life_from_50_to_100_years_enabled: bool
    position_of_reinforcement_not_affected_by_construction_process_enabled: bool
    special_quality_control_of_production_enabled: bool
    nature_of_binder_without_fly_ash_enabled: bool
    air_entrainment_of_more_than_4_percent_enabled: bool
    compact_coating_enabled: bool
    adequate_cement_enabled: bool
    maximum_equivalent_water_to_cement_ratio: ConcreteDurability.MaximumEquivalentWaterToCementRatio
    strength_class_of_the_concrete_enabled: bool
    increase_of_minimum_concrete_cover_type: ConcreteDurability.IncreaseOfMinimumConcreteCoverType
    increase_of_minimum_concrete_cover_factor: float
    stainless_steel_enabled: bool
    stainless_steel_type: ConcreteDurability.StainlessSteelType
    stainless_steel_factor: float
    additional_protection_enabled: bool
    additional_protection_type: ConcreteDurability.AdditionalProtectionType
    additional_protection_factor: float
    allowance_of_deviation_type: ConcreteDurability.AllowanceOfDeviationType
    userdefined_allowance_of_deviation_factor: float
    relaxed_quality_control_enabled: bool
    concrete_cast_enabled: bool
    concrete_cast: ConcreteDurability.ConcreteCast
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., name: _Optional[str] = ..., members: _Optional[_Iterable[int]] = ..., member_sets: _Optional[_Iterable[int]] = ..., no_risk_of_corrosion_or_attack_enabled: bool = ..., no_risk_of_corrosion_or_attack: _Optional[_Union[ConcreteDurability.NoRiskOfCorrosionOrAttack, str]] = ..., corrosion_induced_by_carbonation_enabled: bool = ..., corrosion_induced_by_carbonation: _Optional[_Union[ConcreteDurability.CorrosionInducedByCarbonation, str]] = ..., corrosion_induced_by_chlorides_enabled: bool = ..., corrosion_induced_by_chlorides: _Optional[_Union[ConcreteDurability.CorrosionInducedByChlorides, str]] = ..., corrosion_induced_by_chlorides_from_sea_water_enabled: bool = ..., corrosion_induced_by_chlorides_from_sea_water: _Optional[_Union[ConcreteDurability.CorrosionInducedByChloridesFromSeaWater, str]] = ..., freeze_thaw_attack_enabled: bool = ..., freeze_thaw_attack: _Optional[_Union[ConcreteDurability.FreezeThawAttack, str]] = ..., chemical_attack_enabled: bool = ..., chemical_attack: _Optional[_Union[ConcreteDurability.ChemicalAttack, str]] = ..., concrete_corrosion_induced_by_wear_enabled: bool = ..., concrete_corrosion_induced_by_wear: _Optional[_Union[ConcreteDurability.ConcreteCorrosionInducedByWear, str]] = ..., structural_class_type: _Optional[_Union[ConcreteDurability.StructuralClassType, str]] = ..., userdefined_structural_class: _Optional[_Union[ConcreteDurability.UserdefinedStructuralClass, str]] = ..., design_working_life: _Optional[_Union[ConcreteDurability.DesignWorkingLife, str]] = ..., increase_design_working_life_from_50_to_100_years_enabled: bool = ..., position_of_reinforcement_not_affected_by_construction_process_enabled: bool = ..., special_quality_control_of_production_enabled: bool = ..., nature_of_binder_without_fly_ash_enabled: bool = ..., air_entrainment_of_more_than_4_percent_enabled: bool = ..., compact_coating_enabled: bool = ..., adequate_cement_enabled: bool = ..., maximum_equivalent_water_to_cement_ratio: _Optional[_Union[ConcreteDurability.MaximumEquivalentWaterToCementRatio, str]] = ..., strength_class_of_the_concrete_enabled: bool = ..., increase_of_minimum_concrete_cover_type: _Optional[_Union[ConcreteDurability.IncreaseOfMinimumConcreteCoverType, str]] = ..., increase_of_minimum_concrete_cover_factor: _Optional[float] = ..., stainless_steel_enabled: bool = ..., stainless_steel_type: _Optional[_Union[ConcreteDurability.StainlessSteelType, str]] = ..., stainless_steel_factor: _Optional[float] = ..., additional_protection_enabled: bool = ..., additional_protection_type: _Optional[_Union[ConcreteDurability.AdditionalProtectionType, str]] = ..., additional_protection_factor: _Optional[float] = ..., allowance_of_deviation_type: _Optional[_Union[ConcreteDurability.AllowanceOfDeviationType, str]] = ..., userdefined_allowance_of_deviation_factor: _Optional[float] = ..., relaxed_quality_control_enabled: bool = ..., concrete_cast_enabled: bool = ..., concrete_cast: _Optional[_Union[ConcreteDurability.ConcreteCast, str]] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
