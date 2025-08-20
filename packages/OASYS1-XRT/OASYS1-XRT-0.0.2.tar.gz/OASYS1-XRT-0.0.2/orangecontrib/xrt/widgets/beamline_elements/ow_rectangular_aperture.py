from PyQt5.QtWidgets import QMessageBox

from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui

from orangecontrib.xrt.widgets.gui.ow_optical_element import OWOpticalElement
from orangecontrib.xrt.util.xrt_data import XRTData

class OWRectangularAperture(OWOpticalElement):

    name = "Rectangular Aperture"
    description = "XRT: Rectangular Aperture"
    icon = "icons/slit.png"
    priority = 5

    oe_name = Setting("my_rectangular_aperture")
    center = Setting("[0,0,0]")
    phg = Setting(1.0)
    pvg = Setting(1.0)


    def __init__(self):
        super().__init__()

    def populate_tab_setting(self):
        oasysgui.lineEdit(self.tab_bas, self, "oe_name", "O.E. Name", labelWidth=150, valueType=str, orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "center", "center: ",
                          labelWidth=150,
                          valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "phg", "Horizontal gap [mm]: ",
                          labelWidth=250,
                          valueType=float,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "pvg", "Vertical gap [mm]: ",
                          labelWidth=250,
                          valueType=float,
                          orientation="horizontal")

    def draw_specific_box(self):
        pass

    def check_data(self):
        pass

    def get_xrt_code(self):

        xrtcode_parameters = {
            "name":self.oe_name,
            "center":self.center,
            "phg": self.phg,
            "pvg": self.pvg,
                }

        return self.xrtcode_template().format_map(xrtcode_parameters)

    def xrtcode_template(self):
        return \
"""
from xrt.backends.raycing import BeamLine
from xrt.backends.raycing.apertures import RectangularAperture
component = RectangularAperture(BeamLine(),
    name='{name}',
    center={center},
    kind=('left', 'right', 'bottom', 'top'),
    opening=[-{phg}/2, {phg}/2, -{pvg}/2, {pvg}/2])                
"""



    def send_data(self):
        try:
            self.check_data()
            if self.xrt_data is None:
                out_xrt_data = XRTData()
            else:
                out_xrt_data = self.xrt_data.duplicate()

            out_xrt_data.append(self.get_xrt_code())

            self.send("XRTData", out_xrt_data)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e.args[0]), QMessageBox.Ok)

            self.setStatusMessage("")
            self.progressBarFinished()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    a = QApplication(sys.argv)
    ow = OWRectangularAperture()
    ow.show()
    a.exec_()


