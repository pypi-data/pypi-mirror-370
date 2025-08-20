#!/use/bin/env python
# coding=utf-8
# @Author  : Shuhao Liu
# @Time    : 2025/6/16 21:01 
# @File    : collect_auxiliary.py
import pathlib
import os
import ssl

import wget

import sagea
from sagea.pysrc.auxiliary.FileTool import FileTool
from sagea.pysrc.data_collection.processing_bar import bar


def collect_auxiliary(local_dir):
    """download and unzip auxiliary and validation data from https://zenodo.org/records/15675307."""

    """prepare"""
    local_dir = pathlib.Path(local_dir)

    """download data"""
    url = f"https://zenodo.org/records/15675307/files/sagea_data.zip?download=1"

    local_path = local_dir / "sagea_data.zip"

    print(f"downloading: {url}")

    wget.download(url, str(local_path), bar=bar)

    print()

    print(f"unzipping: {local_path} ...")
    """unzip"""

    FileTool.un_zip(local_path, local_dir)

    os.remove(local_path)
    print("done!\n")


def collect_ddk_data(local_dir=None):
    """download and unzip auxiliary and validation data from https://zenodo.org/records/15679042."""

    if local_dir is None:
        local_dir = sagea.Preference.Config.aux_data_dir

    """prepare"""
    local_dir = pathlib.Path(local_dir)

    """download data"""
    url = f"https://zenodo.org/records/15679042/files/ddk_data.zip?download=1"

    local_path = local_dir / "sagea_data.zip"

    print(f"downloading DDK data from: {url}")

    wget.download(url, str(local_path), bar=bar)

    print()

    print(f"unzipping: {local_path} ...")
    """unzip"""

    FileTool.un_zip(local_path, local_dir)

    os.remove(local_path)
    print("done!\n")


if __name__ == "__main__":
    pass
