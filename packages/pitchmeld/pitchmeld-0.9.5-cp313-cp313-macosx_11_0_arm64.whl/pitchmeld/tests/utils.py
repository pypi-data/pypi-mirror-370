# Copyright (C) 2024 Gilles Degottex <contact@pitchmeld.ing> All Rights Reserved.

import logging

import os
import sys
import glob

import numpy as np
import soundfile

import pitchmeld

def assert_nan_inf(wav):
    idx = np.where(np.isnan(wav))[0]
    assert len(idx)==0

    idx = np.where(np.isinf(wav))[0]
    assert len(idx)==0

def assert_diff_sigs(ref, test, thresh_max=pitchmeld.float32.eps, thresh_rmse=pitchmeld.float32.eps):
    assert ref.shape == test.shape

    assert_nan_inf(test)

    err = ref - test

    if 0:
        os.makedirs(f'test_data/debug', exist_ok=True)
        err = ref - test
        soundfile.write(f'test_data/debug/{bbasename}.ref.wav', ref, fs)
        soundfile.write(f'test_data/debug/{bbasename}.test.wav', test, fs)
        soundfile.write(f'test_data/debug/{bbasename}.err.wav', err, fs)

    RMSE = np.sqrt(np.mean(err**2))
    MAXE = max(abs(err))
    info = {'RMSE':pitchmeld.lin2db(RMSE), 'MAXE':pitchmeld.lin2db(MAXE)}

    if RMSE > thresh_rmse:
        logging.error(f"RMSE is {pitchmeld.lin2db(RMSE):.3f}dB > {pitchmeld.lin2db(thresh_rmse):.3f}dB")
        return False, info

    if MAXE > thresh_max:
        logging.error(f'Max diff {pitchmeld.lin2db(MAXE):.3f}dB > {pitchmeld.lin2db(thresh_max):.3f}dB')
        # err_idx = np.where(abs(err)>thresh_max)[0]
        # if len(err_idx)>0:
        #     for n in err_idx:
        #         logging.error(f'ref[{n}]={ref[n]} test[{n}]={test[n]} err={err[n]} ({pitchmeld.lin2db(err[n])}dB) > {thresh_max} ({pitchmeld.lin2db(thresh_max)}dB)')

        return False, info

    return True, info


def filepaths_to_process():
    fpaths = glob.glob(f"{os.path.dirname(__file__)}/test_data/wav/*.wav")
    assert len(fpaths) > 0
    return fpaths


# def dir_refs(self):
#     return '../pitchmeld/sdk_python3/test_data/refs'

# def dir_output(self):
#     return 'test_data/sdk_python3'
