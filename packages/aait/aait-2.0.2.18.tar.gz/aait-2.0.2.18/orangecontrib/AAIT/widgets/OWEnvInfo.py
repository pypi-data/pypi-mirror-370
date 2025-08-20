import os
import sys
import platform
import numpy as np
import datetime as datetime
import Orange
import Orange.data
from Orange.widgets import widget
from Orange.widgets.utils.signals import Output

from AnyQt.QtWidgets import QApplication

# Conditional imports to mirror Orange add-on layout
if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic
    from Orange.widgets.orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
else:
    from orangecontrib.AAIT.utils.import_uic import uic
    from orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file

try:
    import importlib.metadata as importlib_metadata
except Exception:  # pragma: no cover
    import importlib_metadata  # type: ignore


@apply_modification_from_python_file(filepath_original_widget=__file__)
class OWEnvInfo(widget.OWWidget):
    name = "Environment Info"
    description = "Exports system, Orange, Python, and package versions as a single-row table."
    category = "AAIT - TOOLBOX"
    icon = "icons/owenvinfo.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/owenvinfo.png"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owenvinfo.ui")
    priority = 1094
    want_control_area = False

    class Outputs:
        data = Output("Environment Info", Orange.data.Table)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(470)
        self.setFixedHeight(300)
        uic.loadUi(self.gui, self)

        table = self._build_table()
        self.Outputs.data.send(table)

    @staticmethod
    def _safe_version(pkg: str):
        try:
            return importlib_metadata.version(pkg)
        except Exception:
            return None

    def _collect(self):
        keys = [
            "OS", "Machine", "Processor",
            "Python Version", "Python Executable", "Orange3",
            "Time"
        ]
        vals = [
            platform.platform(),
            platform.machine(),
            platform.processor() or platform.machine(),
            sys.version.replace("\n", " "),
            sys.executable,
            getattr(Orange, "__version__", "unknown"),
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # <-- valeur formatée
        ]

        notable = [
            "aait", "io4it", "hlit",
        ]
        for pkg in notable:
            ver = self._safe_version(pkg)
            if ver:
                keys.append(pkg)
                vals.append(ver)
        return keys, vals

    def _build_table(self) -> Orange.data.Table:
        keys, vals = self._collect()

        metas = [Orange.data.StringVariable.make(k) for k in keys]
        domain = Orange.data.Domain([], metas=metas)
        X = np.zeros((1, 0))
        M = np.array([vals], dtype=object)
        return Orange.data.Table(domain, X, metas=M)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = OWEnvInfo()
    w.show()
    if hasattr(app, "exec"):
        app.exec()
    else:
        app.exec_()