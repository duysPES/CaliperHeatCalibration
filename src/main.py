import PySimpleGUI as sg
from mtc import MTC, PTC
from pathlib import Path
import datetime


def to_file(fname, pyobj):
    p = Path(f"../{fname}").resolve()

    # store in parent directory
    if isinstance(pyobj, PTC):
        pyobj.write(p)
    else:
        with open(p, "w") as f:
            f.write(str(pyobj))


def parse_bowl_sizes(sizes: str) -> list:
    sizes = sizes.split(",")
    return [float(i) for i in sizes]


if __name__ == "__main__":
    lc = [[sg.Text("Enter Bowlsizes Below (mm) (commas and no spaces")],
          [
              sg.InputText("47.6,60.3,76.2,101.6,127.0,142.9,152.4",
                           key="bowlsizes")
          ],
          [
              sg.FilesBrowse("Select .LAS files",
                             enable_events=True,
                             key="file_browser")
          ]]

    rc = [[sg.Checkbox(
        "MTC",
        key="gowell",
    )], [sg.Checkbox("PTC", key="probe")]]

    layout = [[sg.Column(layout=lc), sg.Column(layout=rc)]]
    window = sg.Window("Heat Cal Calc", layout=layout)

    while True:
        event, values = window.read()

        if event in (None, "Quit"):
            break

        if event == "file_browser":
            if values["gowell"] is not True and values['probe'] is not True:
                sg.PopupAutoClose(
                    "You must select either PTC or MTC file to generate")
                continue

            if values["gowell"] is True and values['probe'] is True:
                sg.PopupAutoClose("You can only select one type.")
                continue

            bowlsizes = parse_bowl_sizes(values["bowlsizes"])
            if values['gowell'] is True:
                answer = sg.PopupYesNo("Generate MTC File?")
                if answer.lower() == "yes":
                    sg.PopupNonBlocking("Generating file...please wait",
                                        auto_close=True)
                    files = values[event].split(";")
                    mtc = MTC(files, fingers=24, bowlsizes=bowlsizes)
                    results = mtc.compile()
                    results = mtc.clean(results)
                    to_file("results.mtc", results)
                    sg.PopupOK(
                        "Finished Conversion. Check 'log.out' for more information",
                        keep_on_top=True)
                    break
            elif values['probe'] is True:
                answer = sg.PopupYesNo("Generate PTC File?")
                if answer.lower() == "yes":
                    sg.PopupNonBlocking("Generating file...please wait",
                                        auto_close=True)
                    files = values[event].split(";")
                    ptc = PTC(files, fingers=24, bowlsizes=bowlsizes)
                    ptc.compile()
                    to_file("results.ptc", ptc)
                    sg.PopupOK(
                        "Finished Conversion. Check 'log.out' for more information",
                        keep_on_top=True)
                    break
