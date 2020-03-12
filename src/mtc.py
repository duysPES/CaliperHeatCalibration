from las import CaliperPass
from utils import FtoC
import re


class MTC:
    def __init__(self, fnames, fingers, bowlsizes):
        self.passes = {}
        self.temp_lengths = len(fnames)
        self.fingers = fingers
        self.bowlsizes = bowlsizes
        for fname in fnames:
            temp = fname.split("/")[-1].split("F")[0]

            print(f"\nProcessing.....{fname}")
            self.passes[temp] = CaliperPass(fname,
                                            fingers=fingers,
                                            bowlsizes=bowlsizes,
                                            summary=True)

    def compile(self):
        mtc = ""
        mtc += "diameter mm\n"
        mtc += f"{self.fingers},{len(self.bowlsizes)}\n"
        temps = [int(i) for i in self.passes.keys()]
        temps.sort()
        mtc += f"{FtoC(temps[0]):03},{FtoC(temps[-1]):03}"

        return mtc


if __name__ == "__main__":
    fnames = [
        "../examples/Gowell/93F-11019.LAS", "../examples/Gowell/71F-11019.LAS",
        "../examples/Gowell/45F-11019.LAS", "../examples/Gowell/118F-11019.LAS"
    ]

    mtc = MTC(fnames, fingers=24, bowlsizes=[1, 2, 3, 4, 5, 6, 7])
    print(mtc.compile())
