import ipywidgets as wg
from IPython.display import display
from mascope_sdk import (
    get_workspaces,
)
from traitlets import Unicode, observe

from ..access import load_mascope_token


class Dropdown(wg.Dropdown):  # pylint: disable=abstract-method
    """Base dropdown component. Instantiates a wg.Dropdown and displays it."""

    # Store URL as a class variable to allow attaching an "observer" to it, and to make API requests
    url = Unicode()

    def __init__(self, **kwargs):
        """Initialize the dropdown

        Takes arbitrary keyword arguments and passes them to wg.Dropdown.
        Typical arguments are "options" and "description".
        """
        wg.Dropdown.__init__(self, **kwargs)
        # Load access token on initialization
        self.access_token = load_mascope_token()
        display(self)

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
        # Reset dropdown options to empty list
        self.options = []

    @observe("value")
    def _value_changed(self, change: dict) -> None:  # pylint: disable=unused-argument
        """Callback function triggered when the dropdown selection has changed

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
        self.on_value_changed()

    def on_value_changed(self) -> None:
        """Method to call when dropdown value has changed

        Child classes should override this method for custom action.
        """
        # Do nothing
        pass  # pylint: disable=unnecessary-pass


class UrlDropdown(Dropdown):  # pylint: disable=abstract-method
    """Dropdown to select Mascope URL"""

    def __init__(self, url: str, **kwargs) -> None:
        Dropdown.__init__(
            self,
            options=url,
            description="URL",
            style=kwargs.pop("style", None),
        )
        if "layout_props" in kwargs:
            self.layout = wg.Layout(**kwargs["layout_props"])


class WorkspaceDropdown(Dropdown):  # pylint: disable=abstract-method
    """Dropdown to select Mascope workspace

    Should be linked with an instance of ``UrlDropdown`` to update when URL selected.
    """

    def __init__(self, **kwargs):
        Dropdown.__init__(
            self, options=[], description="Workspaces", style=kwargs.pop("style", None)
        )
        if "layout_props" in kwargs:
            self.layout = wg.Layout(**kwargs["layout_props"])

    @observe("url")
    def _url_changed(self, change: dict) -> None:
        """Override parent class method on URL change"""

        # Reset workspaces
        self.options = []
        # Request workspaces from Mascope and set as the options of the dropdown
        workspaces = get_workspaces(self.url, self.access_token)
        # Transform workspaces into tuples for dropdown
        self.options = [
            (workspace["workspace_name"], workspace) for workspace in workspaces
        ]
