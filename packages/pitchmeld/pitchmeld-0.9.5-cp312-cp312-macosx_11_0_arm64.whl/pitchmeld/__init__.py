# Copyright (C) 2024 Gilles Degottex <contact@pitchmeld.ing> All Rights Reserved.

import json  # Part of python stdlib
import atexit  # Part of python stdlib
import copy  # Part of python stdlib

import numpy as np

# Load the compiled library
try:
    from .sdk_python3_module import *

    atexit.register(unload)

    __version__ = import_version

    info = json.loads(import_info_str)

    def ola(wav, fs, *args, **kwargs):

        if wav.ndim == 1:
            return import_ola(wav, fs, *args, **kwargs)
        else:
            nbc = wav.shape[1]
            syn = import_ola(np.mean(wav, axis=1), fs, *args, **kwargs)
            syn = np.repeat(syn[:, None], nbc, axis=1)
            # syn = []
            # for c in range(wav.shape[1]):
            #     X = import_ola(wav[:,c].copy(), fs, *args, **kwargs)
            #     syn.append(X)
            # syn = np.vstack(syn).T

        return syn

    def estimation_f0(wav, fs, **kwargs):
        ret = import_estimation_f0(wav, fs, **kwargs)
        f0s = ret.reshape((-1, 3))
        return f0s

    def transform_timescaling(wav, fs, *args, **kwargs):
        if "winlen_inner" not in kwargs:
            kwargs["winlen_inner"] = int(fs * 0.015)
        return transform(wav, fs, *args, **kwargs)

    def transform_pitchscaling(wav, fs, *args, **kwargs):
        if "es_order_cst_f0" not in kwargs:
            kwargs["es_order_cst_f0"] = True
        return transform(wav, fs, *args, **kwargs)

    def transform(wav, fs, *args, **kwargs):
        assert len(args) == 0, "No positional arguments are expected after 'wav' and 'fs'. Please use keyword arguments only."

        kwargs_vectors = {}

        if "pbf" in kwargs:
            pbf = kwargs["pbf"]
            pbf = 1.0 / pbf
            if pbf > 1.0:
                tsf = pbf - 1.0
            elif pbf < 1.0:
                tsf = -(1.0 / pbf - 1.0)
            else:
                tsf = 0.0
            kwargs["tsf"] = tsf
            del kwargs["pbf"]

        if "pbfs" in kwargs:
            pbfs = kwargs["pbfs"]
            assert pbfs.ndim == 2, "pbfs should be a 2D array with shape (N, 2) where N is the number of time stamps."
            assert pbfs.shape[1] == 2, "pbfs should be a 2D array with shape (N, 2) where N is the number of time stamps."
            assert np.min(pbfs[:, 0]) >= 0, "pbfs[:,0], the time stamps, should be non-negative."
            assert np.max(pbfs[:, 0]) <= wav.shape[0] / fs, "pbfs[:,0] should not exceed the duration of the input signal."
            assert np.min(np.diff(pbfs[:, 0])) >= 0, "pbfs[:,0], the time stamps, should be increasing."
            assert np.min(pbfs[:, 1]) > 0, "pbfs[:,1] should be positive (time scaling factors)"
            if pbfs.shape[0] > 0:
                tsfs = np.zeros(pbfs.shape[0], dtype=np.float32)

                pbfsv = 1.0 / pbfs[:, 1]
                tsfs[pbfsv > 1.0] = pbfsv[pbfsv > 1.0] - 1.0
                tsfs[pbfsv < 1.0] = -(1.0 / pbfsv[pbfsv < 1.0] - 1.0)

                kwargs_vectors["tsfs_ts"] = np.array(pbfs[:, 0], dtype=np.float32)
                kwargs_vectors["tsfs_vs"] = tsfs
                del kwargs["pbfs"]

        if "psfs" in kwargs:
            psfs = kwargs["psfs"]
            assert psfs.ndim == 2, "psfs should be a 2D array with shape (N, 2) where N is the number of time stamps."
            assert psfs.shape[1] == 2, "psfs should be a 2D array with shape (N, 2) where N is the number of time stamps."
            assert np.min(psfs[:, 0]) >= 0, "psfs[:,0], the time stamps, should be non-negative."
            assert np.max(psfs[:, 0]) <= wav.shape[0] / fs, "psfs[:,0] should not exceed the duration of the input signal."
            if psfs.shape[0] > 1:
                assert np.min(np.diff(psfs[:, 0])) >= 0, "psfs[:,0], the time stamps should be increasing."
            assert np.min(psfs[:, 1]) > 0, "psfs[:,1] should be positive (pitch scaling factors)."
            if psfs.shape[0] > 0:
                kwargs_vectors["psfs_ts"] = np.array(psfs[:, 0], dtype=np.float32)
                kwargs_vectors["psfs_vs"] = np.array(psfs[:, 1], dtype=np.float32)
                del kwargs["psfs"]

            if "tsfs_ts" in kwargs_vectors:
                assert np.all(abs(kwargs_vectors["tsfs_ts"] - psfs[:, 0]) < float32.eps), "When using time varying for both time stretching and pitch scaling, pbfs[:,0] and psfs[:,0], the given time stamps, must be the same."

        if "set_f0s" in kwargs:
            set_f0s = kwargs["set_f0s"]
            assert set_f0s.ndim == 2, "set_f0s should be a 2D array with shape (N, 2) where N is the number of time stamps."
            assert set_f0s.shape[1] == 2, "set_f0s should be a 2D array with shape (N, 2) where N is the number of time stamps."
            assert np.min(set_f0s[:, 0]) >= 0, "set_f0s[:,0], the time stamps, should be non-negative."
            assert np.max(set_f0s[:, 0]) <= wav.shape[0] / fs, "set_f0s[:,0] should not exceed the duration of the input signal."
            if set_f0s.shape[0] > 1:
                assert np.min(np.diff(set_f0s[:, 0])) >= 0, "set_f0s[:,0], the time stamps should be increasing."
            assert np.min(set_f0s[:, 1]) > 0, "set_f0s[:,1] should be positive (f0 values to set)."
            if set_f0s.shape[0] > 0:
                kwargs_vectors["set_f0s_ts"] = np.array(set_f0s[:, 0], dtype=np.float32)
                kwargs_vectors["set_f0s_vs"] = np.array(set_f0s[:, 1], dtype=np.float32)
                del kwargs["set_f0s"]

            if "tsfs_ts" in kwargs_vectors:
                assert np.all(abs(kwargs_vectors["tsfs_ts"] - set_f0s[:, 0]) < float32.eps), "When using time varying for both time stretching and set_f0, pbfs[:,0] and set_f0s[:,0], the given time stamps, must be the same."

        if wav.ndim == 1:
            nbc = 1
            wav_in = wav
        else:
            nbc = wav.shape[1]
            # TODO This does not preserve spatialization
            wav_in = np.mean(wav, axis=1)

        syn, sync_status_reliability = import_transform(wav_in, fs, kwargs_vectors, **kwargs)

        if wav.ndim != 1:
            syn = np.repeat(syn[:, None], nbc, axis=1)

        if ("info" in kwargs) and kwargs["info"]:
            return syn, {"sync": {"reliability": sync_status_reliability}}
        else:
            return syn

