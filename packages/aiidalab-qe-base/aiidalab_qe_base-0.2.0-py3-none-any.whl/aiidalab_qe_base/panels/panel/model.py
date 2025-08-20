from aiidalab_qe_base.models import Model


class PanelModel(Model):
    """Base class for all panel models.

    Attributes
    ----------
    `title` : `str`
        The title to be shown in the GUI.
    `identifier` : `str`
        Which plugin this panel belong to.
    """

    title = "Panel"
    identifier = "panel"
