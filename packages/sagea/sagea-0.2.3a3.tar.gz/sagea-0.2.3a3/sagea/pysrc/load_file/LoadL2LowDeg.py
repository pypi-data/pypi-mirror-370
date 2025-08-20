import datetime
import pathlib
import re

import numpy as np

from sagea.pysrc.auxiliary.FileTool import FileTool
from sagea.pysrc.auxiliary.TimeTool import TimeTool


def __load_TN11(filepath, dates):
    with open(filepath) as f:
        txt = f.read()

    dates_begin_file, dates_end_file = [], []
    values_c20_file, values_c20_dev_file = [], []

    pat_data = r'\s*^\d{5}.*'
    data = re.findall(pat_data, txt, re.M)

    for i in data:
        line = i.split()

        dates_begin_file.append(TimeTool.convert_date_format(
            float(line[0]),
            input_type=TimeTool.DateFormat.MJD,
            output_type=TimeTool.DateFormat.ClassDate
        ))

        dates_end_file.append(TimeTool.convert_date_format(
            float(line[5]),
            input_type=TimeTool.DateFormat.MJD,
            output_type=TimeTool.DateFormat.ClassDate
        ))

        ave_dates_file = TimeTool.convert_date_format(
            (float(line[0]) + float(line[5])) / 2,
            input_type=TimeTool.DateFormat.MJD,
            output_type=TimeTool.DateFormat.ClassDate
        )

        values_c20_file.append(float(line[2]))
        values_c20_dev_file.append(float(line[4]) * 1e-10)

    c20, c20_dev = [], []
    for date in dates:
        this_index = np.where((np.array(dates_begin_file) < date) * (np.array(dates_end_file) > date))[0]

        if len(this_index) > 0:
            this_c20 = values_c20_file[this_index[0]]
            this_c20_dev = values_c20_dev_file[this_index[0]]
        else:
            this_c20, this_c20_dev = np.nan, np.nan

        c20.append(this_c20)
        c20_dev.append(this_c20_dev)

    result = dict(
        c20=np.array(c20),
        c20_dev=np.array(c20_dev)
    )
    return result


def __load_TN13(filepath, dates):
    with open(filepath) as f:
        txt = f.read()

    dates_begin_file, dates_end_file = [], []
    values_c10_file, values_c10_dev_file = [], []
    values_c11_file, values_c11_dev_file = [], []
    values_s11_file, values_s11_dev_file = [], []

    pat_data = r'^GRCOF2.*\w'
    data = re.findall(pat_data, txt, re.M)
    for i in data:
        line = i.split()
        m = int(line[2])

        if m == 0:
            ymd_begin = line[7][:8]
            date_begin = datetime.date(int(ymd_begin[:4]), int(ymd_begin[4:6]), int(ymd_begin[6:]))
            ymd_end = line[8][:8]
            date_end = datetime.date(int(ymd_end[:4]), int(ymd_end[4:6]), int(ymd_end[6:]))

            dates_begin_file.append(date_begin)
            dates_end_file.append(date_end)

            values_c10_file.append(float(line[3]))
            values_c10_dev_file.append(float(line[5]))

        elif m == 1:
            values_c11_file.append(float(line[3]))
            values_c11_dev_file.append(float(line[5]))

            values_s11_file.append(float(line[4]))
            values_s11_dev_file.append(float(line[6]))

    c10, c10_dev = [], []
    c11, c11_dev = [], []
    s11, s11_dev = [], []
    for date in dates:
        this_index = np.where((np.array(dates_begin_file) <= date) * (np.array(dates_end_file) >= date))[0]

        if len(this_index) > 0:
            this_c10 = values_c10_file[this_index[0]]
            this_c10_dev = values_c10_dev_file[this_index[0]]

            this_c11 = values_c11_file[this_index[0]]
            this_c11_dev = values_c11_dev_file[this_index[0]]

            this_s11 = values_s11_file[this_index[0]]
            this_s11_dev = values_s11_dev_file[this_index[0]]

        else:
            this_c10, this_c10_dev = np.nan, np.nan
            this_c11, this_c11_dev = np.nan, np.nan
            this_s11, this_s11_dev = np.nan, np.nan

        c10.append(this_c10)
        c10_dev.append(this_c10_dev)

        c11.append(this_c11)
        c11_dev.append(this_c11_dev)

        s11.append(this_s11)
        s11_dev.append(this_s11_dev)

    result = dict(
        c10=np.array(c10),
        c10_dev=np.array(c10_dev),
        c11=np.array(c11),
        c11_dev=np.array(c11_dev),
        s11=np.array(s11),
        s11_dev=np.array(s11_dev),
    )
    return result


