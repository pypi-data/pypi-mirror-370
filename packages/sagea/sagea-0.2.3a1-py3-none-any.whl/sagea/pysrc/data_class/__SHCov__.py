#!/use/bin/env python
# coding=utf-8
# @Author  : Shuhao Liu
# @Time    : 2025/7/30 16:51 
# @File    : __SHCov__.py
import numpy as np


class SHCov:
    def __init__(self, cov_mat):
        self.__assert_value(cov_mat)

        self.__value = cov_mat

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__assert_value(value)
        self.__value = value

    @staticmethod
    def __assert_value(value: np.ndarray):
        assert value.ndim == 2
        assert value.shape[0] == value.shape[1]

        length_of_cs1d = np.shape(value)[0]
        assert (np.sqrt(length_of_cs1d) % 1) == 0

    def get_SHC(self, sample_num: int, base=None):
        from sagea import SHC

        cov_mat = self.value

        if base is None:
            base = np.array([0] * np.shape(cov_mat)[0])
        else:
            assert type(base) in (SHC, np.ndarray)

        if type(base) is SHC:
            assert len(SHC) == 1
            assert base.get_lmax() == self.get_lmax()
            base = base.value[0]
        else:
            base = base

        print(np.shape(cov_mat), np.shape(base))
        noise = np.random.multivariate_normal(
            mean=base,
            cov=cov_mat,
            size=sample_num
        )

        return SHC(noise)

    def get_lmax(self):
        """

        :return: int, max degree/order of the spherical harmonic coefficients stored in this class.
        """
        length_of_cs1d = np.shape(self.value)[-1]
        lmax = int(np.sqrt(length_of_cs1d) - 1)

        return lmax
