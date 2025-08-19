from math import inf
from dlubal.api import rfem

# Connect to the RFEM application
with rfem.Application() as rfem_app:

    # Close all models opened in application without saving
    rfem_app.close_all_models(save_changes=False)

    # Create new model named 'silo' and get its ID.
    silo_id = rfem_app.create_model(name='silo')

    # Create new model named 'steel_hall' and get its ID.
    steel_hall_id = rfem_app.create_model(name='steel_hall')

    # Cleanup both models
    rfem_app.delete_all_objects(optional_model_id=silo_id)
    rfem_app.delete_all_objects(optional_model_id=steel_hall_id)

    # Create materials in silo
    lst = [
        rfem.structure_core.Material(
            no=1,
            name="S450 | EN 1993-1-1:2005-05"),
        rfem.structure_core.Material(
            no=2,
            name="Sand, well-graded (SW) | DIN 18196:2011-05"),
        rfem.structure_core.Material(
            no=3,
            name="Dry air | --"),
        rfem.structure_core.Material(
            no=4,
            name="S450 | EN 1993-1-1:2005-05"),
        rfem.structure_core.Material(
            no=5,
            name="S450 | EN 1993-1-1:2005-05"),
        rfem.structure_core.Material(
            no=6,
            name="S450 | EN 1993-1-1:2005-05"),
        rfem.structure_core.Material(
            no=7,
            name="S450 | EN 1993-1-1:2005-05"),
    ]
    rfem_app.create_object_list(
        lst,
        silo_id)

    # Update material 5 in silo
    rfem_app.update_object(
        rfem.structure_core.Material(
            no=5,
            comment='commented'),
            silo_id)

    # Update materials 1-4 in silo
    lst = [
        rfem.structure_core.Material(
            no=1,
            comment='updated'),
        rfem.structure_core.Material(
            no=2,
            comment='updated'),
        rfem.structure_core.Material(
            no=3,
            comment='updated'),
        rfem.structure_core.Material(
            no=4,
            comment='updated'),
    ]
    rfem_app.update_object_list(lst,
                                silo_id)

    # Create steel hall
    lst = [
        # Material
        rfem.structure_core.Material(
            no=1,
            name="S235 | EN 1993-1-1:2005-05"),

        # Sections
        rfem.structure_core.Section(
            no=1,
            material=1,
            name="HEB 220"),
        rfem.structure_core.Section(
            no=2,
            material=1,
            name="IPE 240"),
        rfem.structure_core.Section(
            no=3,
            material=1,
            name="IPE 100 | -- | British Steel"),
        rfem.structure_core.Section(
            no=4,
            material=1,
            name="L 20x20x3 | ČSN EN 10056-1:2003 | Ferona"),

        # Nodes
        rfem.structure_core.Node(
            no=1,
            coordinate_1=0.0,
            coordinate_2=0.0,
            coordinate_3=0.0),
        rfem.structure_core.Node(
            no=2,
            coordinate_1=0.0,
            coordinate_2=0.0,
            coordinate_3=-2.5),
        rfem.structure_core.Node(
            no=3,
            coordinate_1=0.0,
            coordinate_2=0.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=4,
            coordinate_1=6.0,
            coordinate_2=0.0,
            coordinate_3=-4.5),
        rfem.structure_core.Node(
            no=5,
            coordinate_1=12.0,
            coordinate_2=0.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=6,
            coordinate_1=12.0,
            coordinate_2=0.0,
            coordinate_3=-2.5),
        rfem.structure_core.Node(
            no=7,
            coordinate_1=12.0,
            coordinate_2=0.0,
            coordinate_3=0.0),
        rfem.structure_core.Node(
            no=8,
            coordinate_1=0.3,
            coordinate_2=0.0,
            coordinate_3=-2.5),
        rfem.structure_core.Node(
            no=9,
            coordinate_1=11.7,
            coordinate_2=0.0,
            coordinate_3=-2.5),
        rfem.structure_core.Node(
            no=10,
            coordinate_1=0.0,
            coordinate_2=5.0,
            coordinate_3=0.0),
        rfem.structure_core.Node(
            no=11,
            coordinate_1=0.0,
            coordinate_2=5.0,
            coordinate_3=-2.5),
        rfem.structure_core.Node(
            no=12,
            coordinate_1=0.0,
            coordinate_2=5.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=13,
            coordinate_1=6.0,
            coordinate_2=5.0,
            coordinate_3=-4.5),
        rfem.structure_core.Node(
            no=14,
            coordinate_1=12.0,
            coordinate_2=5.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=15,
            coordinate_1=12.0,
            coordinate_2=5.0,
            coordinate_3=-2.5),
        rfem.structure_core.Node(
            no=16,
            coordinate_1=12.0,
            coordinate_2=5.0,
            coordinate_3=0.0),
        rfem.structure_core.Node(
            no=17,
            coordinate_1=0.3,
            coordinate_2=5.0,
            coordinate_3=-2.5),
        rfem.structure_core.Node(
            no=18,
            coordinate_1=11.7,
            coordinate_2=5.0,
            coordinate_3=-2.5),
        rfem.structure_core.Node(
            no=19,
            coordinate_1=0.0,
            coordinate_2=10.0,
            coordinate_3=0.0),
        rfem.structure_core.Node(
            no=20,
            coordinate_1=0.0,
            coordinate_2=10.0,
            coordinate_3=-2.5),
        rfem.structure_core.Node(
            no=21,
            coordinate_1=0.0,
            coordinate_2=10.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=22,
            coordinate_1=6.0,
            coordinate_2=10.0,
            coordinate_3=-4.5),
        rfem.structure_core.Node(
            no=23,
            coordinate_1=12.0,
            coordinate_2=10.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=24,
            coordinate_1=12.0,
            coordinate_2=10.0,
            coordinate_3=-2.5),
        rfem.structure_core.Node(
            no=25,
            coordinate_1=12.0,
            coordinate_2=10.0,
            coordinate_3=0.0),
        rfem.structure_core.Node(
            no=26,
            coordinate_1=0.3,
            coordinate_2=10.0,
            coordinate_3=-2.5),
        rfem.structure_core.Node(
            no=27,
            coordinate_1=11.7,
            coordinate_2=10.0,
            coordinate_3=-2.5),
        rfem.structure_core.Node(
            no=28,
            coordinate_1=0.0,
            coordinate_2=15.0,
            coordinate_3=0.0),
        rfem.structure_core.Node(
            no=29,
            coordinate_1=0.0,
            coordinate_2=15.0,
            coordinate_3=-2.5),
        rfem.structure_core.Node(
            no=30,
            coordinate_1=0.0,
            coordinate_2=15.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=31,
            coordinate_1=6.0,
            coordinate_2=15.0,
            coordinate_3=-4.5),
        rfem.structure_core.Node(
            no=32,
            coordinate_1=12.0,
            coordinate_2=15.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=33,
            coordinate_1=12.0,
            coordinate_2=15.0,
            coordinate_3=-2.5),
        rfem.structure_core.Node(
            no=34,
            coordinate_1=12.0,
            coordinate_2=15.0,
            coordinate_3=0.0),
        rfem.structure_core.Node(
            no=35,
            coordinate_1=0.3,
            coordinate_2=15.0,
            coordinate_3=-2.5),
        rfem.structure_core.Node(
            no=36,
            coordinate_1=11.7,
            coordinate_2=15.0,
            coordinate_3=-2.5),
        rfem.structure_core.Node(
            no=37,
            coordinate_1=0.0,
            coordinate_2=20.0,
            coordinate_3=0.0),
        rfem.structure_core.Node(
            no=38,
            coordinate_1=0.0,
            coordinate_2=20.0,
            coordinate_3=-2.5),
        rfem.structure_core.Node(
            no=39,
            coordinate_1=0.0,
            coordinate_2=20.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=40,
            coordinate_1=6.0,
            coordinate_2=20.0,
            coordinate_3=-4.5),
        rfem.structure_core.Node(
            no=41,
            coordinate_1=12.0,
            coordinate_2=20.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=42,
            coordinate_1=12.0,
            coordinate_2=20.0,
            coordinate_3=-2.5),
        rfem.structure_core.Node(
            no=43,
            coordinate_1=12.0,
            coordinate_2=20.0,
            coordinate_3=0.0),
        rfem.structure_core.Node(
            no=44,
            coordinate_1=0.3,
            coordinate_2=20.0,
            coordinate_3=-2.5),
        rfem.structure_core.Node(
            no=45,
            coordinate_1=11.7,
            coordinate_2=20.0,
            coordinate_3=-2.5),

        # Lines
        rfem.structure_core.Line(
            no=1,
            definition_nodes=[1, 2]),
        rfem.structure_core.Line(
            no=2,
            definition_nodes=[2, 3]),
        rfem.structure_core.Line(
            no=3,
            definition_nodes=[3, 4]),
        rfem.structure_core.Line(
            no=4,
            definition_nodes=[4, 5]),
        rfem.structure_core.Line(
            no=5,
            definition_nodes=[5, 6]),
        rfem.structure_core.Line(
            no=6,
            definition_nodes=[2, 8]),
        rfem.structure_core.Line(
            no=7,
            definition_nodes=[6, 9]),
        rfem.structure_core.Line(
            no=8,
            definition_nodes=[6, 7]),
        rfem.structure_core.Line(
            no=9,
            definition_nodes=[10, 11]),
        rfem.structure_core.Line(
            no=10,
            definition_nodes=[11, 12]),
        rfem.structure_core.Line(
            no=11,
            definition_nodes=[12, 13]),
        rfem.structure_core.Line(
            no=12,
            definition_nodes=[13, 14]),
        rfem.structure_core.Line(
            no=13,
            definition_nodes=[14, 15]),
        rfem.structure_core.Line(
            no=14,
            definition_nodes=[11, 17]),
        rfem.structure_core.Line(
            no=15,
            definition_nodes=[15, 18]),
        rfem.structure_core.Line(
            no=16,
            definition_nodes=[15, 16]),
        rfem.structure_core.Line(
            no=17,
            definition_nodes=[19, 20]),
        rfem.structure_core.Line(
            no=18,
            definition_nodes=[20, 21]),
        rfem.structure_core.Line(
            no=19,
            definition_nodes=[21, 22]),
        rfem.structure_core.Line(
            no=20,
            definition_nodes=[22, 23]),
        rfem.structure_core.Line(
            no=21,
            definition_nodes=[23, 24]),
        rfem.structure_core.Line(
            no=22,
            definition_nodes=[20, 26]),
        rfem.structure_core.Line(
            no=23,
            definition_nodes=[24, 27]),
        rfem.structure_core.Line(
            no=24,
            definition_nodes=[24, 25]),
        rfem.structure_core.Line(
            no=25,
            definition_nodes=[28, 29]),
        rfem.structure_core.Line(
            no=26,
            definition_nodes=[29, 30]),
        rfem.structure_core.Line(
            no=27,
            definition_nodes=[30, 31]),
        rfem.structure_core.Line(
            no=28,
            definition_nodes=[31, 32]),
        rfem.structure_core.Line(
            no=29,
            definition_nodes=[32, 33]),
        rfem.structure_core.Line(
            no=30,
            definition_nodes=[29, 35]),
        rfem.structure_core.Line(
            no=31,
            definition_nodes=[33, 36]),
        rfem.structure_core.Line(
            no=32,
            definition_nodes=[33, 34]),
        rfem.structure_core.Line(
            no=33,
            definition_nodes=[37, 38]),
        rfem.structure_core.Line(
            no=34,
            definition_nodes=[38, 39]),
        rfem.structure_core.Line(
            no=35,
            definition_nodes=[39, 40]),
        rfem.structure_core.Line(
            no=36,
            definition_nodes=[40, 41]),
        rfem.structure_core.Line(
            no=37,
            definition_nodes=[41, 42]),
        rfem.structure_core.Line(
            no=38,
            definition_nodes=[38, 44]),
        rfem.structure_core.Line(
            no=39,
            definition_nodes=[42, 45]),
        rfem.structure_core.Line(
            no=40,
            definition_nodes=[42, 43]),
        rfem.structure_core.Line(
            no=41,
            definition_nodes=[2, 11]),
        rfem.structure_core.Line(
            no=42,
            definition_nodes=[6, 15]),
        rfem.structure_core.Line(
            no=43,
            definition_nodes=[4, 13]),
        rfem.structure_core.Line(
            no=44,
            definition_nodes=[5, 14]),
        rfem.structure_core.Line(
            no=45,
            definition_nodes=[3, 12]),
        rfem.structure_core.Line(
            no=46,
            definition_nodes=[11, 20]),
        rfem.structure_core.Line(
            no=47,
            definition_nodes=[15, 24]),
        rfem.structure_core.Line(
            no=48,
            definition_nodes=[13, 22]),
        rfem.structure_core.Line(
            no=49,
            definition_nodes=[14, 23]),
        rfem.structure_core.Line(
            no=50,
            definition_nodes=[12, 21]),
        rfem.structure_core.Line(
            no=51,
            definition_nodes=[20, 29]),
        rfem.structure_core.Line(
            no=52,
            definition_nodes=[24, 33]),
        rfem.structure_core.Line(
            no=53,
            definition_nodes=[22, 31]),
        rfem.structure_core.Line(
            no=54,
            definition_nodes=[23, 32]),
        rfem.structure_core.Line(
            no=55,
            definition_nodes=[21, 30]),
        rfem.structure_core.Line(
            no=56,
            definition_nodes=[29, 38]),
        rfem.structure_core.Line(
            no=57,
            definition_nodes=[33, 42]),
        rfem.structure_core.Line(
            no=58,
            definition_nodes=[31, 40]),
        rfem.structure_core.Line(
            no=59,
            definition_nodes=[32, 41]),
        rfem.structure_core.Line(
            no=60,
            definition_nodes=[30, 39]),
        rfem.structure_core.Line(
            no=61,
            definition_nodes=[7, 14]),
        rfem.structure_core.Line(
            no=62,
            definition_nodes=[5, 16]),
        rfem.structure_core.Line(
            no=63,
            definition_nodes=[5, 13]),
        rfem.structure_core.Line(
            no=64,
            definition_nodes=[14, 4]),
        rfem.structure_core.Line(
            no=65,
            definition_nodes=[13, 3]),
        rfem.structure_core.Line(
            no=66,
            definition_nodes=[12, 4]),
        rfem.structure_core.Line(
            no=67,
            definition_nodes=[1, 12]),
        rfem.structure_core.Line(
            no=68,
            definition_nodes=[3, 10]),

        # Members
        rfem.structure_core.Member(
            no=1,
            section_start=1,
            line=1),
        rfem.structure_core.Member(
            no=2,
            section_start=1,
            line=2),
        rfem.structure_core.Member(
            no=3,
            section_start=2,
            line=3),
        rfem.structure_core.Member(
            no=4,
            section_start=2,
            line=4),
        rfem.structure_core.Member(
            no=5,
            section_start=1,
            line=5),
        rfem.structure_core.Member(
            no=6,
            section_start=2,
            line=6),
        rfem.structure_core.Member(
            no=7,
            section_start=2,
            line=7),
        rfem.structure_core.Member(
            no=8,
            section_start=1,
            line=8),
        rfem.structure_core.Member(
            no=9,
            section_start=1,
            line=9),
        rfem.structure_core.Member(
            no=10,
            section_start=1,
            line=10),
        rfem.structure_core.Member(
            no=11,
            section_start=2,
            line=11),
        rfem.structure_core.Member(
            no=12,
            section_start=2,
            line=12),
        rfem.structure_core.Member(
            no=13,
            section_start=1,
            line=13),
        rfem.structure_core.Member(
            no=14,
            section_start=2,
            line=14),
        rfem.structure_core.Member(
            no=15,
            section_start=2,
            line=15),
        rfem.structure_core.Member(
            no=16,
            section_start=1,
            line=16),
        rfem.structure_core.Member(
            no=17,
            section_start=1,
            line=17),
        rfem.structure_core.Member(
            no=18,
            section_start=1,
            line=18),
        rfem.structure_core.Member(
            no=19,
            section_start=2,
            line=19),
        rfem.structure_core.Member(
            no=20,
            section_start=2,
            line=20),
        rfem.structure_core.Member(
            no=21,
            section_start=1,
            line=21),
        rfem.structure_core.Member(
            no=22,
            section_start=2,
            line=22),
        rfem.structure_core.Member(
            no=23,
            section_start=2,
            line=23),
        rfem.structure_core.Member(
            no=24,
            section_start=1,
            line=24),
        rfem.structure_core.Member(
            no=25,
            section_start=1,
            line=25),
        rfem.structure_core.Member(
            no=26,
            section_start=1,
            line=26),
        rfem.structure_core.Member(
            no=27,
            section_start=2,
            line=27),
        rfem.structure_core.Member(
            no=28,
            section_start=2,
            line=28),
        rfem.structure_core.Member(
            no=29,
            section_start=1,
            line=29),
        rfem.structure_core.Member(
            no=30,
            section_start=2,
            line=30),
        rfem.structure_core.Member(
            no=31,
            section_start=2,
            line=31),
        rfem.structure_core.Member(
            no=32,
            section_start=1,
            line=32),
        rfem.structure_core.Member(
            no=33,
            section_start=1,
            line=33),
        rfem.structure_core.Member(
            no=34,
            section_start=1,
            line=34),
        rfem.structure_core.Member(
            no=35,
            section_start=2,
            line=35),
        rfem.structure_core.Member(
            no=36,
            section_start=2,
            line=36),
        rfem.structure_core.Member(
            no=37,
            section_start=1,
            line=37),
        rfem.structure_core.Member(
            no=38,
            section_start=2,
            line=38),
        rfem.structure_core.Member(
            no=39,
            section_start=2,
            line=39),
        rfem.structure_core.Member(
            no=40,
            section_start=1,
            line=40),
        rfem.structure_core.Member(
            no=41,
            section_start=3,
            line=41),
        rfem.structure_core.Member(
            no=42,
            section_start=3,
            line=42),
        rfem.structure_core.Member(
            no=43,
            section_start=3,
            line=43),
        rfem.structure_core.Member(
            no=44,
            section_start=3,
            line=44),
        rfem.structure_core.Member(
            no=45,
            section_start=3,
            line=45),
        rfem.structure_core.Member(
            no=46,
            section_start=3,
            line=46),
        rfem.structure_core.Member(
            no=47,
            section_start=3,
            line=47),
        rfem.structure_core.Member(
            no=48,
            section_start=3,
            line=48),
        rfem.structure_core.Member(
            no=49,
            section_start=3,
            line=49),
        rfem.structure_core.Member(
            no=50,
            section_start=3,
            line=50),
        rfem.structure_core.Member(
            no=51,
            section_start=3,
            line=51),
        rfem.structure_core.Member(
            no=52,
            section_start=3,
            line=52),
        rfem.structure_core.Member(
            no=53,
            section_start=3,
            line=53),
        rfem.structure_core.Member(
            no=54,
            section_start=3,
            line=54),
        rfem.structure_core.Member(
            no=55,
            section_start=3,
            line=55),
        rfem.structure_core.Member(
            no=56,
            section_start=3,
            line=56),
        rfem.structure_core.Member(
            no=57,
            section_start=3,
            line=57),
        rfem.structure_core.Member(
            no=58,
            section_start=3,
            line=58),
        rfem.structure_core.Member(
            no=59,
            section_start=3,
            line=59),
        rfem.structure_core.Member(
            no=60,
            section_start=3,
            line=60),
        rfem.structure_core.Member(
            no=61,
            section_start=4,
            line=61),
        rfem.structure_core.Member(
            no=62,
            section_start=4,
            line=62),
        rfem.structure_core.Member(
            no=63,
            section_start=4,
            line=63),
        rfem.structure_core.Member(
            no=64,
            section_start=4,
            line=64),
        rfem.structure_core.Member(
            no=65,
            section_start=4,
            line=65),
        rfem.structure_core.Member(
            no=66,
            section_start=4,
            line=66),
        rfem.structure_core.Member(
            no=67,
            section_start=4,
            line=67),
        rfem.structure_core.Member(
            no=68,
            section_start=4,
            line=68),

        # Nodal Support
        rfem.types_for_nodes.NodalSupport(
            no=1,
            nodes=[1, 7, 10, 16, 19, 25, 28, 34, 37, 43],
            spring_x=inf,
            spring_y=inf,
            spring_z=inf,
            rotational_restraint_x=0,
            rotational_restraint_y=inf,
            rotational_restraint_z=inf),

        # Static Analysis Settings
        rfem.loading.StaticAnalysisSettings(
            no=1),
        rfem.loading.StaticAnalysisSettings(
            no=2,
            analysis_type=rfem.loading.StaticAnalysisSettings.ANALYSIS_TYPE_SECOND_ORDER_P_DELTA),
        rfem.loading.StaticAnalysisSettings(
            no=3,
            analysis_type=rfem.loading.StaticAnalysisSettings.ANALYSIS_TYPE_LARGE_DEFORMATIONS,
            number_of_load_increments=10),

        # Load Cases
        rfem.loading.LoadCase(
            no=1,
            name="Self weight",
            static_analysis_settings=1),
        rfem.loading.LoadCase(
            no=2,
            name="Live load",
            static_analysis_settings=2,
            action_category=rfem.loading.LoadCase.ACTION_CATEGORY_IMPOSED_LOADS_CATEGORY_H_ROOFS_QI_H),
        rfem.loading.LoadCase(
            no=3,
            name="Wind load",
            static_analysis_settings=2,
            action_category=rfem.loading.LoadCase.ACTION_CATEGORY_WIND_QW),
        rfem.loading.LoadCase(
            no=4,
            name="Wind load 2",
            static_analysis_settings=2,
            action_category=rfem.loading.LoadCase.ACTION_CATEGORY_WIND_QW),
        rfem.loading.LoadCase(
            no=5,
            name="Stability - linear",
            static_analysis_settings=1,
            action_category=rfem.loading.LoadCase.ACTION_CATEGORY_PERMANENT_IMPOSED_GQ,
            self_weight_active=True),
        rfem.loading.LoadCase(
            no=6,
            name="Snow load",
            static_analysis_settings=2,
            action_category=rfem.loading.LoadCase.ACTION_CATEGORY_SNOW_ICE_LOADS_H_LESS_OR_EQUAL_TO_1000_M_QS),
        rfem.loading.LoadCase(
            no=7,
            name="Imperfections",
            static_analysis_settings=2,
            consider_imperfection=True,
            imperfection_case=1,
            action_category=rfem.loading.LoadCase.ACTION_CATEGORY_PERMANENT_IMPOSED_GQ),
        rfem.loading.LoadCase(
            no=8,
            name="Other permanent load",
            static_analysis_settings=2),

        # Imperfection Case
        rfem.imperfections.ImperfectionCase(
            no=1,
            name="Local Imperfections Only 1",
            assigned_to_load_cases=[7]),

        # Design Situation
        rfem.loading.DesignSituation(
            no=1,
            user_defined_name_enabled=True,
            name="DS 1",
            design_situation_type=rfem.loading.DesignSituation.DESIGN_SITUATION_TYPE_EQU_PERMANENT_AND_TRANSIENT),
    ]
    rfem_app.create_object_list(
        lst,
        steel_hall_id)

    # Delete materials 6 and 7 in silo
    rfem_app.delete_object_list([
        rfem.structure_core.Material(
            no=6),
        rfem.structure_core.Material(
            no=7)
    ],
        silo_id)

    # Delete material 5 in silo
    rfem_app.delete_object(
        rfem.structure_core.Material(
            no=5),
            silo_id)

    # Create rest of objects in silo
    lst = [
        # Sections
        rfem.structure_core.Section(
            no=1,
            material=1,
            name="IPN 300"),
        rfem.structure_core.Section(
            no=2,
            material=1,
            name="UPE 200"),
        rfem.structure_core.Section(
            no=3,
            material=1,
            name="MSH KHP 88.9x3.6"),
        rfem.structure_core.Section(
            no=4,
            material=1,
            name="MSH KHP 88.9x3.6"),
        rfem.structure_core.Section(
            no=5,
            material=1,
            name="LU 0.3/0.2/0.01/0.01/0"),

        # Thicknesses
        rfem.structure_core.Thickness(
            no=1,
            material=4,
            uniform_thickness=0.01,
            assigned_to_surfaces=[2, 3, 4, 5]),
        rfem.structure_core.Thickness(
            no=2,
            material=1,
            uniform_thickness=0.008,
            assigned_to_surfaces=[1, 6, 7, 8, 9]),
        rfem.structure_core.Thickness(
            no=3,
            material=4,
            uniform_thickness=0.005,
            assigned_to_surfaces=[11]),

        # Nodes
        rfem.structure_core.Node(
            no=1,
            coordinate_1=0.0,
            coordinate_2=0.0,
            coordinate_3=0.0),
        rfem.structure_core.Node(
            no=2,
            coordinate_1=3.0,
            coordinate_2=0.0,
            coordinate_3=0.0),
        rfem.structure_core.Node(
            no=3,
            coordinate_1=3.0,
            coordinate_2=3.0,
            coordinate_3=0.0),
        rfem.structure_core.Node(
            no=4,
            coordinate_1=0.0,
            coordinate_2=3.0,
            coordinate_3=0.0),
        rfem.structure_core.Node(
            no=5,
            coordinate_1=0.0,
            coordinate_2=0.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=6,
            coordinate_1=1.5,
            coordinate_2=0.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=7,
            coordinate_1=3.0,
            coordinate_2=0.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=8,
            coordinate_1=3.0,
            coordinate_2=1.5,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=9,
            coordinate_1=3.0,
            coordinate_2=3.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=10,
            coordinate_1=1.5,
            coordinate_2=3.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=11,
            coordinate_1=0.0,
            coordinate_2=3.0,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=12,
            coordinate_1=0.0,
            coordinate_2=1.5,
            coordinate_3=-3.0),
        rfem.structure_core.Node(
            no=13,
            coordinate_1=0.0,
            coordinate_2=0.0,
            coordinate_3=-6.0),
        rfem.structure_core.Node(
            no=14,
            coordinate_1=1.5,
            coordinate_2=0.0,
            coordinate_3=-6.0),
        rfem.structure_core.Node(
            no=15,
            coordinate_1=3.0,
            coordinate_2=0.0,
            coordinate_3=-6.0),
        rfem.structure_core.Node(
            no=16,
            coordinate_1=3.0,
            coordinate_2=1.5,
            coordinate_3=-6.0),
        rfem.structure_core.Node(
            no=17,
            coordinate_1=3.0,
            coordinate_2=3.0,
            coordinate_3=-6.0),
        rfem.structure_core.Node(
            no=18,
            coordinate_1=1.5,
            coordinate_2=3.0,
            coordinate_3=-6.0),
        rfem.structure_core.Node(
            no=19,
            coordinate_1=0.0,
            coordinate_2=3.0,
            coordinate_3=-6.0),
        rfem.structure_core.Node(
            no=20,
            coordinate_1=0.0,
            coordinate_2=1.5,
            coordinate_3=-6.0),
        rfem.structure_core.Node(
            no=21,
            coordinate_1=0.75,
            coordinate_2=0.75,
            coordinate_3=-4.0),
        rfem.structure_core.Node(
            no=22,
            coordinate_1=2.25,
            coordinate_2=0.75,
            coordinate_3=-4.0),
        rfem.structure_core.Node(
            no=23,
            coordinate_1=2.25,
            coordinate_2=2.25,
            coordinate_3=-4.0),
        rfem.structure_core.Node(
            no=24,
            coordinate_1=0.75,
            coordinate_2=2.25,
            coordinate_3=-4.0),
        rfem.structure_core.Node(
            no=25,
            coordinate_1=0.0,
            coordinate_2=0.0,
            coordinate_3=-12.0),
        rfem.structure_core.Node(
            no=26,
            coordinate_1=3.0,
            coordinate_2=0.0,
            coordinate_3=-12.0),
        rfem.structure_core.Node(
            no=27,
            coordinate_1=3.0,
            coordinate_2=3.0,
            coordinate_3=-12.0),
        rfem.structure_core.Node(
            no=28,
            coordinate_1=0.0,
            coordinate_2=3.0,
            coordinate_3=-12.0),

        # Lines
        rfem.structure_core.Line(
            no=1,
            definition_nodes=[1, 5]),
        rfem.structure_core.Line(
            no=2,
            definition_nodes=[2, 7]),
        rfem.structure_core.Line(
            no=3,
            definition_nodes=[3, 9]),
        rfem.structure_core.Line(
            no=4,
            definition_nodes=[4, 11]),
        rfem.structure_core.Line(
            no=5,
            definition_nodes=[5, 13]),
        rfem.structure_core.Line(
            no=6,
            definition_nodes=[7, 15]),
        rfem.structure_core.Line(
            no=7,
            definition_nodes=[9, 17]),
        rfem.structure_core.Line(
            no=8,
            definition_nodes=[11, 19]),
        rfem.structure_core.Line(
            no=9,
            definition_nodes=[13, 14]),
        rfem.structure_core.Line(
            no=10,
            definition_nodes=[14, 15]),
        rfem.structure_core.Line(
            no=11,
            definition_nodes=[15, 16]),
        rfem.structure_core.Line(
            no=12,
            definition_nodes=[16, 17]),
        rfem.structure_core.Line(
            no=13,
            definition_nodes=[17, 18]),
        rfem.structure_core.Line(
            no=14,
            definition_nodes=[18, 19]),
        rfem.structure_core.Line(
            no=15,
            definition_nodes=[19, 20]),
        rfem.structure_core.Line(
            no=16,
            definition_nodes=[20, 13]),
        rfem.structure_core.Line(
            no=17,
            definition_nodes=[1, 6]),
        rfem.structure_core.Line(
            no=18,
            definition_nodes=[2, 6]),
        rfem.structure_core.Line(
            no=19,
            definition_nodes=[2, 8]),
        rfem.structure_core.Line(
            no=20,
            definition_nodes=[3, 8]),
        rfem.structure_core.Line(
            no=21,
            definition_nodes=[3, 10]),
        rfem.structure_core.Line(
            no=22,
            definition_nodes=[4, 10]),
        rfem.structure_core.Line(
            no=23,
            definition_nodes=[4, 12]),
        rfem.structure_core.Line(
            no=24,
            definition_nodes=[1, 12]),
        rfem.structure_core.Line(
            no=25,
            definition_nodes=[5, 14]),
        rfem.structure_core.Line(
            no=26,
            definition_nodes=[7, 14]),
        rfem.structure_core.Line(
            no=27,
            definition_nodes=[7, 16]),
        rfem.structure_core.Line(
            no=28,
            definition_nodes=[9, 16]),
        rfem.structure_core.Line(
            no=29,
            definition_nodes=[9, 18]),
        rfem.structure_core.Line(
            no=30,
            definition_nodes=[11, 18]),
        rfem.structure_core.Line(
            no=31,
            definition_nodes=[11, 20]),
        rfem.structure_core.Line(
            no=32,
            definition_nodes=[5, 20]),
        rfem.structure_core.Line(
            no=33,
            definition_nodes=[5, 6]),
        rfem.structure_core.Line(
            no=34,
            definition_nodes=[6, 7]),
        rfem.structure_core.Line(
            no=35,
            definition_nodes=[7, 8]),
        rfem.structure_core.Line(
            no=36,
            definition_nodes=[8, 9]),
        rfem.structure_core.Line(
            no=37,
            definition_nodes=[9, 10]),
        rfem.structure_core.Line(
            no=38,
            definition_nodes=[10, 11]),
        rfem.structure_core.Line(
            no=39,
            definition_nodes=[11, 12]),
        rfem.structure_core.Line(
            no=40,
            definition_nodes=[12, 5]),
        rfem.structure_core.Line(
            no=41,
            definition_nodes=[21, 22]),
        rfem.structure_core.Line(
            no=42,
            definition_nodes=[22, 23]),
        rfem.structure_core.Line(
            no=43,
            definition_nodes=[23, 24]),
        rfem.structure_core.Line(
            no=44,
            definition_nodes=[24, 21]),
        rfem.structure_core.Line(
            no=45,
            definition_nodes=[13, 21]),
        rfem.structure_core.Line(
            no=46,
            definition_nodes=[15, 22]),
        rfem.structure_core.Line(
            no=47,
            definition_nodes=[17, 23]),
        rfem.structure_core.Line(
            no=48,
            definition_nodes=[19, 24]),
        rfem.structure_core.Line(
            no=49,
            definition_nodes=[13, 25]),
        rfem.structure_core.Line(
            no=50,
            definition_nodes=[15, 26]),
        rfem.structure_core.Line(
            no=51,
            definition_nodes=[17, 27]),
        rfem.structure_core.Line(
            no=52,
            definition_nodes=[19, 28]),
        rfem.structure_core.Line(
            no=53,
            definition_nodes=[25, 26]),
        rfem.structure_core.Line(
            no=54,
            definition_nodes=[26, 27]),
        rfem.structure_core.Line(
            no=55,
            definition_nodes=[27, 28]),
        rfem.structure_core.Line(
            no=56,
            definition_nodes=[28, 25]),

        # Surfaces
        rfem.structure_core.Surface(
            no=1,
            boundary_lines=[41, 42, 43, 44]),
        rfem.structure_core.Surface(
            no=2,
            boundary_lines=[45, 41, 46, 10, 9]),
        rfem.structure_core.Surface(
            no=3,
            boundary_lines=[46, 42, 47, 12, 11]),
        rfem.structure_core.Surface(
            no=4,
            boundary_lines=[47, 43, 48, 14, 13]),
        rfem.structure_core.Surface(
            no=5,
            boundary_lines=[48, 44, 45, 16, 15]),
        rfem.structure_core.Surface(
            no=6,
            boundary_lines=[9, 10, 50, 53, 49]),
        rfem.structure_core.Surface(
            no=7,
            boundary_lines=[11, 12, 51, 54, 50]),
        rfem.structure_core.Surface(
            no=8,
            boundary_lines=[13, 14, 52, 55, 51]),
        rfem.structure_core.Surface(
            no=9,
            boundary_lines=[15, 16, 49, 56, 52]),
        rfem.structure_core.Surface(
            no=10,
            boundary_lines=[9, 10, 11, 12, 13, 14, 15, 16]),
        rfem.structure_core.Surface(
            no=11,
            boundary_lines=[53, 54, 55, 56]),

        # Beams
        rfem.structure_core.Member(
            no=1,
            line=1,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=1),
        rfem.structure_core.Member(
            no=2,
            line=2,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=1),
        rfem.structure_core.Member(
            no=3,
            line=3,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=1),
        rfem.structure_core.Member(
            no=4,
            line=4,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=1),
        rfem.structure_core.Member(
            no=5,
            line=5,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=1),
        rfem.structure_core.Member(
            no=6,
            line=6,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=1),
        rfem.structure_core.Member(
            no=7,
            line=7,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=1),
        rfem.structure_core.Member(
            no=8,
            line=8,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=1),

        # Ribs
        rfem.structure_core.Member(
            no=9,
            type=rfem.structure_core.Member.TYPE_RIB,
            section_start=2,
            line=9),
        rfem.structure_core.Member(
            no=10,
            type=rfem.structure_core.Member.TYPE_RIB,
            section_start=2,
            line=10),
        rfem.structure_core.Member(
            no=11,
            type=rfem.structure_core.Member.TYPE_RIB,
            section_start=2,
            line=11),
        rfem.structure_core.Member(
            no=12,
            type=rfem.structure_core.Member.TYPE_RIB,
            section_start=2,
            line=12),
        rfem.structure_core.Member(
            no=13,
            type=rfem.structure_core.Member.TYPE_RIB,
            section_start=2,
            line=13),
        rfem.structure_core.Member(
            no=14,
            type=rfem.structure_core.Member.TYPE_RIB,
            section_start=2,
            line=14),
        rfem.structure_core.Member(
            no=15,
            type=rfem.structure_core.Member.TYPE_RIB,
            section_start=2,
            line=15),
        rfem.structure_core.Member(
            no=16,
            type=rfem.structure_core.Member.TYPE_RIB,
            section_start=2,
            line=16),

        # Beams
        rfem.structure_core.Member(
            no=17,
            line=17,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=18,
            line=18,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=19,
            line=19,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=20,
            line=20,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=21,
            line=21,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=22,
            line=22,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=23,
            line=23,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=24,
            line=24,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=25,
            line=25,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=26,
            line=26,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=27,
            line=27,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=28,
            line=28,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=29,
            line=29,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=30,
            line=30,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=31,
            line=31,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=32,
            line=32,
            member_hinge_start=1,
            member_hinge_end=2,
            section_start=3),
        rfem.structure_core.Member(
            no=33,
            line=33,
            section_start=4,
            member_hinge_start=1),
        rfem.structure_core.Member(
            no=34,
            line=34,
            section_start=4,
            member_hinge_end=2),
        rfem.structure_core.Member(
            no=35,
            line=35,
            section_start=4,
            member_hinge_start=1),
        rfem.structure_core.Member(
            no=36,
            line=36,
            section_start=4,
            member_hinge_end=2),
        rfem.structure_core.Member(
            no=37,
            line=37,
            section_start=4,
            member_hinge_start=1),
        rfem.structure_core.Member(
            no=38,
            line=38,
            section_start=4,
            member_hinge_end=2),
        rfem.structure_core.Member(
            no=39,
            line=39,
            section_start=4,
            member_hinge_start=1),
        rfem.structure_core.Member(
            no=40,
            line=40,
            section_start=5,
            member_hinge_end=2),
        rfem.structure_core.Member(
            no=41,
            line=49,
            section_start=5,
            rotation_angle=1.57079632679487),
        rfem.structure_core.Member(
            no=42,
            line=50,
            section_start=5),
        rfem.structure_core.Member(
            no=43,
            line=51,
            section_start=5,
            rotation_angle=-1.57079632679487),
        rfem.structure_core.Member(
            no=44,
            line=52,
            section_start=5,
            rotation_angle=3.14159265358974),

        # Solid
        rfem.structure_core.Solid(
            no=1,
            type=rfem.structure_core.Solid.TYPE_STANDARD,
            material=2,
            boundary_surfaces=[1, 2, 3, 4, 5, 10]),

        # Nodal Support
        rfem.types_for_nodes.NodalSupport(
            no=1,
            nodes=[1, 2, 3, 4],
            spring_x=700000,
            spring_y=800000,
            spring_z=5000000),

        # Member Hinges
        rfem.types_for_members.MemberHinge(
            no=1,
            moment_release_mt=28000,
            axial_release_n=inf,
            axial_release_vy=inf,
            axial_release_vz=inf),
        rfem.types_for_members.MemberHinge(
            no=2,
            moment_release_mt=29000,
            axial_release_n=inf,
            axial_release_vy=inf,
            axial_release_vz=inf,
            moment_release_mz=inf),

        # Static Analysis Settings
        rfem.loading.StaticAnalysisSettings(
            no=1),
        rfem.loading.StaticAnalysisSettings(
            no=2,
            analysis_type=rfem.loading.StaticAnalysisSettings.ANALYSIS_TYPE_SECOND_ORDER_P_DELTA,
            number_of_load_increments=2),
        rfem.loading.StaticAnalysisSettings(
            no=3,
            analysis_type=rfem.loading.StaticAnalysisSettings.ANALYSIS_TYPE_LARGE_DEFORMATIONS,
            number_of_load_increments=10),

        # Load Cases
        rfem.loading.LoadCase(
            no=1,
            name="Self weight",
            static_analysis_settings=1),
        rfem.loading.LoadCase(
            no=2,
            name="Live load",
            static_analysis_settings=2,
            action_category=rfem.loading.LoadCase.ACTION_CATEGORY_PERMANENT_IMPOSED_GQ),
        rfem.loading.LoadCase(
            no=3,
            name="Stability - linear",
            static_analysis_settings=1,
            action_category=rfem.loading.LoadCase.ACTION_CATEGORY_PERMANENT_IMPOSED_GQ,
            self_weight_active=True),
    ]
    rfem_app.create_object_list(
        lst,
        silo_id)

    # Delete material 3 in silo
    rfem_app.delete_object(
        rfem.structure_core.Material(
            no=3),
            silo_id)

    # Connection is terminated automatically at the end of the script.
