from PyQt5.QtWidgets import QMessageBox

from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui

from orangecontrib.xrt.widgets.gui.ow_optical_element import OWOpticalElement
from orangecontrib.xrt.util.xrt_data import XRTData

class OWToridMirrorDistorted(OWOpticalElement):

    name = "Toroid Mirror Distorted"
    description = "XRT: Toroid Mirror Distorted"
    icon = "icons/toroidal_mirror.png"
    priority = 7


    oe_name = Setting("my_mirror")
    center = Setting("[0,0,0]")
    material = Setting("Material('C', rho=3.52, kind='plate')")
    R = Setting(1000.0)
    r = Setting(10.0)
    pitch = Setting("np.pi/2")
    yaw = Setting("0.0")
    limPhysX = Setting("[-5, 5]")
    limPhysY = Setting("[-15, 15]")


    def __init__(self):
        super().__init__()

    def populate_tab_setting(self):
        oasysgui.lineEdit(self.tab_bas, self, "oe_name", "O.E. Name", labelWidth=150, valueType=str, orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "center", "center: ",
                          labelWidth=150,
                          valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "material", "material command: ",
                          labelWidth=150,
                          valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "R", "R [mm]: ",
                          labelWidth=250,
                          valueType=float,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "r", "r [mm]: ",
                          labelWidth=250,
                          valueType=float,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "pitch", "pitch angle [rad]: ",
                          labelWidth=150,
                          valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "yaw", "yaw angle [rad]: ",
                          labelWidth=150,
                          valueType=str,
                          orientation="horizontal")


        oasysgui.lineEdit(self.tab_bas, self, "limPhysX", "limPhysX limits [mm]: ",
                          labelWidth=150,
                          valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "limPhysY", "limPhysY limits [mm]: ",
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
            "material": self.material,
            "R": self.R,
            "r": self.r,
            "pitch": self.pitch,
            "yaw": self.yaw,
            "limPhysX": self.limPhysX,
            "limPhysY": self.limPhysY,
                }

        return self.xrtcode_template().format_map(xrtcode_parameters)

    def xrtcode_template(self):
        return \
"""
import numpy as np
from xrt.backends.raycing import BeamLine
from orangecontrib.xrt.util.toroid_mirror_distorted import ToroidMirrorDistorted # TODO: use native XRT
from xrt.backends.raycing.materials import Material
component = ToroidMirrorDistorted(
    distorsion_factor=1,
    bl=BeamLine(),
    name='{name}',
    center={center},
    material={material},
    R={R},
    r={r},
    pitch={pitch},
    yaw={yaw},
    limPhysX={limPhysX},
    limPhysY={limPhysY},
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
    ow = OWToridMirrorDistorted()
    ow.show()
    a.exec_()


