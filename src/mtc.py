from las import CaliperPass
from utils import FtoC
import re


class MTC:
    def __init__(self, fnames, fingers, bowlsizes):
        bowlsizes.sort()
        self.passes = {}
        self.temp_lengths = len(fnames)
        self.fingers = fingers
        self.bowlsizes = bowlsizes
        for fname in fnames:
            temp = int(fname.split("/")[-1].split("F")[0])

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
        mtc += f"{FtoC(temps[0]):03},{FtoC(temps[-1]):03}\n"

        for bowlsize in self.bowlsizes:
            mtc += f"{bowlsize},{self.temp_lengths}\n"

            for temp in temps:
                mtc += f"{FtoC(temp):04},"
            mtc += "\n"

            for finger in range(self.fingers):
                for temp in temps:
                    fing_avg = self.passes[temp].data[f"R{finger+1:02}"][
                        'data'][f'bowlsize_{bowlsize}'].mean()
                    # print(finger + 1, f'bowlsize_{bowlsize}', fing_avg)
                    mtc += f"{int(fing_avg):04},"

                mtc += "\n"

        # for i, line in enumerate(mtc):
        #     if line[-1] == ",":
        #         mtc.pop()
        # mtc = "".join(mtc)
        return mtc


if __name__ == "__main__":
    fnames = [
        "../examples/Gowell/93F-11019.LAS", "../examples/Gowell/71F-11019.LAS",
        "../examples/Gowell/45F-11019.LAS", "../examples/Gowell/118F-11019.LAS"
    ]

    mtc = MTC(fnames,
              fingers=24,
              bowlsizes=[47.6, 60.3, 76.2, 101.6, 127.0, 142.9, 152.4])
    print(mtc.compile())
