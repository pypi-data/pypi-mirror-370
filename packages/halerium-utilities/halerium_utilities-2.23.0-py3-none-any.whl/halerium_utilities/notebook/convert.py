from copy import deepcopy


def convert_to_native_format(notebook, inplace=False):
    """
    Converts a notebook json structure into the native format in
    which source code is stored as a multiline string.

    Parameters
    ----------
    notebook : dict
        The notebook json structure.
        Can be either in native or jupyter format.
    inplace : bool, optional
        Whether to perform the operation in-place.

    Returns
    -------
    notebook
        The notebook in native format.
    """

    if not inplace:
        notebook = deepcopy(notebook)

    for cell in notebook["cells"]:
        if isinstance(cell["source"], list):
            source = ""
            for line in cell["source"][:-1]:
                # ensure correct line breaks
                source += line.rstrip('\r\n') + "\n"
            # last line needs to line break
            if len(cell["source"]) > 0:
                source += cell["source"][-1].rstrip('\r\n')
            cell["source"] = source
        elif not isinstance(cell["source"], str):
            raise TypeError("Cell source must be either of type str or list.")

    return notebook


def convert_to_jupyter_format(notebook, inplace=False):
    """
    Converts a notebook json structure into the jupyter format in
    which source code is stored as a list of strings.

    Parameters
    ----------
    notebook : dict
        The notebook json structure.
        Can be either in native or jupyter format.
    inplace : bool, optional
        Whether to perform the operation in-place.

    Returns
    -------
    notebook
        The notebook in jupyter format.
    """

    if not inplace:
        notebook = deepcopy(notebook)

    for cell in notebook["cells"]:
        if isinstance(cell["source"], str):
            source = cell["source"].split("\n")
            for i, line in enumerate(source[:-1]):
                # ensure correct line breaks
                source[i] = line.rstrip('\r\n') + "\n"
            # last line needs to line break
            if len(source) > 0:
                source[-1] = source[-1].rstrip('\r\n')
            cell["source"] = source
        elif not isinstance(cell["source"], list):
            raise TypeError("Cell source must be either of type str or list.")

    return notebook