def __load_TN14(filepath, dates):
    with open(filepath) as f:
        txt = f.read()

    values_c20_file = []
    values_c20_dev_file = []

    values_c30_file = []
    values_c30_dev_file = []

    dates_begin_file, dates_end_file = [], []

    pat_data = r'\s*^\d{5}.*'
    data = re.findall(pat_data, txt, re.M)
    for i in data:
        line = i.split()
        this_date_begin = TimeTool.convert_date_format(
            float(line[0]),
            input_type=TimeTool.DateFormat.MJD,
            output_type=TimeTool.DateFormat.ClassDate,
        )

        this_date_end = TimeTool.convert_date_format(
            float(line[8]),
            input_type=TimeTool.DateFormat.MJD,
            output_type=TimeTool.DateFormat.ClassDate,
        )

        dates_begin_file.append(this_date_begin)
        dates_end_file.append(this_date_end)

        if line[2] != 'NaN':
            values_c20_file.append(float(line[2]))
            values_c20_dev_file.append(float(line[4]) * 1e-10)
        else:
            values_c20_file.append(np.nan)
            values_c20_dev_file.append(np.nan)

        if line[5] != 'NaN':
            values_c30_file.append(float(line[5]))
            values_c30_dev_file.append(float(line[7]) * 1e-10)
        else:
            values_c30_file.append(np.nan)
            values_c30_dev_file.append(np.nan)

    c20, c20_dev = [], []
    c30, c30_dev = [], []
    for date in dates:
        this_index = np.where((np.array(dates_begin_file) < date) * (np.array(dates_end_file) > date))[0]

        if len(this_index) > 0:
            this_c20 = values_c20_file[this_index[0]]
            this_c20_dev = values_c20_dev_file[this_index[0]]

            this_c30 = values_c30_file[this_index[0]]
            this_c30_dev = values_c30_dev_file[this_index[0]]

        else:
            this_c20, this_c20_dev = np.nan, np.nan
            this_c30, this_c30_dev = np.nan, np.nan

        c20.append(this_c20)
        c20_dev.append(this_c20_dev)

        c30.append(this_c30)
        c30_dev.append(this_c30_dev)

    result = dict(
        c20=np.array(c20),
        c20_dev=np.array(c20_dev),
        c30=np.array(c30),
        c30_dev=np.array(c30_dev),
    )

    return result


def load_low_degs(filepath, dates):
    if FileTool.is_iterable(filepath) and (type(filepath) is not str):
        filepath_to_load = list(filepath)
    else:
        filepath_to_load = [pathlib.Path(filepath)]

    if len(filepath_to_load) == 1:
        this_filepath = filepath_to_load[0]

        if this_filepath.is_file():
            check_ids = ("TN-11", "TN-13", "TN-14")
            check_pattern = "(" + ")|(".join(check_ids) + ")"  # r"(TN-11)|(TN-13)|(TN-14)"
            checked = re.search(check_pattern, this_filepath.name) is not None
            if not checked:
                assert False, f"file name should include one of ids: {check_pattern}"

            if "TN-11" in this_filepath.name:
                return __load_TN11(this_filepath, dates)
            elif "TN-13" in this_filepath.name:
                return __load_TN13(this_filepath, dates)
            elif "TN-14" in this_filepath.name:
                return __load_TN14(this_filepath, dates)
            else:
                assert False

        elif this_filepath.is_dir():

            filepath_to_load = FileTool.get_l2_low_deg_path(this_filepath)

            return load_low_degs(filepath_to_load, dates)

    else:
        result = {}
        for i in range(len(filepath_to_load)):
            this_result = load_low_degs(filepath_to_load[i], dates)
            result.update(this_result)

        return result

    pass


def demo():
    dates = [
        datetime.date(2001, 1, 15),
        datetime.date(2010, 1, 15),
        datetime.date(2010, 1, 17),
        datetime.date(2010, 2, 15),
        datetime.date(2010, 3, 15),
        datetime.date(2010, 4, 15),
        datetime.date(2010, 5, 15),
        datetime.date(2010, 6, 15),
        datetime.date(2010, 7, 15),
        datetime.date(2010, 8, 15),
        datetime.date(2010, 9, 15),
        datetime.date(2010, 10, 15),
        datetime.date(2010, 11, 15),
        datetime.date(2010, 12, 15),
        datetime.date(2020, 12, 15),
    ]

    result_tn11 = __load_TN11(
        "/tests/data/L2_low_degrees/TN-11_C20_SLR_RL06.txt",
        dates=dates,
    )

    print(result_tn11.keys())
    print(result_tn11["c20_dev"])
    print(result_tn11["c20"] == result_tn11["c20"])

    result_tn13 = __load_TN13(
        "/tests/data/L2_low_degrees/TN-13_GEOC_CSR_RL06.txt",
        dates=dates,
    )

    print(result_tn13.keys())
    print(result_tn13["s11"])

    result_tn14 = __load_TN14(
        "/tests/data/L2_low_degrees/TN-14_C30_C20_SLR_GSFC.txt",
        dates=dates,
    )

    print(result_tn14.keys())
    print(result_tn14["c30"])

    result = {**result_tn11, **result_tn13, **result_tn14}
    print(result.keys())


if __name__ == '__main__':
    demo()
