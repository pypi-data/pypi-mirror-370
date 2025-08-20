import os, copy, numpy
# from shadow4.beam.s4_beam import S4Beam

class XRTData:
    def __init__(self, component=None):

        if isinstance(component, type(None)):
            self.__components = []
        elif isinstance(component, list):
            self.__components = component
        else:
            self.__components = [component]

    def duplicate(self):
        return copy.deepcopy(self)

    def append(self, component):
        self.__components.append(component)

    def number_of_components(self):
        return len(self.__components)

    def components(self):
        return self.__components

    def component(self, index):
        return self.components()[index]

    def info(self):
        txt = ""
        for i in range(self.number_of_components()):
            txt += ("\n>> %d " % i) + repr(type(self.component(i)))
        return txt


if __name__ == "__main__":
    txt1 = """
from xrt.backends.raycing import BeamLine
from xrt.backends.raycing.sources import Undulator

xrt_component = Undulator(
    BeamLine(),
    name="ID09 IVU17c",
    center=[0, 0, 0],
    period=0.017,
    n=117.647,
    eE=6.0,
    eI=0.2,
    eEpsilonX=0.151152446676,
    eEpsilonZ=0.014131139047200002,
    eEspread=0.001,
    eSigmaX=33.46035,
    eSigmaZ=7.28154,
    distE='eV',
    targetE=[18070.0, 1],
    eMin=17000.0,
    eMax=18500.0,
    nrays=20000,
)
"""

    txt2 = """
from xrt.backends.raycing.sources import Undulator
from xrt.backends.raycing.screens import Screen

xrt_component = Screen(
    BeamLine(),
    name='sample_screen',
    center=[0, 56289, 0],
    )
"""

    oo = XRTData(component=txt1)
    print("N: ", oo.number_of_components())
    print("info: \n", oo.info())
    # print("index 0: \n", oo.component(0))

    oo.append(txt2)
    print("N: ", oo.number_of_components())
    print("info: \n", oo.info())
    print("index 1: \n", oo.component(1))
