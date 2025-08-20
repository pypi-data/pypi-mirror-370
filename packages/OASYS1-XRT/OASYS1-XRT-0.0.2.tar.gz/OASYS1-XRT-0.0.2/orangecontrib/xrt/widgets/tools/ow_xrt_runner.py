import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QTextCursor

from orangewidget import gui
from orangewidget.settings import Setting

from oasys.widgets import gui as oasysgui
from oasys.widgets import widget
from oasys.util.oasys_util import EmittingStream

from orangecontrib.xrt.widgets.gui.python_script import PythonConsole
from orangecontrib.xrt.util.xrt_data import XRTData

class OWRunner(widget.OWWidget):

    name = "XRT Runner Python Script"
    description = "XRT Runner Python Script"
    icon = "icons/runner.png"
    maintainer = "Manuel Sanchez del Rio"
    maintainer_email = "srio(@at@)esrf.eu"
    priority = 500
    category = "Tools"
    keywords = ["script"]

    inputs = [("XRTData", XRTData, "set_input")]

    outputs = [{"name":"XRTData",
                "type":XRTData,
                "doc":"XRT Data",
                "id":"data"}]

    beamline_name = Setting("my_xrt_beamline")
    repetition = Setting(3)

    screens_to_plot = Setting("['sample_screen']")
    sizes_in_um = Setting("[10000]")


    script_file_flag = Setting(0)
    script_file_name = Setting("tmp.py")

    dump_scores_flag = Setting(0)
    dump_beams_flag = Setting(0)

    #
    #
    #
    IMAGE_WIDTH = 890
    IMAGE_HEIGHT = 680

    is_automatic_run = Setting(True)

    error_id = 0
    warning_id = 0
    info_id = 0

    MAX_WIDTH = 1320
    MAX_HEIGHT = 700

    CONTROL_AREA_WIDTH = 405
    TABS_AREA_HEIGHT = 560

    input_data = None

    def __init__(self, show_automatic_box=True, show_general_option_box=True):
        super().__init__() # show_automatic_box=show_automatic_box)


        geom = QApplication.desktop().availableGeometry()
        self.setGeometry(QRect(round(geom.width()*0.05),
                               round(geom.height()*0.05),
                               round(min(geom.width()*0.98, self.MAX_WIDTH)),
                               round(min(geom.height()*0.95, self.MAX_HEIGHT))))

        self.setMaximumHeight(self.geometry().height())
        self.setMaximumWidth(self.geometry().width())

        self.controlArea.setFixedWidth(self.CONTROL_AREA_WIDTH)

        self.general_options_box = gui.widgetBox(self.controlArea, "General Options", addSpace=True, orientation="horizontal")
        self.general_options_box.setVisible(show_general_option_box)

        if show_automatic_box :
            gui.checkBox(self.general_options_box, self, 'is_automatic_run', 'Automatic Execution')


        #
        #
        #
        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Refresh Script", callback=self.refresh_script)
        font = QFont(button.font())
        font.setBold(True)
        button.setFont(font)
        palette = QPalette(button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Blue'))
        button.setPalette(palette) # assign new palette
        button.setFixedHeight(45)


        gui.separator(self.controlArea)

        ###
        gen_box = oasysgui.widgetBox(self.controlArea, "Main", addSpace=False, orientation="vertical", width=self.CONTROL_AREA_WIDTH-5)

        oasysgui.lineEdit(gen_box, self, "beamline_name", "Beamline name", labelWidth=150, valueType=str,
                          orientation="horizontal", callback=self.refresh_script)
        oasysgui.lineEdit(gen_box, self, "repetition", "Number of repetitions", labelWidth=250, valueType=int,
                          orientation="horizontal", callback=self.refresh_script)

        ###
        gen_box = oasysgui.widgetBox(self.controlArea, "Plots", addSpace=False, orientation="vertical", width=self.CONTROL_AREA_WIDTH-5)

        oasysgui.lineEdit(gen_box, self, "screens_to_plot", "List with screens to plot", labelWidth=150, valueType=str,
                          orientation="horizontal", callback=self.refresh_script)
        oasysgui.lineEdit(gen_box, self, "sizes_in_um", "List with screen size in um", labelWidth=150, valueType=str,
                          orientation="horizontal", callback=self.refresh_script)

        ###
        gen_box = oasysgui.widgetBox(self.controlArea, "Output files", addSpace=False, orientation="vertical", width=self.CONTROL_AREA_WIDTH-5)
        gui.comboBox(gen_box, self, "script_file_flag", label="write file with script",
                     items=["No", "Yes"], labelWidth=300,
                     sendSelectedValue=False, orientation="horizontal")
        box1 = gui.widgetBox(gen_box, orientation="horizontal")
        oasysgui.lineEdit(box1, self, "script_file_name", "Script File Name", labelWidth=150, valueType=str,
                          orientation="horizontal")
        self.show_at("self.script_file_flag == 1", box1)

        gui.comboBox(gen_box, self, "dump_scores_flag", label="dump scores and results to files",
                     items=["No", "Yes", "Yes"], labelWidth=300,
                     sendSelectedValue=False, orientation="horizontal")

        gui.comboBox(gen_box, self, "dump_beams_flag", label="dump beams to file",
                     items=["No", "Yes"], labelWidth=300,
                     sendSelectedValue=False, orientation="horizontal")


        tabs_setting = oasysgui.tabWidget(self.mainArea)
        tabs_setting.setFixedHeight(self.IMAGE_HEIGHT)
        tabs_setting.setFixedWidth(self.IMAGE_WIDTH)

        tab_scr = oasysgui.createTabPage(tabs_setting, "Python Script")
        tab_out = oasysgui.createTabPage(tabs_setting, "System Output")

        self.pythonScript = oasysgui.textArea(readOnly=False)
        self.pythonScript.setStyleSheet("background-color: white; font-family: Courier, monospace;")
        self.pythonScript.setMaximumHeight(self.IMAGE_HEIGHT - 250)

        script_box = oasysgui.widgetBox(tab_scr, "", addSpace=False, orientation="vertical", height=self.IMAGE_HEIGHT - 10, width=self.IMAGE_WIDTH - 10)
        script_box.layout().addWidget(self.pythonScript)

        console_box = oasysgui.widgetBox(script_box, "", addSpace=True, orientation="vertical",
                                          height=150, width=self.IMAGE_WIDTH - 10)

        self.console = PythonConsole(self.__dict__, self)
        console_box.layout().addWidget(self.console)

        self.wofry_output = oasysgui.textArea()

        out_box = oasysgui.widgetBox(tab_out, "System Output", addSpace=True, orientation="horizontal", height=self.IMAGE_WIDTH - 45)
        out_box.layout().addWidget(self.wofry_output)

        #############################

        button_box = oasysgui.widgetBox(tab_scr, "", addSpace=True, orientation="horizontal")

        gui.button(button_box, self, "Run Script", callback=self.execute_script, height=40)

        gui.rubber(self.controlArea)

        self.process_showers()

    def set_input(self, xrt_data):
        if not xrt_data is None:
            if isinstance(xrt_data, XRTData):
                self.input_data = xrt_data
            else:
                raise Exception("Bad input.")

            if self.is_automatic_run:
                self.refresh_script()

    def callResetSettings(self):
        pass

    def execute_script(self):
        self._script = str(self.pythonScript.toPlainText())
        self.console.write("\nRunning script:\n")
        self.console.push("exec(_script)")
        self.console.new_prompt(sys.ps1)

    def save_script(self):
        file_name = self.script_file_name
        if not file_name is None:
            if not file_name.strip() == "":
                file = open(file_name, "w")
                file.write(str(self.pythonScript.toPlainText()))
                file.close()

    def refresh_script(self):
        self.wofry_output.setText("")

        sys.stdout = EmittingStream(textWritten=self.writeStdOut)

        self.pythonScript.setText(self.to_python_code())

        if self.script_file_flag:
            self.save_script()

    def writeStdOut(self, text):
        cursor = self.wofry_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.wofry_output.setTextCursor(cursor)
        self.wofry_output.ensureCursorVisible()

    def to_python_code(self):
        if self.input_data is None: return "# << ERROR No XRDData >>"

        code_parameters = {
            "beamline_name": self.beamline_name,
            "REPETITION": self.repetition,
            "build_beamline_code": self.build_beamline_code(),
            "run_process_code": self.run_process_code(),
            "screens_to_plot": self.screens_to_plot,
            "sizes_in_um": self.sizes_in_um,
                }

        template_code = self.get_template_code()
        full_text_code = template_code.format_map(code_parameters)
        return full_text_code

    def build_beamline_code(self):
        indent = "    "
        txt = ""
        txt += "def build_beamline(name=''):\n"
        txt += "\n"
        txt += indent + "from xrt.backends.raycing import BeamLine\n"
        txt += indent + "bl = BeamLine()\n"
        txt += indent + "bl.name = name\n"
        txt += "\n"

        if self.input_data is None:
            txt += indent + "## ERROR No XRTData available ##\n"
            return txt

        for i in range(self.input_data.number_of_components()):
            txt_i = self.input_data.component(i)
            txt_i_indented = "\n".join(indent + line for line in txt_i.splitlines())

            txt += "\n"
            txt += indent + "#\n"
            txt += indent + "# Component index: %d\n" % i
            txt += indent + "#\n"
            txt += txt_i_indented
            txt += "\n"
            txt += indent + "setattr(bl, component.name, component)\n"

        txt += "\n"
        txt += indent + "#\n"
        txt += indent + "#\n"
        txt += indent + "#\n"
        txt += indent + "return bl\n"

        return txt

    def run_process_code(self):
        indent = "    "
        txt = ""
        txt += "def run_process(bl):\n"
        txt += "\n"
        txt += indent + "import numpy as np\n"
        txt += indent + "global REPETITION\n"
        txt += indent + "global dump_beams_folder, dump_beams_flag\n"
        txt += indent + "print('REPETITION = %d' % REPETITION)\n"
        txt += indent + "t0 = time.time()\n"
        txt += "\n"
        txt += indent + "beam_at_screens = dict()\n"

        if self.input_data is None:
            txt += indent + "## ERROR No XRTData available ##\n"
            return txt

        for i in range(self.input_data.number_of_components()):
            txt_i = self.input_data.component(i)
            namespace = dict()
            try:
                exec(txt_i, namespace)
                component = namespace["component"]

                txt += "\n"
                txt += indent + "#\n"
                txt += indent + "# Component index: %d (%s)\n" % (i, component.name)
                txt += indent + "#\n"
                #
                # needs local access to components... TO BE UPDATED!
                #
                from xrt.backends.raycing.sources import Undulator
                from xrt.backends.raycing.screens import Screen
                from xrt.backends.raycing.oes import Plate
                from xrt.backends.raycing.apertures import RectangularAperture
                from orangecontrib.xrt.util.toroid_mirror_distorted import ToroidMirrorDistorted # TODO: use native XRT
                from xrt.backends.raycing.oes import DoubleParaboloidLens

                if isinstance(component, Undulator):
                    txt += indent +  "component = bl.%s\n" % component.name
                    txt += indent +  "beam = component.shine()\n"
                    txt += indent +  'if dump_beams_flag: np.save("%s%s_%02d.npy" % (dump_beams_folder, component.name, REPETITION), beam)\n'
                elif isinstance(component, Screen):
                    txt += indent +  "component = bl.%s\n" % component.name
                    txt += indent +  "beam_at_screen = component.expose(beam)\n"
                    txt += indent +  "beam_at_screens[component.name] = beam_at_screen\n"
                    txt += indent +  'if dump_beams_flag: np.save("%s%s_%02d.npy" % (dump_beams_folder, component.name, REPETITION), beam)\n'
                elif isinstance(component, DoubleParaboloidLens):
                    txt += indent +  "component = bl.%s\n" % component.name
                    txt += indent +  "beam, _, _ = component.multiple_refract(beam) # WARNING: NOT STANDARD: output beam is returned!! \n"
                    txt += indent +  'if dump_beams_flag: np.save("%s%s_%02d.npy" % (dump_beams_folder, component.name, REPETITION), beam)\n'
                elif isinstance(component, Plate):
                    txt += indent +  "component = bl.%s\n" % component.name
                    txt += indent +  "_, _, _ = component.double_refract(beam)\n"
                    txt += indent +  'if dump_beams_flag: np.save("%s%s_%02d.npy" % (dump_beams_folder, component.name, REPETITION), beam)\n'
                elif isinstance(component, RectangularAperture):
                    txt += indent +  "component = bl.%s\n" % component.name
                    txt += indent +  "_ = component.propagate(beam)\n"
                    txt += indent +  'if dump_beams_flag: np.save("%s%s_%02d.npy" % (dump_beams_folder, component.name, REPETITION), beam)\n'
                elif isinstance(component, ToroidMirrorDistorted):
                    txt += indent +  "component = bl.%s\n" % component.name
                    txt += indent +  "beam, _ = component.reflect(beam) # WARNING: NOT STANDARD: output beam is returned!!\n"
                    txt += indent +  'if dump_beams_flag: np.save("%s%s_%02d.npy" % (dump_beams_folder, component.name, REPETITION), beam)\n'


                else:
                    txt += indent +  "# <<<ERROR>>> not implemented component.\n"
            except Exception as exception:
                QMessageBox.critical(self, "Error", str(exception), QMessageBox.Ok)
                if self.IS_DEVELOP: raise exception

        txt += "\n"

        txt += indent + "#\n"
        txt += indent + "#\n"
        txt += indent + "#\n"
        txt += indent + 'dt = time.time() - t0\n'
        txt += indent + 'print("Time needed to create source and trace system %.3f sec" % dt)\n'
        txt += indent + 'REPETITION += 1\n'
        txt += indent + "return beam_at_screens\n"

        return txt


    def get_template_code(self):
        return """
import os
import time
import numpy as np
from scipy.signal import savgol_filter
import xrt

from xrt.backends.raycing import BeamLine
from xrt.plotter import XYCAxis, XYCPlot
from xrt.runner import run_ray_tracing

#
# build_beamline_code
#
{build_beamline_code}

#
# run_process_code
#
{run_process_code}


def make_plot(bl, screen, size=100, bins=1024, cbins=256):
    global dump_scores_folder

    xaxis = XYCAxis(label='x', limits=[-size/2, size/2], unit='um', bins=bins,
                    ppb=int(1024/bins))
    yaxis = XYCAxis(label='z', limits=[-size/2, size/2], unit='um', bins=bins,
                    ppb=int(1024/bins))
    caxis = XYCAxis(label='energy', limits=[bl.u17.eMin, bl.u17.eMax],
                    unit='eV', bins=cbins, fwhmFormatStr="%.2f",
                    ppb=int(512/cbins))

    fname = dump_scores_folder + "/screen_%s.png" % screen

    plot = XYCPlot(beam=screen, xaxis=xaxis, yaxis=yaxis, caxis=caxis, saveName=fname)

    return plot

def do_after_script(plots):
    global dump_scores_folder

    out_str1 = ""
    fwhm_h = np.array([plot.dx for plot in plots])
    fwhm_v = np.array([plot.dy for plot in plots])
    ecen = np.array([plot.cE/1e3 for plot in plots])
    flux = np.array([plot.flux for plot in plots])
    profile_h = np.array([[p.xaxis.binCenters, p.xaxis.total1D]
                          for p in plots])
    profile_v = np.array([[p.yaxis.binCenters, p.yaxis.total1D]
                          for p in plots])
    profile_e = np.array([[p.caxis.binCenters, p.caxis.total1D]
                          for p in plots])

    epeak = []
    for k, plot in enumerate(plots):
        fname = dump_scores_folder + "/res_%s_profile_h.txt" % plot.beam
        np.savetxt(fname, profile_h[k].T)
        fname = dump_scores_folder + "/res_%s_profile_v.txt" % plot.beam
        np.savetxt(fname, profile_v[k].T)
        fname = dump_scores_folder + "/res_%s_profile_e.txt" % plot.beam
        np.savetxt(fname, profile_e[k].T)
        e, y = np.loadtxt(fname, unpack=True)
        epeak.append(e[np.argmax(savgol_filter(y, 51, 3))])
    epeak = np.array(epeak)/1e3

    out_str2 = [
        "epeak  =  " + repr(epeak.tolist()),
        "ecen   =  " + repr(ecen.tolist()),
        "fwhm_h =  " + repr(fwhm_h.tolist()),
        "fwhm_v =  " + repr(fwhm_v.tolist()),
        "flux   =  " + repr(flux.tolist()),
    ]

    out_str2 = chr(10).join(out_str2)
    print(out_str2)
    out_str1 += chr(10) + out_str2 + chr(10)
    with open(dump_scores_folder + "/results.txt", 'w') as f:
        f.write(out_str1)

#
# main
#
global REPETITION
REPETITION = 0

#
# xrt beamline
#
bl = build_beamline(name="{beamline_name}")

#
# prepare output folders (in the directory with bl.name)
#
global dump_scores_folder
dump_scores_flag = 1
dump_scores_folder = "%s/scores/" % bl.name
os.makedirs(dump_scores_folder, exist_ok=True)

global dump_beams_flag, dump_beams_folder
dump_beams_flag = 1
dump_beams_folder = "%s/beams/" % bl.name
if dump_beams_flag: os.makedirs(dump_beams_folder, exist_ok=True)


#
# declare run_process() that makes the tracing
#
xrt.backends.raycing.run.run_process = run_process

#
# define plots
#
screens_to_plot = {screens_to_plot}
sizes_in_um     = {sizes_in_um}

plots = []
for i in range(len(screens_to_plot)):
    plots.append(make_plot(bl, screens_to_plot[i], sizes_in_um[i]))

#
# run
#
run_ray_tracing(plots=plots,
                repeats={REPETITION},
                pickleEvery=1,
                updateEvery=1,
                beamLine=bl,
                afterScript=do_after_script,
                afterScriptArgs=[plots])



"""


if __name__ == "__main__":
    txt1 = """
from xrt.backends.raycing import BeamLine
from xrt.backends.raycing.sources import Undulator
component = Undulator(
    BeamLine(),
    name="u17",
    center=[0,1250,0],
    period=17.0,
    n=117,
    eE=6.0,
    eI=0.2,
    eEpsilonX=0.0,
    eEpsilonZ=0.0,
    eEspread=0.00094,
    eSigmaX=30.0,
    eSigmaZ=5.2,
    distE="eV",
    targetE=[18070.0,1],
    eMin=17000.0,
    eMax=18500.0,
    nrays=20000,
    )
"""

    txt2 = """
from xrt.backends.raycing import BeamLine
from xrt.backends.raycing.screens import Screen
component = Screen(
    BeamLine(),
    name="sample_screen",
    center=[0, 56289, 0],
    )
"""

    oo = XRTData(component=txt1)
    oo.append(txt2)

    a = QApplication(sys.argv)
    ow = OWRunner()
    ow.set_input(oo)
    ow.show()
    a.exec_()
    ow.saveSettings()