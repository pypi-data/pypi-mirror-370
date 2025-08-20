import pathlib
import re
import datetime

import numpy as np
from sagea.pysrc.auxiliary import Preference

from sagea.pysrc.auxiliary.FileTool import FileTool
from sagea.pysrc.auxiliary.TimeTool import TimeTool
from sagea.pysrc.data_class.__SHC__ import SHC


def match_dates_from_filename(filename):
    match_flag = False
    this_date_begin, this_date_end = None, None

    '''date format: yyyymmdd-yyyymmdd or yyyy-mm-dd-yyyy-mm-dd'''
    if not match_flag:
        date_begin_end_pattern = r"(\d{4})-?(\d{2})-?(\d{2})(-|_)(\d{4})-?(\d{2})-?(\d{2})"
        date_begin_end_searched = re.search(date_begin_end_pattern, filename)

        if date_begin_end_searched is not None:
            date_begin_end = date_begin_end_searched.groups()
            this_date_begin = datetime.date(*list(map(int, date_begin_end[:3])))
            this_date_end = datetime.date(*list(map(int, date_begin_end[4:])))

            match_flag = True

    '''date format: yyyyddd-yyyyddd'''
    if not match_flag:
        date_begin_end_pattern = r"(\d{4})(\d{3})-(\d{4})(\d{3})"
        date_begin_end_searched = re.search(date_begin_end_pattern, filename)

        if date_begin_end_searched is not None:
            date_begin_end = date_begin_end_searched.groups()
            this_date_begin = datetime.date(int(date_begin_end[0]), 1, 1) + datetime.timedelta(
                days=int(date_begin_end[1]) - 1)
            this_date_end = datetime.date(int(date_begin_end[2]), 1, 1) + datetime.timedelta(
                days=int(date_begin_end[3]) - 1)

            match_flag = True

    '''date format: yyyy-mm'''
    if not match_flag:
        date_begin_end_pattern = r"(\d{4})(-|_|)(\d{2})"
        date_begin_end_searched = re.search(date_begin_end_pattern, filename)

        if date_begin_end_searched is not None:
            year_month = date_begin_end_searched.groups()
            year = int(year_month[0])
            month = int(year_month[2])

            this_date_begin = datetime.date(int(year), month, 1)
            this_date_end = TimeTool.get_the_final_day_of_this_month(year=year, month=month)

            match_flag = True

    assert match_flag, (f"illegal date format in filename: {filename}. "
                        f"Filename should contain following one of parts: "
                        "yyyymmdd-yyyymmdd; "
                        "yyyy-mm-dd-yyyy-mm-dd; "
                        "yyyyddd-yyyyddd; "
                        "yyyy-mm."
                        )

    return this_date_begin, this_date_end


def load_SHC(filepath, lmax: int, key: str = None, read_rows=None, get_dates=False,
             dimension: Preference.Dimension = None):
    """

    :param dimension: physical dimension in sagea.Preference.Dimension
    :param filepath: path of standard SH file, or iterable of paths
    :param key: str, '' if there is not any key.
    :param lmax: max degree and order.
    :param read_rows: iter, Number of columns where degree l, order m, coefficient clm, and slm are located.
    :param get_dates: bool, if True return dates.
    :return: if get_dates is True:
                (each) filename should contain following one of parts:
                    "yyyymmdd-yyyymmdd";
                    "yyyy-mm-dd-yyyy-mm-dd";
                    "yyyyddd-yyyyddd";
                    "yyyy-mm"

                SHC instance, dates_begin, dates_end
            else:
                SHC instance
    """

    if key is None:
        key = ""

    def are_all_num(x: list):
        for i in read_rows:
            if x[i - 1].replace('e', '').replace('E', '').replace('E', '').replace('E', '').replace('-',
                                                                                                    '').replace(
                '+', '').replace('.', '').isnumeric():
                pass
            else:
                return False

        return True

    if FileTool.is_iterable(filepath) and (type(filepath) is not str):
        filepath_to_load = list(filepath)
    else:
        filepath_to_load = [pathlib.Path(filepath)]

    for i in range(len(filepath_to_load)):
        assert pathlib.Path(filepath_to_load[i]).exists(), f"{filepath_to_load[i]} does not exist"
        assert pathlib.Path(filepath_to_load[i]).is_file(), f"{filepath_to_load[i]} is not a file."
        assert type(filepath_to_load[i]) in (str,) or isinstance(filepath_to_load[i], pathlib.PurePath)

        if type(filepath_to_load[i]) is str:
            filepath_to_load[i] = pathlib.Path(filepath_to_load[i])

    if len(filepath_to_load) == 1:

        assert filepath_to_load[0].exists(), f"{filepath_to_load[0]} does not exist"

        if filepath_to_load[0].is_file():
            if read_rows is None:
                read_rows = [1, 2, 3, 4] if key == "" else [2, 3, 4, 5]

            l_queue = read_rows[0]
            m_queue = read_rows[1]
            c_queue = read_rows[2]
            s_queue = read_rows[3]

            mat_shape = (lmax + 1, lmax + 1)
            clm, slm = np.zeros(mat_shape), np.zeros(mat_shape)

            with open(filepath_to_load[0]) as f:
                txt_list = f.readlines()

                for i in range(len(txt_list)):
                    if txt_list[i].replace(" ", "").startswith(key):
                        this_line = txt_list[i].split()

                        # if len(this_line) == 4 and are_all_num(this_line):
                        if are_all_num(this_line):
                            l = int(this_line[l_queue - 1])
                            if l > lmax:
                                continue

                            m = int(this_line[m_queue - 1])

                            clm[l, m] = float(this_line[c_queue - 1])
                            slm[l, m] = float(this_line[s_queue - 1])

                        else:
                            continue

            if get_dates:
                this_date_begin, this_date_end = match_dates_from_filename(filepath_to_load[0].name)
                shc = SHC(clm, slm, dimension=dimension)

                return shc, [this_date_begin], [this_date_end]

            else:
                return SHC(clm, slm, dimension=dimension)

        elif filepath_to_load[0].is_dir():
            file_list = FileTool.get_files_in_dir(filepath_to_load[0], sub=True)
            file_list.sort()

            files_to_load = []

            for i in range(len(file_list)):
                files_to_load.append(file_list[i])

            return load_SHC(*files_to_load, key=key, lmax=lmax, read_rows=read_rows,
                            get_dates=get_dates, dimension=dimension)

    else:
        shc = None
        dates_begin, dates_end = [], []

        for i in range(len(filepath_to_load)):

            load = load_SHC(filepath_to_load[i], key=key, lmax=lmax, read_rows=read_rows,
                            get_dates=get_dates, dimension=dimension)

            if type(load) is tuple:
                assert len(load) in (1, 3)
                load_shc = load[0]
            else:
                load_shc = load

            if shc is None:
                shc = load_shc
            else:
                shc.append(
                    load_shc,
                )

            if get_dates:
                assert len(load) == 3
                d_begin, d_end = load[1], load[2]
                dates_begin.append(d_begin[0])
                dates_end.append(d_end[0])

        if get_dates:
            return shc, dates_begin, dates_end
        else:
            return shc
