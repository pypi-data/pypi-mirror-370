# Copyright (C) 2024 Gilles Degottex <contact@pitchmeld.ing> All Rights Reserved.

import unittest

import logging

import os
import sys
import glob
import json

import numpy as np
import soundfile

# sys.path.append(os.path.dirname(__file__)+'/../..')
import pitchmeld
import pitchmeld.tests.utils as utils

class TestModule(unittest.TestCase):

    def test_info(self):
        self.assertTrue(len(pitchmeld.__version__)>0)
        self.assertTrue(len(pitchmeld.info)>0)

        self.assertEqual(pitchmeld.lin2db(2.0), +6.020600318908691)
        self.assertEqual(pitchmeld.lin2db(0.5), -6.020600318908691)

    def test_float(self):
        self.assertEqual(pitchmeld.float32.size, 4)
        self.assertTrue(pitchmeld.float32.eps<1e-6)
        self.assertTrue(pitchmeld.lin2db(pitchmeld.float32.min)<-750)
        self.assertTrue(pitchmeld.lin2db(pitchmeld.float32.max)>+750)

        self.assertEqual(pitchmeld.float64.size, 8)
        self.assertTrue(pitchmeld.float64.eps<1e-15)
        self.assertTrue(pitchmeld.float64.min<1e-300)
        self.assertTrue(pitchmeld.float64.max>1e+300)

    def test_ola_smoke(self):
        for fpath_in in utils.filepaths_to_process():
            wav, fs = soundfile.read(fpath_in, dtype='float32')
            for first_frame_at_t0 in [True, False]:
                for timestep in [int(fs*0.01), int(fs*0.05)]:
                    for winlen in [int(fs*0.10), int(fs*0.20)]:
                        with self.subTest(p1=[fpath_in, first_frame_at_t0, timestep, winlen]):
                            syn = pitchmeld.ola(wav, fs, first_frame_at_t0=first_frame_at_t0, timestep=timestep, winlen=winlen)

    def test_ola_resynth(self):
        for fpath_in in utils.filepaths_to_process():
            with self.subTest(p1=[fpath_in]):
                wav, fs = soundfile.read(fpath_in, dtype='float32')
                self.assertTrue(len(wav)>0)
                syn = pitchmeld.ola(wav, fs)
                self.assertTrue(len(syn)>0)
                self.assertTrue(len(syn) == len(wav))
                self.assertTrue(utils.assert_diff_sigs(wav, syn, thresh_max=pitchmeld.db2lin(-140.0), thresh_rmse=pitchmeld.db2lin(-140.0)))

if __name__ == '__main__':
    unittest.main()
