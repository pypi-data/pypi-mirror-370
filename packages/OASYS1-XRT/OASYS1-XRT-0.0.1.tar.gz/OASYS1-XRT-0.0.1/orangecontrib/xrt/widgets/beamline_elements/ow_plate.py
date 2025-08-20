from PyQt5.QtWidgets import QMessageBox

from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui

from orangecontrib.xrt.widgets.gui.ow_optical_element import OWOpticalElement
from orangecontrib.xrt.util.xrt_data import XRTData

class OWPlate(OWOpticalElement):

    name = "Plate"
    description = "XRT: Plate"
    icon = "icons/filter.png"
    priority = 6

    oe_name = Setting("my_plate")
    center = Setting("[0,0,0]")
    pitch = Setting("np.pi/2")
    material = Setting("Material('C', rho=3.52, kind='plate')")
    t = Setting(0.3)
    surface = Setting("r'diamond 300$\mu$m'")

    def __init__(self):
        super().__init__()

    def populate_tab_setting(self):
        oasysgui.lineEdit(self.tab_bas, self, "oe_name", "O.E. Name", labelWidth=150, valueType=str, orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "center", "center: ",
                          labelWidth=150,
                          valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "pitch", "pitch angle [rad]: ",
                          labelWidth=150,
                          valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "material", "material command: ",
                          labelWidth=150,
                          valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "t", "thickness [mm]: ",
                          labelWidth=250,
                          valueType=float,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "surface", "surface command: ",
                          labelWidth=150,
                          valueType=str,
                          orientation="horizontal")


    def draw_specific_box(self):
        pass

    def check_data(self):
        pass

    def get_xrt_code(self):

        xrtcode_parameters = {
            "name":self.oe_name,
            "center":self.center,
            "pitch": self.pitch,
            "material": self.material,
            "t": self.t,
            "surface": self.surface,
                }

        return self.xrtcode_template().format_map(xrtcode_parameters)

    def xrtcode_template(self):
        return \
"""
import numpy as np
from xrt.backends.raycing import BeamLine
from xrt.backends.raycing.oes import Plate
from xrt.backends.raycing.materials import Material
component = Plate(BeamLine(),
    name='{name}',
    center={center},
    pitch={pitch},
    material={material},
    t={t},
    surface={surface},
    )                             
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
    ow = OWPlate()
    ow.show()
    a.exec_()


