from math import inf
from dlubal.api import rfem
from pydantic import BaseModel, Field
import streamlit as st

"""
Cantilever beam design using RFEM API and Pydantic for input validation.
To run this script install Streamlit and execute the following command in the terminal:
'python -m streamlit run pydantic_streamlit.py'
"""

class CantileverData(BaseModel):
    """
    Pydantic class defining the model parameters.
    This class is used to validate the input parameters for the RFEM model.
    """
    length: float = Field(None, gt=0, le=10)
    material: str = 'S235'
    section: str = 'IPE 120'


def define_structure(model : CantileverData) -> None:
    """
    Define and return a list of structural objects.
    This function creates a cantilever beam with the specified parameters.
    """
    object_lst = [
        # Define material
        rfem.structure_core.Material(
            no=1,
            name=model.material,
        ),

        # Define section
        rfem.structure_core.Section(
            no=1,
            name=model.section,
            material=1,
        ),

        # Define nodes
        rfem.structure_core.Node(
            no=1,
        ),
        rfem.structure_core.Node(
            no=2,
            coordinate_1=model.length,
        ),

        # Define member
        rfem.structure_core.Member(
            no=1,
            node_start=1,
            node_end=2,
            section_start=1,
        ),

        # Define nodal support at Node 1 (fully fixed)
        rfem.types_for_nodes.NodalSupport(
            no=1,
            nodes=[1],
            spring_x=inf,
            spring_y=inf,
            spring_z=inf,
            rotational_restraint_x=inf,
            rotational_restraint_y=inf,
            rotational_restraint_z=inf,
        ),
    ]
    rfem_app.create_object_list(objs=object_lst)

if __name__ == '__main__':

    # Streamlit app
    st.title("RFEM API Cantilever Design")
    form = st.form(key='cantilever_form')
    l = form.slider(label='Select length [m] (0, 10>)', min_value=0.00, max_value=15.00)
    mat = form.selectbox('Select material', ['S235', 'S275', 'S355', 'S450'])
    sec = form.selectbox('Select section', ['IPE 100', 'IPE 120','HEA 100', 'HEB 100'])
    submit_button = form.form_submit_button(label='Submit')

    if submit_button:
        try:
            model = CantileverData(length=l, material=mat, section=sec)

            form.write('Parameters OK. Creating cantilever in RFEM...')
            with rfem.Application() as rfem_app:
                # Step 1: Create a new model
                rfem_app.close_all_models(save_changes=False)
                rfem_app.create_model(name='cantilever')

                # Step 2: Clear existing objects
                rfem_app.delete_all_objects()

                # Step 3: Define and create all objects.
                define_structure(model)
                st.badge("Success", icon=":material/check:", color="green")

        except ValueError as e:
            st.badge("Error", icon="⚠️", color="red")
            st.error(f"Pydantic output: {e}")
