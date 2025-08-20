import os
import random
import shutil
import string
from pathlib import Path
import gzip
import zipfile

import h5py

from sagea.pysrc.auxiliary import Preference


class FileTool:

    # @staticmethod
    # def get_project_dir(sub=None, *, relative=False):
    #     dir_of_project = Path().absolute()
    #     relative_dir_str = Path('')
    #
    #     i = 0
    #     while True:
    #         i += 1
    #         if i > 100:
    #             raise Exception
    #
    #         if Path.exists(dir_of_project / 'sagea'):
    #             break
    #
    #         dir_of_project = dir_of_project.parent
    #         relative_dir_str /= '..'
    #
    #     if relative:
    #         result = relative_dir_str
    #         # return Path(relative_dir_str)
    #
    #     else:
    #         result = dir_of_project
    #         # return dir_of_project
    #
    #     if sub is not None:
    #         result /= sub
    #
    #     return result

    @staticmethod
    def is_iterable(obj):
        try:
            iter(obj)
            return True
        except TypeError:
            return False

    @staticmethod
    def get_files_in_dir(fp, sub=False):
        assert fp.is_dir, f"{fp} is not a directory."

        file_list = []

        iterlist = list(fp.iterdir())
        for i in range(len(iterlist)):
            if iterlist[i].is_file():
                if not iterlist[i].name.startswith('.'):
                    file_list.append(iterlist[i])

            elif sub:
                file_list += FileTool.get_files_in_dir(iterlist[i], sub=sub)

        return file_list

    @staticmethod
    def un_gz(gz_file_path: Path, target_path: Path = None):

        if target_path is None:
            target_path = gz_file_path.parent / gz_file_path.name.replace('.gz', '')

        g_file = gzip.GzipFile(gz_file_path)
        open(target_path, "wb+").write(g_file.read())
        g_file.close()

    @staticmethod
    def un_zip(zip_file_path: Path, target_path: Path = None):
        if target_path is None:
            target_path = zip_file_path.parent / zip_file_path.name.replace('.zip', '')

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(target_path)

    @staticmethod
    def get_l2_low_deg_path(filedir: Path = None,
                            file_id: Preference.L2LowDegreeFileID = None,
                            institute: Preference.L2InstituteType = None,
                            release: Preference.L2Release = None
                            ):

        filedir = FileTool.get_project_dir() / 'data/L2_low_degrees' if filedir is None else filedir

        if file_id == Preference.L2LowDegreeFileID.TN11:
            filedir /= 'TN-11_C20_SLR_RL06.txt'

        elif file_id == Preference.L2LowDegreeFileID.TN13:
            assert institute in (
                Preference.L2InstituteType.CSR, Preference.L2InstituteType.GFZ, Preference.L2InstituteType.JPL)
            assert release in (Preference.L2Release.RL06, Preference.L2Release.RL061)

            institute_str = institute.name
            release_str = release.name.replace('RL061', 'RL06.1')
            filedir /= f'TN-13_GEOC_{institute_str}_{release_str}.txt'

        elif file_id == Preference.L2LowDegreeFileID.TN14:
            filedir /= 'TN-14_C30_C20_SLR_GSFC.txt'

        else:
            raise Exception

        return filedir

    @staticmethod
    def get_hdf5_structure(filepath):
        def append_structure(fdata, flevel=0, texts=None):
            if texts is None:
                texts = []

            texts.append(f"{'|  ' * flevel}|--{fdata.name.split('/')[-1]}")

            if type(fdata) is h5py._hl.group.Group:
                flevel += 1
                texts.append('|  ' * flevel + '|')
                for fkey in fdata.keys():
                    append_structure(fdata[fkey], flevel, texts)
                flevel -= 1
                texts.append('|  ' * flevel + '|')

            elif type(fdata) is h5py._hl.dataset.Dataset:
                lines[-1] += f' {fdata.shape}'
                pass

            return texts

        filepath = Path(filepath)
        assert filepath.name.endswith('.hdf5')
        lines = []

        with h5py.File(filepath, 'r') as f:
            lines.append(f'{filepath.name}')
            lines.append('|')

            for key in f.keys():
                lines = append_structure(f[key], texts=lines)

        for i in range(len(lines) - 1, -1, -1):
            if lines[i].replace('|', '').replace(' ', '') == '':
                lines.pop(i)
            else:
                break

        return '\n'.join(lines)

    @staticmethod
    def get_GIA_path(filedir: Path = None, gia_type=Preference.GIAModel):
        assert gia_type in Preference.GIAModel

        filedir = FileTool.get_project_dir("data/GIA/") if filedir is None else filedir

        if gia_type == Preference.GIAModel.Caron2018:
            return filedir / "GIA.Caron_et_al_2018.txt"
        elif gia_type == Preference.GIAModel.Caron2019:
            return filedir / "GIA.Caron_Ivins_2019.txt"
        elif gia_type == Preference.GIAModel.ICE6GC:
            return filedir / "GIA.ICE-6G_C.txt"
        elif gia_type == Preference.GIAModel.ICE6GD:
            return filedir / "GIA.ICE-6G_D.txt"
        else:
            assert False

    @staticmethod
    def move_folder(src_folder, dst_folder):
        try:
            shutil.move(src_folder, dst_folder)
        except Exception as e:
            print(f"move files failed: {e}")

    @staticmethod
    def remove_file(filepath):
        os.remove(filepath)

    @staticmethod
    def add_ramdom_suffix(filename, length=None):
        if length is None:
            length = 16

        assert type(filename) is str or issubclass(type(filename), Path)

        random_str = ''.join(random.sample(string.ascii_letters + string.digits, length - 1)) + "_"

        if type(filename) is str:
            filename_split = filename.split('/')
            if len(filename_split) >= 2:
                return "/".join(filename_split[:-1]) + "/" + random_str + filename_split[-1]
            else:
                return random_str + filename_split[-1]

        elif issubclass(type(filename), Path):
            parent = filename.parent
            name = filename.name

            name_random = random_str + name

            return parent / name_random
