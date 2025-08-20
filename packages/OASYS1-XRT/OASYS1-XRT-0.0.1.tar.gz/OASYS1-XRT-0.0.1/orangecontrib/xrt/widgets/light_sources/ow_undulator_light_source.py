import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QRect

from orangewidget import widget
from orangewidget import gui
from orangewidget.settings import Setting

from oasys.widgets.widget import OWWidget
from oasys.widgets import gui as oasysgui

from syned.widget.widget_decorator import WidgetDecorator
from syned.beamline.beamline import Beamline as SynedBeamline
from syned.storage_ring.light_source import LightSource as SynedLightSource

from orangecontrib.xrt.util.xrt_data import XRTData

class OWUndulatorLightSource(OWWidget, WidgetDecorator):

    name = "Undulator Light Source"
    description = "XRT: Undulator Light Source"
    icon = "icons/undulator.png"
    priority = 2

    inputs = []
    WidgetDecorator.append_syned_input_data(inputs)

    outputs = [{"name":"XRTData",
                "type":XRTData,
                "doc":"XRT Data",
                "id":"data"}]

    want_main_area=0

    MAX_WIDTH = 460 + 10
    MAX_HEIGHT = 700 + 25

    TABS_AREA_HEIGHT = 625
    CONTROL_AREA_WIDTH = 450


    # name = 'u17', center = [0, 1250, 0], period = 17,
    # n = 117, eE = 6, eI = 0.2, eEpsilonX = 0.130, eEpsilonZ = 0.010,
    # eEspread = 9.4e-4, eSigmaX = 30, eSigmaZ = 5.2, distE = 'eV',
    # targetE = [18.07e3, 1], eMin = 17000, eMax = 18500, nrays = 20e3)

    source_name = Setting("my_source")
    center  = Setting("[0,0,0]")
    period = Setting(10.0) # mm
    n = Setting(100)
    eE = Setting(1.0) # GeV
    eI = Setting(0.1) # A
    eEpsilonX = (0.0) # nm.rad
    eEpsilonZ = (0.0) # nm.rad
    eSpread = Setting(0.0)  # %
    eSigmaX = Setting(0.0) # um
    eSigmaZ = Setting(0.0) # um
    distE = Setting("eV")
    targetE = Setting("[18070.0, 1]")
    eMin    = Setting(17000.0)
    eMax    = Setting(18500.0)
    nrays   = Setting(20000)

    def __init__(self):
        super().__init__()

        self.runaction = widget.OWAction("Send Data", self)
        self.runaction.triggered.connect(self.send_data)
        self.addAction(self.runaction)

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Send Data", callback=self.send_data)
        font = QFont(button.font())
        font.setBold(True)
        button.setFont(font)
        palette = QPalette(button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Blue'))
        button.setPalette(palette) # assign new palette
        button.setFixedHeight(45)

        gui.separator(self.controlArea)

        geom = QApplication.desktop().availableGeometry()
        self.setGeometry(QRect(round(geom.width()*0.05),
                               round(geom.height()*0.05),
                               round(min(geom.width()*0.98, self.MAX_WIDTH)),
                               round(min(geom.height()*0.95, self.MAX_HEIGHT))))

        self.setMaximumHeight(self.geometry().height())
        self.setMaximumWidth(self.geometry().width())

        self.controlArea.setFixedWidth(self.CONTROL_AREA_WIDTH)

        self.tabs_setting = oasysgui.tabWidget(self.controlArea)
        self.tabs_setting.setFixedHeight(self.TABS_AREA_HEIGHT)
        self.tabs_setting.setFixedWidth(self.CONTROL_AREA_WIDTH-5)

        self.tab_bas = oasysgui.createTabPage(self.tabs_setting, "O.E. Setting")
        self.populate_tab_setting()

        self.tab_xrtcode = oasysgui.createTabPage(self.tabs_setting, "XRT code")
        self.populate_tab_xrtcode(self.tab_xrtcode)

        self.draw_specific_box()


    def populate_tab_setting(self):
        oasysgui.lineEdit(self.tab_bas, self, "source_name", "Source Name", labelWidth=150, valueType=str, orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "center", "center: ",
                          labelWidth=150,
                          valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "eE", "Electron beam energy [GeV]: ",
                          labelWidth=250,
                          valueType=float,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "eI", "Electron beam current [A]: ",
                          labelWidth=250,
                          valueType=float,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "eEpsilonX", "Electron beam emittance H [nm.rad]: ",
                          labelWidth=250,
                          valueType=float,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "eEpsilonZ", "Electron beam emittance V [nm.rad]: ",
                          labelWidth=250,
                          valueType=float,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "eSpread", "Electron energy spread [%]: ",
                          labelWidth=250,
                          valueType=float,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "eSigmaX", "Electron beam r.m.s. size H [um]: ",
                          labelWidth=250,
                          valueType=float,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "eSigmaZ", "Electron beam r.m.s. size V [um]: ",
                          labelWidth=250,
                          valueType=float,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "period", "Period [mm]: ",
                          labelWidth=250,
                          valueType=float,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "n", "Number of Periods: ",
                          labelWidth=250,
                          valueType=int,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "distE", "Photon energy units: ",
                          labelWidth=150,
                          valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "targetE", "Target energy [eV]: ",
                          labelWidth=150,
                          valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "eMin", "Min energy [eV]: ",
                          labelWidth=250,
                          valueType=float,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "eMax", "Max energy [eV]: ",
                          labelWidth=250,
                          valueType=float,
                          orientation="horizontal")

        oasysgui.lineEdit(self.tab_bas, self, "nrays", "Number of rays: ",
                          labelWidth=250,
                          valueType=int,
                          orientation="horizontal")


    def populate_tab_xrtcode(self, tab_util):
        left_box_0 = oasysgui.widgetBox(tab_util, "XRT code to be sent", addSpace=False, orientation="vertical", height=450)
        gui.button(left_box_0, self, "Update XRT code", callback=self.update_xrtcode)

        self.xrtcode_id = oasysgui.textArea(height=380, width=415, readOnly=True)
        left_box_0.layout().addWidget(self.xrtcode_id)

    def draw_specific_box(self):
        pass

    def update_xrtcode(self):
        self.xrtcode_id.setText(self.get_xrt_code())

    def get_xrt_code(self):

        xrtcode_parameters = {
            "name":self.source_name,
            "center":self.center,
            "period":self.period,
            "n":int(self.n),
            "eE":self.eE,
            "eI":self.eI,
            "eEpsilonX":self.eEpsilonX,
            "eEpsilonZ":self.eEpsilonZ,
            "eEspread":self.eSpread,
            "eSigmaX":self.eSigmaX,
            "eSigmaZ":self.eSigmaZ,
            "distE":self.distE,
            "targetE":self.targetE,
            "eMin":self.eMin,
            "eMax":self.eMax,
            "nrays":self.nrays,
                }

        return self.xrtcode_template().format_map(xrtcode_parameters)

    def xrtcode_template(self):
        return \
"""
from xrt.backends.raycing import BeamLine
from xrt.backends.raycing.sources import Undulator
component = Undulator(
    BeamLine(),
    name="{name}",
    center={center},
    period={period},
    n={n},
    eE={eE},
    eI={eI},
    eEpsilonX={eEpsilonX},
    eEpsilonZ={eEpsilonZ},
    eEspread={eEspread},
    eSigmaX={eSigmaX},
    eSigmaZ={eSigmaZ},
    distE="{distE}",
    targetE={targetE},
    eMin={eMin},
    eMax={eMax},
    nrays={nrays},
    )
"""

    def receive_syned_data(self, data):
        if data is not None:

            if isinstance(data, SynedLightSource):
                ee = data.get_electron_beam()
                id = data.get_magnetic_structure()
            elif isinstance(data, SynedBeamline) and not data._light_source is None:
                ee = data._light_source.get_electron_beam()
                id = data._light_source.get_magnetic_structure()

            self.eE = ee.energy()
            self.eI = ee.current()
            self.eSpread = ee._energy_spread
            sx, sxp, sz, szp = ee.get_sigmas_all()
            self.eSigmaX = 1e6 * sx
            self.eSigmaZ = 1e6 * sz
            self.eEpsilonX = 1e9 * sx * sxp
            self.eEpsilonZ = 1e9 * sz * szp
            e0 = round(id.resonance_energy(ee.gamma()))
            self.targetE = "[%f, 1]" % e0
            self.eMin = e0 - 100
            self.eMax = e0 + 100
            self.period = 1e3 * id._period_length
            self.n = int(id._number_of_periods)

        else:
            raise Exception("Input data must contain a SYNED LightSource")


    def check_data(self):
        pass

    def send_data(self):
        try:
            self.check_data()

            self.send("XRTData", XRTData(component=self.get_xrt_code()))

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e.args[0]), QMessageBox.Ok)

            self.setStatusMessage("")
            self.progressBarFinished()

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWUndulatorLightSource()
    ow.show()
    a.exec_()
