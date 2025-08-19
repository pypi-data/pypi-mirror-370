# Copyright (C) 2024 Gilles Degottex <contact@pitchmeld.ing> All Rights Reserved.

import unittest

import logging

import os
import sys
import glob

import numpy as np
import soundfile

# sys.path.append(os.path.dirname(__file__)+'/../..')
import pitchmeld
import pitchmeld.tests.utils as utils

class TestModule(unittest.TestCase):

    def test_nothing(self):
        pass

    def test_transform_resynth(self):
        for fpath_in in utils.filepaths_to_process():
            with self.subTest(p1=[fpath_in]):
                bbasename = os.path.splitext(os.path.basename(fpath_in))[0]
                # print(f'INFO: Testing {fpath_in} ...')
                wav, fs = soundfile.read(fpath_in, dtype='float32')

                syn = pitchmeld.transform(wav, fs)

                self.assertFalse(np.isinf(syn).any())  # TODO Use utils.assert_nan_inf
                self.assertFalse(np.isnan(syn).any())  # TODO Use utils.assert_nan_inf
                self.assertTrue(utils.assert_diff_sigs(wav, syn, thresh_max=pitchmeld.db2lin(-42.0), thresh_rmse=pitchmeld.db2lin(-64.0)))

    def test_empty(self):
        wav = np.array([])
        syn = pitchmeld.transform(wav, 44100)
        self.assertTrue(len(syn) == 0)

    def test_transform_smoke(self):
        for fpath_in in utils.filepaths_to_process():
            wav, fs = soundfile.read(fpath_in, dtype='float32')
            for first_frame_at_t0 in [True, False]:
                for timestep in [int(fs*0.01), int(fs*0.05)]:
                    for winlen_inner in [int(fs*0.10), int(fs*0.20)]:
                        with self.subTest(p1=[fpath_in, first_frame_at_t0, timestep, winlen_inner]):
                            syn = pitchmeld.transform(wav, fs, first_frame_at_t0=first_frame_at_t0, timestep=timestep, winlen_inner=winlen_inner)
                            self.assertFalse(np.isinf(syn).any())  # TODO Use utils.assert_nan_inf
                            self.assertFalse(np.isnan(syn).any())  # TODO Use utils.assert_nan_inf

    def test_transform_pitch_scaling_smoke(self):
        for fpath_in in utils.filepaths_to_process():
            bbasename = os.path.splitext(os.path.basename(fpath_in))[0]
            wav, fs = soundfile.read(fpath_in, dtype='float32')

            for psf in [0.5, 0.75, 1.0, 1.5, 2.0]:
                for psf_max in [1.0, 1.5, 2.0]:
                    with self.subTest(p1=[fpath_in, psf, psf_max]):
                        syn = pitchmeld.transform(wav, fs, psf=psf, psf_max=psf_max)
                        self.assertFalse(np.isinf(syn).any())  # TODO Use utils.assert_nan_inf
                        self.assertFalse(np.isnan(syn).any())  # TODO Use utils.assert_nan_inf

    def test_transform_time_scaling_smoke(self):
        for fpath_in in utils.filepaths_to_process():
            bbasename = os.path.splitext(os.path.basename(fpath_in))[0]
            wav, fs = soundfile.read(fpath_in, dtype='float32')

            for pbf in [0.75, 1.0, 1.5]:
                for ts_bdi in [0.0, 0.1]:
                    for ts_bdt in [0.0, 0.1]:
                        for ts_ffb in [0.0, 0.1]:
                            for ts_bdm in [0.0, 2.0]:
                                with self.subTest(p1=[fpath_in, pbf, ts_bdi, ts_bdt, ts_ffb, ts_bdm]):
                                    syn = pitchmeld.transform(wav, fs, pbf=pbf, ts_bdi=ts_bdi, ts_ffb=ts_ffb, ts_bdt=ts_bdt, ts_bdm=ts_bdm)
                                    self.assertFalse(np.isinf(syn).any())  # TODO Use utils.assert_nan_inf
                                    self.assertFalse(np.isnan(syn).any())  # TODO Use utils.assert_nan_inf

            for ts_skip_start in [True, False]:
                with self.subTest(p1=[fpath_in, ts_skip_start]):
                    syn = pitchmeld.transform(wav, fs, ts_bdi=0.1, ts_skip_start=ts_skip_start)
                    self.assertFalse(np.isinf(syn).any())  # TODO Use utils.assert_nan_inf
                    self.assertFalse(np.isnan(syn).any())  # TODO Use utils.assert_nan_inf

if __name__ == '__main__':
    unittest.main()
