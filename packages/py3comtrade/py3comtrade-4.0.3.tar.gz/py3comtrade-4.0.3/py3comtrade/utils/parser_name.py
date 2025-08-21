#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd

from py3comtrade.model.type import AnalogFlag, PhaseCode


def parse_name(name_str):
    channel_type = AnalogFlag.ACV
    # 区分相别
    if name_str in ["电压", "U"]:
        channel_type = AnalogFlag.ACV
    elif name_str in ["电流", "I"]:
        channel_type = AnalogFlag.ACC
    elif name_str in ["功率因数"]:
        channel_type = AnalogFlag.AG
    elif name_str in ["频率"]:
        channel_type = AnalogFlag.FQ
    elif name_str in ["功率"]:
        channel_type = AnalogFlag.PW
    elif name_str in ["阻抗"]:
        channel_type = AnalogFlag.ZX
    phase = PhaseCode.A_PHASE
    if name_str in ["A", "a"]:
        phase = PhaseCode.A_PHASE
    elif name_str in ["B", "b"]:
        phase = PhaseCode.B_PHASE
    elif name_str in ["C", "c"]:
        phase = PhaseCode.C_PHASE
    elif name_str in ["N", "n", "I0", "i0"]:
        phase = PhaseCode.N_PHASE
    return {"channel_type": channel_type, "phase": phase}


if __name__ == '__main__':

    df = pd.read_csv("../../ext/analog_channel_names.csv")

    for index, row in df.iterrows():
        pn = parse_name(row.values[0])
        print(pn)
