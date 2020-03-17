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


def do_peek(fname):
    answer = sg.PopupYesNo("Do you want to view file?")
    if answer.lower() == "yes":
        with open(Path(fname).resolve(), "r") as f:
            contents = f.read()
        layout = [[sg.Multiline(contents, disabled=True, size=(200, 600))]]
        window = sg.Window("File Preview", layout=layout, size=(500, 500))
        window.finalize()
        while True:
            e, v = window.read()

            if e is None:
                break
        window.close()


def parse_bowl_sizes(sizes: str) -> list:
    sizes = sizes.split(",")
    return [float(i) for i in [j for j in sizes if j]]


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

    rc = [[
        sg.Checkbox("MTC", key="gowell", default=True, change_submits=True)
    ], [sg.Checkbox("PTC", key="probe", change_submits=True)],
          [
              sg.Text("Fingers: "),
              sg.Combo(values=[24, 40, 56],
                       key="arms",
                       size=(2, 1),
                       default_value=24)
          ]]

    layout = [[sg.Column(layout=lc), sg.Column(layout=rc)]]
    window = sg.Window("Heat Cal Calc", layout=layout)

    while True:
        event, values = window.read()

        if event in (None, "Quit"):
            break

        if event in ("gowell", "probe"):
            if event == "gowell":
                window['gowell'].Update(value=True)
                window['probe'].Update(value=False)
            elif event == "probe":
                window['gowell'].Update(value=False)
                window['probe'].Update(value=True)

        if event == "file_browser":
            fingers = int(values['arms'])
            bowlsizes = parse_bowl_sizes(values["bowlsizes"])
            if values['gowell'] is True:
                answer = sg.PopupYesNo("Generate MTC File?")
                if answer.lower() == "yes":
                    sg.PopupNonBlocking("Generating file...please wait",
                                        auto_close=True)
                    files = values[event].split(";")
                    mtc = MTC(files, fingers=fingers, bowlsizes=bowlsizes)
                    results = mtc.compile()
                    results = mtc.clean(results)
                    to_file("results.mtc", results)
                    do_peek("results.mtc")

            elif values['probe'] is True:
                answer = sg.PopupYesNo("Generate PTC File?")
                if answer.lower() == "yes":
                    sg.PopupNonBlocking("Generating file...please wait",
                                        auto_close=True)
                    files = values[event].split(";")
                    ptc = PTC(files, fingers=fingers, bowlsizes=bowlsizes)
                    ptc.compile()
                    to_file("results.ptc", ptc)
                    do_peek("results.ptc")
