import ipywidgets as wg

DEFAULT_WIDGETS_PROPERTIES = {
    "layout": wg.Layout(width="auto", height="40px"),
    "style": {"description_width": "initial"},
}

DEFAULT_BUTTON_PROPERTIES = {
    "layout": wg.Layout(width="auto", height="40px"),
}

DEFAULT_BOX_PROPERTIES = {
    "layout": wg.Layout(
        border="solid 1px",
        padding="10px",
        margin="10px",
        width="95%",  # With 100 % annoying slider bar botton of each HBox
        style={"description_width": "initial"},
    )
}


def create_layout(height: str = None, width: str = None) -> wg.Layout:
    """
    Function to create flexible layout with optional user-defined dimensions.
    If not given auto sizing will be used.

    :param height: height for the ipywidget-layout, defaults to None
    :type height: str, optional
    :param width: width for the ipywidget-layout, defaults to None
    :type width: str, optional
    :return: ipywidget-layout for ipywidget Outputs
    :rtype: wg.Layout
    """
    return wg.Layout(
        flex="1 1 auto",
        height=height if height else "auto",
        width=width if width else "auto",
    )


# Grid options for ag-Grid widget
GRID_OPTIONS = {
    "domLayout": "normal",  # Adjust table height automatically
    "pagination": True,  # Enable pagination
    "paginationPageSize": 20,  # Show 20 rows per page
    "defaultColDef": {  # Default column settings
        "resizable": True,  # Allow resizing columns
        "sortable": True,  # Enable sorting
        "filter": True,  # Enable filtering
        "minWidth": 150,  # Set minimum width for all columns
        "wrapText": True,  # Wrap text in cells
        "autoHeight": True,  # Adjust row height automatically
    },
}
