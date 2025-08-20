from pathlib import Path

import traitlets as tl
from anywidget import AnyWidget


class TableWidget(AnyWidget):
    _esm = Path(__file__).parent / "table_widget.js"
    _css = Path(__file__).parent / "table_widget.css"
    data = tl.List().tag(sync=True)
    selected_rows = tl.List().tag(sync=True)
