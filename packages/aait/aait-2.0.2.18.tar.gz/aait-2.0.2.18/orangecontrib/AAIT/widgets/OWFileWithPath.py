import os
import sys

import Orange.data
from AnyQt.QtWidgets import QApplication
from Orange.widgets import widget
from Orange.widgets.utils.signals import Input, Output


if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic
    from Orange.widgets.orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
else:
    from orangecontrib.AAIT.utils.import_uic import uic
    from orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file


@apply_modification_from_python_file(filepath_original_widget=__file__)
class OWFileWithPath(widget.OWWidget):
    name = "File with Path"
    category = "AAIT - TOOLBOX"
    description = "Load some tabular data specified with a filepath ('.../data/example.xlsx')."
    icon = "icons/owfilewithpath.svg"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/owfilewithpath.svg"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owfilewithpath.ui")
    want_control_area = False
    priority = 1060

    class Inputs:
        filepath = Input("Path", str)
        path_table = Input("Path Table", Orange.data.Table)

    class Outputs:
        data = Output("Data", Orange.data.Table)


    @Inputs.filepath
    def set_filepath(self, in_filepath):
        if in_filepath is not None:
            self.filepath = in_filepath
            self.run()

    @Inputs.path_table
    def set_path_table(self, in_path_table):
        if in_path_table is not None:
            if "path" in in_path_table.domain:
                self.filepath = in_path_table[0]["path"].value
                self.run()
            else:
                self.warning("You need a 'path' variable from which the data will be loaded.")


    def __init__(self):
        super().__init__()
        # Qt Management
        self.setFixedWidth(470)
        self.setFixedHeight(300)
        uic.loadUi(self.gui, self)

        # Data Management
        self.filepath = None
        self.data = None
        self.autorun = True
        self.post_initialized()

    def run(self):
        self.error("")
        self.warning("")

        if self.filepath is None:
            return

        try:
            self.filepath = self.filepath.strip('"')
            out_data = Orange.data.Table.from_file(self.filepath)
            out_data.name = self.filepath
        except Exception as e:
            self.error(f"An error occurred: the provided file path may not be supported ({e})")
            return

        self.Outputs.data.send(out_data)

    def post_initialized(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_widget = OWFileWithPath()
    my_widget.show()
    if hasattr(app, "exec"):
        app.exec()
    else:
        app.exec_()
