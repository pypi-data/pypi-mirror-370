from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QRect

from orangewidget import gui
from orangewidget import widget
from orangewidget.settings import Setting
from oasys.widgets.widget import OWWidget
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence
from oasys.widgets.gui import ConfirmDialog, MessageDialog

from syned.widget.widget_decorator import WidgetDecorator


from orangecontrib.xrt.util.xrt_data import XRTData

class OWOpticalElement(OWWidget, WidgetDecorator):

    maintainer = "M Sanchez del Rio"
    maintainer_email = "srio(@at@)esrf.eu"
    keywords = ["data", "file", "load", "read"]
    category = "XRT Optical Elements"

    outputs = [{"name":"XRTData",
                "type":XRTData,
                "doc":"XRT Data",
                "id":"data"}]

    inputs = [("XRTData", XRTData, "receive_xrt_data")]
    WidgetDecorator.append_syned_input_data(inputs)


    xrt_data = None

    shape = Setting(0)
    surface_shape = Setting(0)

    want_main_area=0

    is_automatic_run = Setting(0)

    MAX_WIDTH = 460 + 10
    MAX_HEIGHT = 700 + 25

    TABS_AREA_HEIGHT = 625
    CONTROL_AREA_WIDTH = 450

    def __init__(self, show_automatic_box=True):
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

        if show_automatic_box :
            gui.checkBox(self.controlArea, self, 'is_automatic_run', 'Automatic Execution')

        self.tabs_setting = oasysgui.tabWidget(self.controlArea)
        self.tabs_setting.setFixedHeight(self.TABS_AREA_HEIGHT)
        self.tabs_setting.setFixedWidth(self.CONTROL_AREA_WIDTH-5)

        self.tab_bas = oasysgui.createTabPage(self.tabs_setting, "O.E. Setting")
        self.populate_tab_setting()

        self.tab_xrtcode = oasysgui.createTabPage(self.tabs_setting, "XRT code")
        self.populate_tab_xrtcode(self.tab_xrtcode)

        self.draw_specific_box()

    def populate_tab_xrtcode(self, tab_util):
        left_box_0 = oasysgui.widgetBox(tab_util, "XRT code to be sent", addSpace=False, orientation="vertical", height=450)
        gui.button(left_box_0, self, "Update XRT code", callback=self.update_xrtcode)

        self.xrtcode_id = oasysgui.textArea(height=380, width=415, readOnly=True)
        left_box_0.layout().addWidget(self.xrtcode_id)

    def update_xrtcode(self):
        self.xrtcode_id.setText(self.get_xrt_code())

    def draw_specific_box(self):
        raise NotImplementedError()

    def check_data(self):
        congruence.checkPositiveNumber(self.p, "Distance from previous Continuation Plane")
        congruence.checkPositiveNumber(self.q, "Distance to next Continuation Plane")
        congruence.checkPositiveAngle(self.angle_radial, "Incident Angle (to normal)")
        congruence.checkPositiveAngle(self.angle_azimuthal, "Rotation along Beam Axis")

    def send_data(self):
        raise NotImplementedError()

    def get_optical_element(self):
        raise NotImplementedError()

    def receive_syned_data(self, data):
        xrt_data = data

        if xrt_data is not None:
            self.xrt_data = xrt_data
            if self.is_automatic_run: self.send_data()

    def receive_xrt_data(self, data):
        if isinstance(data, XRTData):
            self.xrt_data = data
            if self.is_automatic_run: self.send_data()
        else:
            MessageDialog.message(self, "Data is not XRTData: bad content", "Error", "critical")

    def callResetSettings(self):
        if ConfirmDialog.confirmed(parent=self, message="Confirm Reset of the Fields?"):
            try:
                self.resetSettings()
            except:
                pass
