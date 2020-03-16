import lasio
import numpy as np
import datetime


class CaliperPass:
    def __init__(self, fname, fingers, bowlsizes, summary=False):
        self.fname = fname
        try:
            self.las = lasio.read(fname)
        except ValueError as err:
            print(err)
            print("You must generate LAS file with wrapping off")
        self.df = self.las.df().dropna()
        self.bowlsizes = bowlsizes
        self.data = {}

        # construct header for finger numbers
        self.finger_id = []
        for i in range(fingers):
            if i + 1 < 10:
                self.finger_id.append(f"R0{i+1}")
            else:
                self.finger_id.append(f"R{i+1}")

        # identify indexes for different bowlsizes
        # and construct dictionary to hold finger position with idxes of bowl transitions
        for idx, finger in enumerate(self.finger_id):
            self.data[finger] = {}
            finger_np = self.df[finger].to_numpy()
            bowls = [0] + self.segment_bowls(
                finger_np, threshold=50, to_skip=100) + [len(finger_np) - 1]
            if len(bowlsizes) != len(bowls) - 1:
                raise IndexError(
                    f"Bowl idxs must match length of detected bowlsizes for finger: {finger}\nBowl Idx Length: {len(bowls)}\nBowlsizes Length: {len(bowlsizes)}"
                )
            self.data[finger]['segments'] = bowls

        # do the same thing as above but use temp
        # the mnemonic will also change depending on Probe or GoWell
        try:  # try using GoWell
            temp = self.df["TEMP1"].to_numpy()
        except KeyError:
            temp = self.df["ETEMP.DEGF"].to_numpy()
        self.data['TEMP'] = {}
        self.data['TEMP']['preproc_data'] = temp
        self.clean_temp_data()
        self.clean_finger_data()

        if summary:
            self.summarize(log=True)

    def clean_finger_data(self):
        """
        Identifiies outliers in finger data and removes them
        by each bowl size
        """
        for finger, idxs in self.data.items():
            if finger == "TEMP":
                continue
            idxs = idxs['segments']
            self.data[finger]['data'] = {}
            self.data[finger]['preproc_data'] = {}

            finger_data = np.array([])
            for i, idx in enumerate(idxs):
                try:
                    start = idxs[i]
                    end = idxs[i + 1]
                except IndexError:
                    continue
                bowl_data = self.df[finger].to_numpy()[start:end]
                self.data[finger]['preproc_data'][
                    f'bowlsize_{self.bowlsizes[i]}'] = bowl_data
                outliers = np.where(
                    abs(bowl_data.mean() - bowl_data) > (bowl_data.std() *
                                                         2))[0]
                parsed_data = np.delete(bowl_data, outliers)
                finger_data = parsed_data
                # finger_data = np.hstack((finger_data, parsed_data))

                self.data[finger]['data'][
                    f'bowlsize_{self.bowlsizes[i]}'] = finger_data

    def clean_temp_data(self):
        """
        Identifies outliers in temp data and removes them
        """
        temp = self.data['TEMP']['preproc_data']
        idxs = np.where(abs(temp.mean() - temp) > (2 * temp.std()))[0]
        self.data['TEMP']['data'] = np.delete(temp, idxs)

    def summarize(self, log=False):
        summary_str = ""
        summary_str += f"\nSummary [{self.fname}]: \n"
        orig_v = 0
        data_v = 0
        for k, v in self.data.items():
            if k == "TEMP":
                continue
            data = sum([len(v['data'][i]) for i in v['data'].keys()])
            orig = sum(
                [len(v['preproc_data'][i]) for i in v['preproc_data'].keys()])
            # print(k, data, orig, f"{(orig - data) / orig * 100}%")
            orig_v += orig
            data_v += data

        temp_data = len(self.data['TEMP']['data'])
        temp_pre = len(self.data['TEMP']['preproc_data'])

        summary_str += f"\tData Reduction (Fingers): {(orig_v - data_v) / orig_v * 100}% [{orig_v - data_v}]\n"
        summary_str += f"\tData Reduction (Temperature): {(temp_pre-temp_data)/temp_pre*100}% [{orig_v - data_v}]"

        if log:
            with open("log.out", "a") as f:
                now = datetime.datetime.today().ctime()
                f.write(now + "\n" + summary_str + "\n")
        print(summary_str)

    def segment_bowls(self, arr, threshold, to_skip):
        skip = False
        counter = 0
        idxs = []
        for idx in range(len(arr)):
            if skip:
                if counter == to_skip:
                    skip = False
                    counter = 0
                else:
                    counter += 1
                    continue
            try:
                if abs(arr[idx + 1] - arr[idx]) > threshold:
                    idxs.append(idx)
                    skip = True
            except IndexError:
                pass
        return idxs


if __name__ == "__main__":
    cp45 = CaliperPass(fname="../examples/Gowell/45F-11019.LAS",
                       fingers=24,
                       bowlsizes=[1, 2, 3, 4, 5, 6, 7])
    cp45.summarize()