
def is_notebook(obj):
    return isinstance(obj, dict) and ("cells" in obj)


def create_card_cell_link(card_id, notebook, cell_index):
    """Add link between a Halerium board card and notebook cell.

    Parameters
    ----------
    card_id :
        The id of the card.
    notebook:
        The notebook or file path or descriptor of the notebook to add a card to.
    cell_index:
        The index of the cell in the notebook to link.

    Returns
    -------

    """
    link_line_start = f'# <halerium id="{card_id}">\n'
    link_line_end = f'# </halerium id="{card_id}">\n'

    is_notebook_file = False
    if not is_notebook(notebook):
        is_notebook_file = True
        notebook_file = notebook
        from ..file.io import read_notebook
        notebook = read_notebook(notebook_file)

    notebook['cells'][cell_index]['source'].insert(0, link_line_start)
    # add line break in last line if needed
    if not notebook['cells'][cell_index]['source'][-1].endswith("\n"):
        notebook['cells'][cell_index]['source'][-1] += "\n"
    notebook['cells'][cell_index]['source'].append(link_line_end)

    if is_notebook_file:
        from ..file.io import write_notebook
        write_notebook(notebook, notebook_file)

