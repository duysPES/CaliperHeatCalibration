from las import CaliperPass
from utils import FtoC
import datetime
import re
from configparser import ConfigParser, RawConfigParser
from pathlib import Path


def mm2in(mm):
    result = round(mm / 25.4, 2)
    if result == mm // 25.4:
        return int(result)
    else:
        return result


class Parser(ConfigParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def write(self, fileobject, space_around_delimiters=None):
        d = "{}\t".format(self._delimiters[0])
        if self._defaults:
            self._write_section(fileobject, self.default_section,
                                self._defaults.items(), d)
        for section in self._sections:
            self._write_section(fileobject, section,
                                self._sections[section].items(), d)


class HeatCalibration:
    def __init__(self, fnames, fingers, bowlsizes):
        with open(Path("log.out").resolve(), "w") as f:
            pass
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

    def clean(self, results):
        results = results.split("\n")
        p = []
        for r in results:
            try:
                if r[-1] == ",":
                    p.append(r[:-1])
                else:
                    p.append(r)
            except IndexError:
                p.append(r[:-1])
        results = "\n".join(p)
        return results


class PTC(HeatCalibration):
    def __init__(self, fnames, fingers, bowlsizes):
        super().__init__(fnames, fingers, bowlsizes)
        self.ptc = None

    def compile(self):
        now = datetime.date.today()
        ptc = Parser()
        ptc.optionxform = str
        temps = [int(i) for i in self.passes.keys()]
        temps.sort()

        ptc["Calinfo"] = {
            "Date": f"{now.month}/{now.day}/{now.year}",
            "Serial": "GP12345",
            "Arms": self.fingers,
            "Temp": "F",
            "Diam": "in"
        }

        for i, temp in enumerate(temps):
            ptc[f"Temp{i+1}"] = {}
            ptc[f"Temp{i+1}"]['Temp'] = str(temp)

            for j, bowl in enumerate(self.bowlsizes):
                fing_avg = []
                for finger in range(self.fingers):
                    avg = self.passes[temp].data[f"R{finger+1:02}"]['data'][
                        f"bowlsize_{bowl}"].mean()

                    fing_avg.append(str(round(avg, 2)))
                joined = "\t".join(fing_avg)
                ptc[f"Temp{i+1}"][f"Diam{j+1}"] = str(mm2in(bowl))
                ptc[f"Temp{i+1}"][f"Meas{j+1}"] = joined
        self.ptc = ptc

    def write(self, fname):
        with open(fname, "w") as f:
            self.ptc.write(f)


class MTC(HeatCalibration):
    def __init__(self, fnames, fingers, bowlsizes):
        super().__init__(fnames, fingers, bowlsizes)

    def compile(self):
        mtc = f"gowell-heat-calibration {str(datetime.date.today())}\n"
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

            for temp in temps:
                temp_avg = self.passes[temp].data['TEMP']['data'].mean()
                mtc += f"{int(temp_avg):04},"
            mtc += "\n"

            for finger in range(self.fingers):
                for temp in temps:
                    fing_avg = self.passes[temp].data[f"R{finger+1:02}"][
                        'data'][f'bowlsize_{bowlsize}'].mean()
                    # print(finger + 1, f'bowlsize_{bowlsize}', fing_avg)
                    mtc += f"{int(fing_avg):04},"

                mtc += "\n"
        return mtc


if __name__ == "__main__":
    fnames = [
        "../examples/Gowell/93F-11019.LAS", "../examples/Gowell/71F-11019.LAS",
        "../examples/Gowell/45F-11019.LAS",
        "../examples/Gowell/118F-11019.LAS",
        "../examples/Gowell/144F-11019.LAS",
        "../examples/Gowell/169F-11019.LAS",
        "../examples/Gowell/194F-11019.LAS",
        "../examples/Gowell/219F-11019.LAS",
        "../examples/Gowell/244F-11019.LAS",
        "../examples/Gowell/270F-11019.LAS",
        "../examples/Gowell/295F-11019.LAS"
    ]

    # fnames = [
    #     "../examples/Probe/38F-11139.LAS", "../examples/Probe/73F-1139.LAS"
    # ]

    # mtc = MTC(fnames,
    #           fingers=24,
    #           bowlsizes=[47.6, 60.3, 76.2, 101.6, 127.0, 142.9, 152.4])
    # with open("results.mtc", "w") as f:
    #     results = mtc.compile()
    #     results = mtc.clean(results)
    #     f.write(results)
    ptc = PTC(fnames,
              fingers=24,
              bowlsizes=[47.6, 60.3, 76.2, 101.6, 127.0, 142.9, 152.4])
    ptc.compile()
