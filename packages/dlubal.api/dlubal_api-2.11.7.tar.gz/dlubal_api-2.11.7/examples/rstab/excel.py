import os
import xlwings as xw
from dlubal.api import rstab

def open_work_book():
    """Open excel file."""

    dirname = os.path.join(os.getcwd(), os.path.dirname(__file__))
    path = os.path.join(dirname,'src/Nodes.xlsx')

    wb = xw.Book(path)

    return wb

def close_work_book(wb):
    """Close excel file."""

    wb.save()
    app = wb.app
    wb.close()
    app.kill()

def get_node_from_excel(work_book) -> dict:
    """Retrieve node from excel file."""

    input_sheet = work_book.sheets('Nodes')

    node1 = {'no' : int(input_sheet["A2"].value),
              'x' : input_sheet["B2"].value,
              'y' : input_sheet["C2"].value,
              'z' : input_sheet["D2"].value}

    return node1

def write_node_to_excel(node, work_book) -> None:
    """Write data to excel file."""

    input_sheet = work_book.sheets('Nodes')

    input_sheet["A3"].value = node.no
    input_sheet["B3"].value = node.coordinate_1
    input_sheet["C3"].value = node.coordinate_2
    input_sheet["D3"].value = node.coordinate_3
    if node.comment:
        input_sheet["E3"].value = node.comment


if __name__ == "__main__":
    """Main routine."""

    with rstab.Application() as rstab_app:

        # Step 1: Create a new model
        rstab_app.close_all_models(save_changes=False)
        rstab_app.create_model(name='excel')

        # Step 2: Clear existing objects
        rstab_app.delete_all_objects()

        # Step 3: Get data for node from excel
        work_book = open_work_book()

        # Step 4: Create nodes in RSTAB
        node1 = get_node_from_excel(work_book)

        rstab_app.create_object_list(objs = [
            rstab.structure_core.Node(
                no = node1['no'],
                coordinate_1 = node1['x'],
                coordinate_2 = node1['y'],
                coordinate_3 = node1['z']),
            rstab.structure_core.Node(
                no = 2,
                coordinate_1 = 1,
                coordinate_2 = 2,
                coordinate_3 = 4,
                comment = 'Node 2')])

        # Step 4: Get node 2 from RSTAB
        node2 = rstab_app.get_object(
            obj = rstab.structure_core.Node(
                no = 2))
        write_node_to_excel(node2, work_book)

        # Step 5: Save and close excel file
        close_work_book(work_book)