except ModuleNotFoundError as e:

    import os  # Part of python stdlib
    import glob  # Part of python stdlib

    modulename = os.path.basename(os.path.dirname(__file__))

    print(f"Failed to import {modulename}: {e}")

    modules = glob.glob(os.path.dirname(__file__) + "/*.so")  # TODO .so is wrong on Windows and Mac
    if len(modules) == 0:
        print(f"No implementation found. The module is incomplete.\n")
    else:
        import sysconfig  # Part of python stdlib
        import platform  # Part of python stdlib
        import re  # Part of python stdlib

        def get_os_details(abi):
            version = "unknown version"
            arch = "unknown arch"
            os = "unknown os"
            try:
                res = re.search(r"cpython-([^-]+)-([^-]+)-(.+)", abi)

                version = res.group(1)
                version = version[:1] + "." + version[1:]

                arch = res.group(2)
                osname = res.group(3)
            except:
                # Can't block the information if this fails
                pass

            return f"Python {version}, Arch:{arch}, OS:{osname}"

        abi_current = sysconfig.get_config_var("SOABI")
        print(f"The version of the running python interpreter is {get_os_details(abi_current)} (ABI: {abi_current})")
        print(f"whereas this {modulename} module offers the versions:")
        for libfilepath in modules:
            libfilename = os.path.basename(libfilepath)
            abi_available = libfilename[len("sdk_python3_module.") : -len(".so")]
            print(f"    {get_os_details(abi_available)} (ABI: {abi_available})")

        print(f"It is very likely that this {modulename} module has been compiled for a different Python version, architecture or operating system.")

    raise e
