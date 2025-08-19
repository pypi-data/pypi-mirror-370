import ipywidgets as wg
from IPython.display import display
from traitlets import Unicode, observe
from mascope_sdk import (
    get_sample_batches,
)
from ..access import load_mascope_token


class MultiSelect(wg.SelectMultiple):  # pylint: disable=abstract-method
    """Base multi-select component.
    Instantiates a wg.SelectMultiple and displays it."""

    # Store URL as a class variable to allow attaching an "observer" to it, and to make API requests
    url = Unicode()

    def __init__(self, **kwargs):
        """Initialize the multiselect

        Takes arbitrary keyword arguments and passes them to wg.SelectMultiple.
        Typical arguments are "options" and "description".
        """
        wg.SelectMultiple.__init__(self, **kwargs)
        # Load access token on initialization
        self.access_token = load_mascope_token()
        self.import_peaks_checkbox = wg.Checkbox(
            value=True, description="Import peaks", disabled=False
        )  ## Checkbox to import peaks
        self.import_peaks_checkbox.observe(
            self._on_import_peaks_checkbox_changed, names="value"
        )  # Observe changes in the import_peaks_checkbox value
        self.load_button = wg.Button(description="Load", disabled=True)  ## Load button
        self.load_button.on_click(
            self._button_clicked
        )  # Attach the button click event to the _button_clicked method
        self.data_clear_key = wg.IntText(
            value=0, description="Data key", disabled=False
        )  # Hidden button for cache clearing
        self.data_load_key = wg.IntText(
            value=0, description="Data loading times", disabled=False
        )  # Hidden button for data loading
        self.load_error_output = (
            wg.Output()
        )  # Add an output widget for clearing property_cache
        self.browser = wg.VBox(
            [
                self,
                self.import_peaks_checkbox,
                self.load_button,
                self.load_error_output,
            ]
        )
        display(self.browser)  # Display the browser widget

    def _on_import_peaks_checkbox_changed(
        self, change: dict  # pylint: disable=unused-argument
    ) -> None:
        """
        Callback function triggered when the value of import_peaks_checkbox changes.

        :param change: The change dictionary containing old and new values.
        :type change: dict
        """
        # Enable the load button
        self.load_button.disabled = False

    @observe("load_button")
    def _button_clicked(
        self, button: wg.Button  # pylint: disable=unused-argument
    ) -> None:
        """Callback function triggered when multiselect load button has been clicked"""
        self.load_button.disabled = True
        self.on_load_button_clicked()

    @observe("url")
    def _url_changed(self, change: dict) -> None:  # pylint: disable=unused-argument
        """Callback function triggered when the URL has changed

        Child classes may override this method.

        :param change: The change dictionary at least holds a 'type' key.
            * ``type``: the type of notification.
            Other keys may be passed depending on the value of 'type'. In the
            case where type is 'change', we also have the following keys:
            * ``owner`` : the HasTraits instance
            * ``old`` : the old value of the modified trait attribute
            * ``new`` : the new value of the modified trait attribute
            * ``name`` : the name of the modified trait attribute.
        :type change: dict
        """
        # Reset multiselect options to empty list
        self.options = []

    @observe("value")
    def _value_changed(self, change: dict) -> None:  # pylint: disable=unused-argument
        """Callback function triggered when the multiselect selection has changed

        Child classes may override this method.

        :param change: The change dictionary at least holds a 'type' key.
            * ``type``: the type of notification.
            Other keys may be passed depending on the value of 'type'. In the
            case where type is 'change', we also have the following keys:
            * ``owner`` : the HasTraits instance
            * ``old`` : the old value of the modified trait attribute
            * ``new`` : the new value of the modified trait attribute
            * ``name`` : the name of the modified trait attribute.
        :type change: dict
        """
        if len(self.value) > 0:
            self.load_button.disabled = False
        self.on_value_changed()

    def on_load_button_clicked(self) -> None:
        """Method to call when multiselect load button has been clicked

        Child classes should override this method for custom action.
        """
        # Do nothing
        pass  # pylint: disable=unnecessary-pass

    def on_value_changed(self) -> None:
        """Method to call when multiselect value has changed

        Child classes should override this method for custom action.
        """
        # Do nothing
        pass  # pylint: disable=unnecessary-pass


class SampleBatchMultiSelect(MultiSelect):  # pylint: disable=abstract-method
    """Dropdown to select Mascope sample batch of a selected workspace

    Should be linked with an instance of ``UrlDropdown`` to update when URL selected,
    and an instance of ``WorkspaceDropdown`` to update when workspace selected.
    """

    # workspace_id of the selected workspace in the linked WorkspaceDropdown
    workspace_id = Unicode()

    def __init__(self, **kwargs):
        # Show num_of_lines options in the MultiSelect screen
        num_of_lines = 10
        layout_height = f"{20*num_of_lines}px"

        if "layout_props" in kwargs:
            layout = wg.Layout(**kwargs["layout_props"])
            layout.height = layout_height
        else:
            layout = wg.Layout(height=layout_height)

        # Initialize the MultiSelect with the layout and other kwargs
        MultiSelect.__init__(
            self,
            options=[],
            description="Sample batches",
            layout=layout,
            style=kwargs.pop("style", None),
        )

    @observe("workspace_id")
    def _workspace_changed(
        self, change: dict  # pylint: disable=unused-argument
    ) -> None:
        """Callback function triggered when the ``workspace_id`` has changed"""

        if self.url == "" or self.workspace_id == "":
            # If no URL or no workspace, reset options to empty list
            self.options = []
        else:
            # Fetch sample batches of the selected workspace
            sample_batches = get_sample_batches(
                self.url, self.access_token, self.workspace_id
            )
            # Transform sample batches into tuples for multiselect
            self.options = [
                (batch["sample_batch_name"], batch) for batch in sample_batches
            ]
