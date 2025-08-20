# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 00:18:50 2023

@author: osama
"""
import sys
from glob import glob
import datetime
import pandas as pd
import numpy as np
from loone_data_prep.data_analyses_fns import DF_Date_Range
from loone_data_prep.utils import stg2sto, stg2ar


M3_Yr = 2008
M3_M = 1
M3_D = 1
D2_Yr = 2007
D2_M = 12
D2_D = 30
St_Yr = 2008
St_M = 1
St_D = 1
En_Yr = 2024
En_M = 9
En_D = 30

# Tp Concentrations Dataframe
TP_df = None

def main(input_dir: str, output_dir: str) -> None:
    # To create File (Average_LO_Storage)
    # Read LO Average Stage (ft)
    LO_Stage = pd.read_csv(f'{input_dir}/LO_Stage.csv')
    # Create Column (EOD Stg(ft, NGVD)) in File (SFWMM_Daily_Outputs)
    # LO_Stage = DF_Date_Range(LO_Stage, M3_Yr, M3_M, M3_D, En_Yr, En_M, En_D)
    # Calculate average
    if "Average_Stage" not in LO_Stage.columns:
        LO_Stage = LO_Stage.loc[:, ~LO_Stage.columns.str.contains('^Unnamed')]
        LO_Stage['Average_Stage'] = LO_Stage.mean(axis=1, numeric_only=True)
        LO_Stage.to_csv(f'{input_dir}/LO_Stage.csv', index=False)
    LO_Storage = stg2sto(f'{input_dir}/StgSto_data.csv', LO_Stage['Average_Stage'], 0)
    LO_SA = stg2ar(f'{input_dir}/Stgar_data.csv', LO_Stage['Average_Stage'], 0)
    LO_Stg_Sto_SA_df = pd.DataFrame(LO_Stage['date'], columns=['date'])
    LO_Stg_Sto_SA_df['Stage_ft'] = LO_Stage['Average_Stage']
    LO_Stg_Sto_SA_df['Stage_m'] = LO_Stg_Sto_SA_df['Stage_ft'].values * 0.3048  # ft to m
    LO_Stg_Sto_SA_df['Storage_acft'] = LO_Storage
    LO_Stg_Sto_SA_df['Storage_cmd'] = LO_Stg_Sto_SA_df['Storage_acft'] * 1233.48  # acft to m3/d
    LO_Stg_Sto_SA_df['SA_acres'] = LO_SA  # acres

    # Read flow data cubic meters per day
    S65_total = pd.read_csv(f'{input_dir}/S65E_total.csv')
    S65_total["S65E_tot_cmd"] = S65_total[["S65E_S_FLOW_cfs", "S65EX1_S_FLOW_cfs"]].sum(axis=1)
    S71_S = pd.read_csv(f'{input_dir}/S71_S_FLOW_cmd.csv')
    S72_S = pd.read_csv(f'{input_dir}/S72_S_FLOW_cmd.csv')
    S84_S = pd.read_csv(f'{input_dir}/S84_S_FLOW_cmd.csv')
    S127_C = pd.read_csv(f'{input_dir}/S127_C_FLOW_cmd.csv')
    S127_P = pd.read_csv(f'{input_dir}/S127_P_FLOW_cmd.csv')
    S129_C = pd.read_csv(f'{input_dir}/S129_C_FLOW_cmd.csv')
    S129_P = pd.read_csv(f'{input_dir}/S129_PMP_P_FLOW_cmd.csv')
    S133_P = pd.read_csv(f'{input_dir}/S133_P_FLOW_cmd.csv')
    S135_C = pd.read_csv(f'{input_dir}/S135_C_FLOW_cmd.csv')
    S135_P = pd.read_csv(f'{input_dir}/S135_PMP_P_FLOW_cmd.csv')
    S154_C = pd.read_csv(f'{input_dir}/S154_C_FLOW_cmd.csv')
    S191_S = pd.read_csv(f'{input_dir}/S191_S_FLOW_cmd.csv')
    S308 = pd.read_csv(f'{input_dir}/S308.DS_FLOW_cmd.csv')
    S351_S = pd.read_csv(f'{input_dir}/S351_S_FLOW_cmd.csv')
    S352_S = pd.read_csv(f'{input_dir}/S352_S_FLOW_cmd.csv')
    S354_S = pd.read_csv(f'{input_dir}/S354_S_FLOW_cmd.csv')
    FISHP = pd.read_csv(f'{input_dir}/FISHP_FLOW_cmd.csv')
    L8 = pd.read_csv(f'{input_dir}/L8.441_FLOW_cmd.csv')
    S2_P = pd.read_csv(f'{input_dir}/S2_P_FLOW_cmd.csv')
    S3_P = pd.read_csv(f'{input_dir}/S3_P_FLOW_cmd.csv')
    S4_P = pd.read_csv(f'{input_dir}/S4_P_FLOW_cmd.csv')

    S77_S = pd.read_csv(f'{input_dir}/S77_S_FLOW_cmd.csv')
    INDUST = pd.read_csv(f'{input_dir}/INDUST_FLOW_cmd.csv')

    # Read Interpolated TP data
    # Data_Interpolation Python Script is used to interpolate TP data for all inflow stations addressed below!
    S65_total_TP = pd.read_csv(f'{input_dir}/water_quality_S65E_PHOSPHATE, TOTAL AS P_Interpolated.csv')
    S71_TP = pd.read_csv(f'{input_dir}/water_quality_S71_PHOSPHATE, TOTAL AS P_Interpolated.csv')
    S72_TP = pd.read_csv(f'{input_dir}/water_quality_S72_PHOSPHATE, TOTAL AS P_Interpolated.csv')
    S84_TP = pd.read_csv(f'{input_dir}/water_quality_S84_PHOSPHATE, TOTAL AS P_Interpolated.csv')
    S127_TP = pd.read_csv(f'{input_dir}/water_quality_S127_PHOSPHATE, TOTAL AS P_Interpolated.csv')
    S133_TP = pd.read_csv(f'{input_dir}/water_quality_S133_PHOSPHATE, TOTAL AS P_Interpolated.csv')
    S135_TP = pd.read_csv(f'{input_dir}/water_quality_S135_PHOSPHATE, TOTAL AS P_Interpolated.csv')
    S154_TP = pd.read_csv(f'{input_dir}/water_quality_S154_PHOSPHATE, TOTAL AS P_Interpolated.csv')
    S191_TP = pd.read_csv(f'{input_dir}/water_quality_S191_PHOSPHATE, TOTAL AS P_Interpolated.csv')
    S308_TP = pd.read_csv(f'{input_dir}/water_quality_S308C_PHOSPHATE, TOTAL AS P_Interpolated.csv')
    FISHP_TP = pd.read_csv(f'{input_dir}/water_quality_FECSR78_PHOSPHATE, TOTAL AS P_Interpolated.csv')
    L8_TP = pd.read_csv(f'{input_dir}/water_quality_CULV10A_PHOSPHATE, TOTAL AS P_Interpolated.csv')
    S4_TP = pd.read_csv(f'{input_dir}/water_quality_S4_PHOSPHATE, TOTAL AS P_Interpolated.csv')

    # Set date range for S65 TP
    S65_total_TP = DF_Date_Range(S65_total_TP, M3_Yr, M3_M, M3_D, En_Yr, En_M, En_D)

    # Set Date Range
    Q_names = ['S65_Q', 'S71_Q', 'S72_Q', 'S84_Q', 'S127_C_Q', 'S127_P_Q', 'S129_C_Q', 'S129_P_Q', 'S133_P_Q',
               'S135_C_Q', 'S135_P_Q', 'S154_Q', 'S191_Q', 'S308_Q', 'S351_Q', 'S352_Q', 'S354_Q', 'FISHP_Q', 'L8_Q',
               'S2_P_Q', 'S3_P_Q', 'S4_P_Q', 'S77_Q', 'INDUST_Q']
    Q_list = {'S65_Q': S65_total, 'S71_Q': S71_S, 'S72_Q': S72_S, 'S84_Q': S84_S, 'S127_C_Q': S127_C,
              'S127_P_Q': S127_P, 'S129_C_Q': S129_C, 'S129_P_Q': S129_P, 'S133_P_Q': S133_P, 'S135_C_Q': S135_C,
              'S135_P_Q': S135_P, 'S154_Q': S154_C, 'S191_Q': S191_S, 'S308_Q': S308, 'S351_Q': S351_S,
              'S352_Q': S352_S, 'S354_Q': S354_S, 'FISHP_Q': FISHP, 'L8_Q': L8, 'S2_P_Q': S2_P, 'S3_P_Q': S3_P,
              'S4_P_Q': S4_P, 'S77_Q': S77_S, 'INDUST_Q': INDUST}
    # Identify date range
    date = pd.date_range(start=f'{M3_M}/{M3_D}/{M3_Yr}', end=f'{En_M}/{En_D}/{En_Yr}', freq='D')
    # Create Flow Dataframe
    Flow_df = pd.DataFrame(date, columns=['date'])
    for i in range(len(Q_names)):
        x = DF_Date_Range(Q_list[Q_names[i]], M3_Yr, M3_M, M3_D, En_Yr, En_M, En_D)
        if len(x.iloc[:, -1:].values) == len(Flow_df['date']):
            Flow_df[Q_names[i]] = x.iloc[:, -1:].values
        else:
            x.rename(columns={x.columns[-1]: Q_names[i]}, inplace=True)
            Flow_df = pd.merge(Flow_df, x[['date', Q_names[i]]], on='date', how='left')

    Flow_df['S127_C_Q'] = Flow_df['S127_C_Q'][Flow_df['S127_C_Q'] >= 0]
    Flow_df['S127_C_Q'] = Flow_df['S127_C_Q'].fillna(0)
    Flow_df['S127_In'] = Flow_df[["S127_C_Q", "S127_P_Q"]].sum(axis=1)
    Flow_df['S129_C_Q'] = Flow_df['S129_C_Q'][Flow_df['S129_C_Q'] >= 0]
    Flow_df['S129_C_Q'] = Flow_df['S129_C_Q'].fillna(0)
    Flow_df['S129_In'] = Flow_df[["S129_C_Q", "S129_P_Q"]].sum(axis=1)
    Flow_df['S135_C_Q'] = Flow_df['S135_C_Q'][Flow_df['S135_C_Q'] >= 0]
    Flow_df['S135_C_Q'] = Flow_df['S135_C_Q'].fillna(0)
    Flow_df['S135_In'] = Flow_df[["S135_C_Q", "S135_P_Q"]].sum(axis=1)
    Flow_df['S308_In'] = Flow_df['S308_Q'][Flow_df['S308_Q'] < 0]
    Flow_df['S308_In'] = Flow_df['S308_In'] * -1
    Flow_df['S308_In'] = Flow_df['S308_In'].fillna(0)
    Flow_df['S77_In'] = Flow_df['S77_Q'][Flow_df['S77_Q'] < 0]
    Flow_df['S77_In'] = Flow_df['S77_In'] * -1
    Flow_df['S77_In'] = Flow_df['S77_In'].fillna(0)
    Flow_df['S351_In'] = Flow_df['S351_Q'][Flow_df['S351_Q'] < 0]
    Flow_df['S351_In'] = Flow_df['S351_In'] * -1
    Flow_df['S351_In'] = Flow_df['S351_In'].fillna(0)
    Flow_df['S352_In'] = Flow_df['S352_Q'][Flow_df['S352_Q'] < 0]
    Flow_df['S352_In'] = Flow_df['S352_In'] * -1
    Flow_df['S352_In'] = Flow_df['S352_In'].fillna(0)
    Flow_df['S354_In'] = Flow_df['S354_Q'][Flow_df['S354_Q'] < 0]
    Flow_df['S354_In'] = Flow_df['S354_In'] * -1
    Flow_df['S354_In'] = Flow_df['S354_In'].fillna(0)
    Flow_df['L8_In'] = Flow_df['L8_Q'][Flow_df['L8_Q'] < 0]
    Flow_df['L8_In'] = Flow_df['L8_In'] * -1
    Flow_df['L8_In'] = Flow_df['L8_In'].fillna(0)
    Flow_df['S308_Out'] = Flow_df['S308_Q'][Flow_df['S308_Q'] >= 0]
    Flow_df['S308_Out'] = Flow_df['S308_Out'].fillna(0)
    Flow_df['S77_Out'] = Flow_df['S77_Q'][Flow_df['S77_Q'] >= 0]
    Flow_df['S77_Out'] = Flow_df['S77_Out'].fillna(0)
    Flow_df['INDUST_Out'] = Flow_df['INDUST_Q'][Flow_df['INDUST_Q'] >= 0]
    Flow_df['INDUST_Out'] = Flow_df['INDUST_Out'].fillna(0)
    Flow_df['S351_Out'] = Flow_df['S351_Q'][Flow_df['S351_Q'] >= 0]
    Flow_df['S351_Out'] = Flow_df['S351_Out'].fillna(0)
    Flow_df['S352_Out'] = Flow_df['S352_Q'][Flow_df['S352_Q'] >= 0]
    Flow_df['S352_Out'] = Flow_df['S352_Out'].fillna(0)
    Flow_df['S354_Out'] = Flow_df['S354_Q'][Flow_df['S354_Q'] >= 0]
    Flow_df['S354_Out'] = Flow_df['S354_Out'].fillna(0)
    Flow_df['L8_Out'] = Flow_df['L8_Q'][Flow_df['L8_Q'] >= 0]
    Flow_df['L8_Out'] = Flow_df['L8_Out'].fillna(0)
    Flow_df['Inflows'] = Flow_df[["S65_Q", "S71_Q", 'S72_Q', 'S84_Q', 'S127_In', 'S129_In', 'S133_P_Q', 'S135_In',
                                  'S154_Q', 'S191_Q', 'S308_In', 'S77_In', 'S351_In', 'S352_In', 'S354_In', 'L8_In',
                                  'FISHP_Q', 'S2_P_Q', 'S3_P_Q', 'S4_P_Q']].sum(axis=1)
    Flow_df['Netflows'] = Flow_df['Inflows'] - Flow_df['INDUST_Out']
    flow_filter_cols = ["S308_Out", "S77_Out", 'S351_Out', 'S352_Out', 'S354_Out', 'INDUST_Out', 'L8_Out']
    Flow_df['Outflows'] = Flow_df[flow_filter_cols].sum(axis=1)
    TP_names = ['S65_TP', 'S71_TP', 'S72_TP', 'S84_TP', 'S127_TP', 'S133_TP', 'S135_TP', 'S154_TP', 'S191_TP',
                'S308_TP', 'FISHP_TP', 'L8_TP', 'S4_TP']
    TP_list = {'S65_TP': S65_total_TP, 'S71_TP': S71_TP, 'S72_TP': S72_TP, 'S84_TP': S84_TP, 'S127_TP': S127_TP,
               'S133_TP': S133_TP, 'S135_TP': S135_TP, 'S154_TP': S154_TP, 'S191_TP': S191_TP, 'S308_TP': S308_TP,
               'FISHP_TP': FISHP_TP, 'L8_TP': L8_TP, 'S4_TP': S4_TP}
    # Create TP Concentrations Dataframe
    TP_df = pd.DataFrame(date, columns=['date'])
    for i in range(len(TP_names)):
        y = DF_Date_Range(TP_list[TP_names[i]], M3_Yr, M3_M, M3_D, En_Yr, En_M, En_D)
        if len(y.iloc[:, -1:].values) == len(TP_df['date']):
            TP_df[TP_names[i]] = y.iloc[:, -1:].values
        else:
            y.rename(columns={y.columns[-1]: TP_names[i]}, inplace=True)
            TP_df = pd.merge(TP_df, y[['date', TP_names[i]]], on='date', how='left')

    # Determine TP Loads (mg)
    TP_Loads_In = pd.DataFrame(date, columns=['date'])
    TP_Loads_In['S65_P_Ld'] = Flow_df['S65_Q'] * TP_df['S65_TP'] * 1000  # (m3/d * mg/L * 1000 = mg/d)
    TP_Loads_In['S71_P_Ld'] = Flow_df['S71_Q'] * TP_df['S71_TP'] * 1000
    TP_Loads_In['S72_P_Ld'] = Flow_df['S72_Q'] * TP_df['S72_TP'] * 1000
    TP_Loads_In['S84_P_Ld'] = Flow_df['S84_Q'] * TP_df['S84_TP'] * 1000
    TP_Loads_In['S127_P_Ld'] = Flow_df['S127_In'] * TP_df['S127_TP'] * 1000
    TP_Loads_In['S133_P_Ld'] = Flow_df['S133_P_Q'] * TP_df['S133_TP'] * 1000
    TP_Loads_In['S135_P_Ld'] = Flow_df['S135_In'] * TP_df['S135_TP'] * 1000
    TP_Loads_In['S154_P_Ld'] = Flow_df['S154_Q'] * TP_df['S154_TP'] * 1000
    TP_Loads_In['S191_P_Ld'] = Flow_df['S191_Q'] * TP_df['S191_TP'] * 1000
    TP_Loads_In['S308_P_Ld'] = Flow_df['S308_In'] * TP_df['S308_TP'] * 1000
    TP_Loads_In['FISHP_P_Ld'] = Flow_df['FISHP_Q'] * TP_df['FISHP_TP'] * 1000
    TP_Loads_In['L8_P_Ld'] = Flow_df['L8_In'] * TP_df['L8_TP'] * 1000
    TP_Loads_In['S4_P_Ld'] = Flow_df['S4_P_Q'] * TP_df['S4_TP'] * 1000
    # Calculate the total External Loads to Lake Okeechobee
    TP_Loads_In['External_P_Ld_mg'] = TP_Loads_In.sum(axis=1, numeric_only=True)

    # Create File (LO_External_Loadings_3MLag)
    TP_Loads_In_3MLag = DF_Date_Range(TP_Loads_In, M3_Yr, M3_M, M3_D, En_Yr, En_M, En_D)
    TP_Loads_In_3MLag_df = pd.DataFrame(TP_Loads_In_3MLag['date'], columns=['date'])
    TP_Loads_In_3MLag_df['TP_Loads_In_mg'] = TP_Loads_In_3MLag['External_P_Ld_mg']
    TP_Loads_In_3MLag_df['Atm_Loading_mg'] = [95890410.96] * len(TP_Loads_In_3MLag_df)

    # Create File (LO_Inflows_BK)
    LO_Inflows_BK = pd.DataFrame(Flow_df['date'], columns=['date'])
    LO_Inflows_BK['Inflows_cmd'] = Flow_df['Inflows']
    LO_Inflows_BK = DF_Date_Range(LO_Inflows_BK, St_Yr, St_M, St_D, En_Yr, En_M, En_D)

    # Create File (Outflows_consd_20082023)
    Outflows_consd = pd.DataFrame(Flow_df['date'], columns=['date'])
    Outflows_consd['Outflows_acft'] = Flow_df['Outflows']/1233.48  # acft
    Outflows_consd = DF_Date_Range(Outflows_consd, St_Yr, St_M, St_D, En_Yr, En_M, En_D)

    # Create File (INDUST_Outflow_20082023)
    INDUST_Outflows = pd.DataFrame(Flow_df['date'], columns=['date'])
    INDUST_Outflows['INDUST'] = Flow_df['INDUST_Out']

    # Create File (Netflows_acft)
    # This is also Column (Net Inflow) in File (SFWMM_Daily_Outputs)
    Netflows = pd.DataFrame(Flow_df['date'], columns=['date'])
    Netflows['Netflows_acft'] = Flow_df['Netflows']/1233.48  # acft
    Netflows = DF_Date_Range(Netflows, D2_Yr, D2_M, D2_D, En_Yr, En_M, En_D)

    # Create File (TotalQWCA_Obs)
    # This is also Column (RegWCA) in File (SFWMM_Daily_Outputs)
    TotalQWCA = pd.DataFrame(Flow_df['date'], columns=['date'])
    TotalQWCA['S351_Out'] = Flow_df['S351_Out'] * (35.3147/86400)  # cmd to cfs
    TotalQWCA['S354_Out'] = Flow_df['S354_Out'] * (35.3147/86400)
    TotalQWCA['RegWCA_cfs'] = TotalQWCA.sum(axis=1, numeric_only=True)  # cfs
    TotalQWCA['RegWCA_acft'] = TotalQWCA['RegWCA_cfs'] * 1.9835  # acft
    TotalQWCA = DF_Date_Range(TotalQWCA, D2_Yr, D2_M, D2_D, En_Yr, En_M, En_D)

    # Create Column (RegL8C51) in the File (SFWMM_Daily_Outputs)
    L8C51 = pd.DataFrame(Flow_df['date'], columns=['date'])
    L8C51['S352_Out'] = Flow_df['S352_Out'].values * (35.3147/86400)  # cmd to cfs
    L8C51['L8_O_cfs'] = Flow_df['L8_Out'].values * (35.3147/86400)  # cmd to cfs
    L8C51['L8C51_cfs'] = L8C51.sum(axis=1, numeric_only=True)  # cfs
    L8C51.to_csv(f'{output_dir}/L8C51.csv', index=False)

    # C43 RO C44 RO
    # Create Files (C43RO, C43RO_Monthly, C44RO, C44RO_Monthly)
    # As well as Columns C43Runoff and C44Runoff in File (SFWMM_Daily_Outputs)
    s79_path = glob(f'{input_dir}/S79_*FLOW*.csv')[0]
    s80_path = glob(f'{input_dir}/S80_*FLOW*.csv')[0]
    S79 = pd.read_csv(s79_path)
    S79 = S79.fillna(0)
    S80 = pd.read_csv(s80_path)
    S80 = S80.fillna(0)
    S79['Q_cmd'] = S79['S79_TOT_FLOW_cmd']  # already in cmd * 0.0283168466 * 86400
    S80['Q_cmd'] = S80['S80_S_FLOW_cmd']  # already in cmd * 0.0283168466 * 86400
    S79 = DF_Date_Range(S79, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    S80 = DF_Date_Range(S80, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    C43RO_df = pd.DataFrame(S79['date'], columns=['date'])
    C44RO_df = pd.DataFrame(S79['date'], columns=['date'])
    C43RO = np.zeros(len(C43RO_df.index))
    C44RO = np.zeros(len(C44RO_df.index))
    for i in range(len(C44RO_df.index)):
        if S79['Q_cmd'].iloc[i] - Flow_df['S77_Out'].iloc[i] + Flow_df['S77_In'].iloc[i] < 0:
            C43RO[i] = 0
        else:
            C43RO[i] = S79['Q_cmd'].iloc[i] - Flow_df['S77_Out'].iloc[i] + Flow_df['S77_In'].iloc[i]
    for i in range(len(C44RO_df.index)):
        if S80['Q_cmd'].iloc[i] - Flow_df['S308_Out'].iloc[i] + Flow_df['S308_In'].iloc[i] < 0:
            C44RO[i] = 0
        else:
            C44RO[i] = S80['Q_cmd'].iloc[i] - Flow_df['S308_Out'].iloc[i] + Flow_df['S308_In'].iloc[i]
    C43RO_df['C43RO_cmd'] = C43RO
    C44RO_df['C44RO_cmd'] = C44RO
    C43RO_df['C43RO'] = C43RO_df['C43RO_cmd']/(0.0283168466 * 86400)
    C44RO_df['C44RO'] = C44RO_df['C44RO_cmd']/(0.0283168466 * 86400)
    C43RO_df.to_csv(f'{output_dir}/C43RO.csv', index=False)
    C44RO_df.to_csv(f'{output_dir}/C44RO.csv', index=False)
    C43RO_df = C43RO_df.set_index(C43RO_df['date'])
    C44RO_df = C44RO_df.set_index(C44RO_df['date'])
    C43RO_df.index = pd.to_datetime(C43RO_df.index, unit='ns')
    C44RO_df.index = pd.to_datetime(C44RO_df.index, unit='ns')
    C43Mon = C43RO_df.resample('M').mean()
    C44Mon = C44RO_df.resample('M').mean()
    C43Mon.to_csv(f'{output_dir}/C43RO_Monthly.csv', index=False)
    C44Mon.to_csv(f'{output_dir}/C44RO_Monthly.csv', index=False)

    # SLTRIB
    # Create File (SLTRIB_Monthly)
    S48_S_path = glob(f'{input_dir}/S48_*FLOW*.csv')[0]
    S49_S_path = glob(f'{input_dir}/S49_*FLOW*.csv')[0]
    S48_S = pd.read_csv(S48_S_path)
    S49_S = pd.read_csv(S49_S_path)
    S48_S = DF_Date_Range(S48_S, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    S49_S = DF_Date_Range(S49_S, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    SLTRIB = pd.DataFrame(S48_S['date'], columns=['date'])
    SLTRIB['SLTRIB_cmd'] = S48_S['S48_S_FLOW_cmd'] + S49_S['S49_S_FLOW_cmd']
    SLTRIB['SLTRIB_cfs'] = SLTRIB['SLTRIB_cmd']/(0.0283168466 * 86400)
    SLTRIB = SLTRIB.set_index(SLTRIB['date'])
    SLTRIB.index = pd.to_datetime(SLTRIB.index, unit='ns')
    SLTRIBMon = SLTRIB.resample('M').mean()
    SLTRIB.drop(['date'], axis=1, inplace=True)
    SLTRIB = SLTRIB.reset_index()
    SLTRIB.to_csv(f'{output_dir}/SLTRIB.csv', index=False)
    SLTRIBMon.to_csv(f'{output_dir}/SLTRIB_Monthly.csv')
    Basin_RO = pd.DataFrame(SLTRIBMon.index, columns=['date'])
    Basin_RO['SLTRIB'] = SLTRIBMon['SLTRIB_cfs'].values * 1.9835  # cfs to acft
    Basin_RO['C44RO'] = C44Mon['C44RO'].values * 86400
    Basin_RO['C43RO'] = C43Mon['C43RO'].values * 86400
    Basin_RO.to_csv(f'{output_dir}/Basin_RO_inputs.csv', index=False)

    # EAA MIA RUNOFF
    # Create File (EAA_MIA_RUNOFF_Inputs)
    s3_path = glob(f'{input_dir}/S3_FLOW*.csv')[0]
    s2_path = glob(f'{input_dir}/S2_NNR*FLOW*.csv')[0]
    S3_Miami_data = pd.read_csv(s3_path)
    S3_Miami_data = DF_Date_Range(S3_Miami_data, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    S3_Miami = S3_Miami_data['S3_FLOW_cmd']
    S2_NNR_data = pd.read_csv(s2_path)
    S2_NNR_data = DF_Date_Range(S2_NNR_data, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    S2_NNR = S2_NNR_data['S2 NNR_FLOW_cmd']
    EAA_MIA_RO = pd.DataFrame(date, columns=['date'])
    EAA_MIA_RO['MIA'] = S3_Miami.values/(0.0283168466 * 86400)
    EAA_MIA_RO['NNR'] = S2_NNR.values/(0.0283168466 * 86400)
    EAA_MIA_RO['WPB'] = Flow_df['S352_Out']/(0.0283168466 * 86400)
    EAA_MIA_RO['S2PMP'] = Flow_df['S2_P_Q']/(0.0283168466 * 86400)
    EAA_MIA_RO['S3PMP'] = Flow_df['S3_P_Q']/(0.0283168466 * 86400)
    EAA_MIA_RO.to_csv(f'{output_dir}/EAA_MIA_RUNOFF_Inputs.csv', index=False)

    # Weekly Tributary Conditions
    # Create File (Trib_cond_wkly_data)
    # Net RF Inch
    RF_data = pd.read_csv(f'{input_dir}/LAKE_RAINFALL_DATA.csv')
    RF_data = DF_Date_Range(RF_data, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    ET_data = pd.read_csv(f'{input_dir}/LOONE_AVERAGE_ETPI_DATA.csv')
    ET_data = DF_Date_Range(ET_data, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    Net_RF = pd.DataFrame(RF_data['date'], columns=['date'])
    Net_RF = DF_Date_Range(Net_RF, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    Net_RF['NetRF_In'] = RF_data['average_rainfall'] - ET_data['average_ETPI']
    Net_RF = Net_RF.set_index(['date'])
    Net_RF.index = pd.to_datetime(Net_RF.index, unit='ns')
    Net_RF_Weekly = Net_RF.resample('W-FRI').sum()
    # Net Inflows cfs
    Net_Inflows = pd.DataFrame(Flow_df['date'], columns=['date'])
    Net_Inflows = DF_Date_Range(Net_Inflows, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    Net_Inflows['Net_Inflows'] = Flow_df['Netflows']/(0.0283168466 * 86400)  # cmd to cfs
    Net_Inflows = Net_Inflows.set_index(['date'])
    Net_Inflows.index = pd.to_datetime(Net_Inflows.index, unit='ns')
    Net_Inflow_Weekly = Net_Inflows.resample('W-FRI').mean()
    # S65 cfs
    S65E = pd.DataFrame(Flow_df['date'], columns=['date'])
    S65E = DF_Date_Range(S65E, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    S65E['S65E'] = Flow_df['S65_Q']/(0.0283168466 * 86400)  # cmd to cfs
    S65E = S65E.set_index(['date'])
    S65E.index = pd.to_datetime(S65E.index, unit='ns')
    S65E_Weekly = S65E.resample('W-FRI').mean()
    # PI
    # TODO
    # This is prepared manually
    # Weekly data is downloaded from https://www.ncei.noaa.gov/access/monitoring/weekly-palmers/time-series/0804
    # State:Florida Division:4.South Central
    PI = pd.DataFrame(S65E_Weekly.index, columns=['date'])
    PI_data = pd.read_csv(f'{input_dir}/PI.csv')
    PI['PI'] = PI_data.iloc[:, 1]

    Trib_Cond_Wkly = pd.DataFrame(S65E_Weekly.index, columns=['date'])
    Trib_Cond_Wkly['NetRF'] = Net_RF_Weekly['NetRF_In'].values
    Trib_Cond_Wkly['NetInf'] = Net_Inflow_Weekly['Net_Inflows'].values
    Trib_Cond_Wkly['S65E'] = S65E_Weekly['S65E'].values
    Trib_Cond_Wkly['Palmer'] = PI['PI'].values
    Trib_Cond_Wkly.to_csv(f'{output_dir}/Trib_cond_wkly_data.csv', index=False)

    # Wind Speed
    # Create File (LOWS)
    L001WS = pd.read_csv(f'{input_dir}/L001_WNDS_MPH.csv')
    L005WS = pd.read_csv(f'{input_dir}/L005_WNDS_MPH.csv')
    L006WS = pd.read_csv(f'{input_dir}/L006_WNDS_MPH.csv')
    LZ40WS = pd.read_csv(f'{input_dir}/LZ40_WNDS_MPH.csv')
    L001WS = DF_Date_Range(L001WS, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    L005WS = DF_Date_Range(L005WS, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    L006WS = DF_Date_Range(L006WS, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    LZ40WS = DF_Date_Range(LZ40WS, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    LOWS = pd.DataFrame(L001WS['date'], columns=['date'])
    LOWS['L001WS'] = L001WS['L001_WNDS_MPH']
    LOWS['L005WS'] = L005WS['L005_WNDS_MPH']
    LOWS['L006WS'] = L006WS['L006_WNDS_MPH']
    LOWS['LZ40WS'] = LZ40WS['LZ40_WNDS_MPH']
    LOWS['LO_Avg_WS_MPH'] = LOWS.mean(axis=1, numeric_only=True)
    LOWS.to_csv(f'{output_dir}/LOWS.csv', index=False)

    # RFVol acft
    # Create File (RF_Volume)
    # Merge the DataFrames on date to ensure matching rows
    RF_data_copy = RF_data.copy()
    LO_Stg_Sto_SA_df_copy = LO_Stg_Sto_SA_df.copy()
    RF_data_copy['date'] = pd.to_datetime(RF_data_copy['date'])
    LO_Stg_Sto_SA_df_copy['date'] = pd.to_datetime(LO_Stg_Sto_SA_df_copy['date'])
    merged_rf_sa = pd.merge(RF_data_copy[['date', 'average_rainfall']], 
                            LO_Stg_Sto_SA_df_copy[['date', 'SA_acres']], 
                            on='date', how='inner')
    
    RFVol = pd.DataFrame(merged_rf_sa['date'], columns=['date'])
    RFVol['RFVol_acft'] = (merged_rf_sa['average_rainfall'].values/12) * merged_rf_sa['SA_acres'].values
    date_reference = RFVol['date'].iloc[0]
    date_inserts = [date_reference - datetime.timedelta(days=2), date_reference - datetime.timedelta(days=1)]
    df_insert = pd.DataFrame(data={'date': date_inserts, 'RFVol_acft': [0.0, 0.0]})
    RFVol = pd.concat([df_insert, RFVol])
    RFVol.to_csv(f'{output_dir}/RFVol.csv', index=False)

    # ETVol acft
    # Create File (ETVol)
    # Merge the DataFrames on date to ensure matching rows
    ET_data_copy = ET_data.copy()
    LO_Stg_Sto_SA_df_copy = LO_Stg_Sto_SA_df.copy()
    ET_data_copy['date'] = pd.to_datetime(ET_data_copy['date'])
    LO_Stg_Sto_SA_df_copy['date'] = pd.to_datetime(LO_Stg_Sto_SA_df_copy['date'])
    merged_et_sa = pd.merge(ET_data_copy[['date', 'average_ETPI']],
                            LO_Stg_Sto_SA_df_copy[['date', 'SA_acres']], 
                            on='date', how='inner')

    ETVol = pd.DataFrame(merged_et_sa['date'], columns=['date'])
    ETVol['ETVol_acft'] = (merged_et_sa['average_ETPI'].values/12) * merged_et_sa['SA_acres'].values
    date_reference = ETVol['date'].iloc[0]
    date_inserts = [date_reference - datetime.timedelta(days=2), date_reference - datetime.timedelta(days=1)]
    df_insert = pd.DataFrame(data={'date': date_inserts, 'ETVol_acft': [0.0, 0.0]})
    ETVol = pd.concat([df_insert, ETVol])
    ETVol.to_csv(f'{output_dir}/ETVol.csv', index=False)

    # WCA Stages
    # Create File (WCA_Stages_Inputs)
    Stg_3ANW = pd.read_csv(f'{input_dir}/Stg_3ANW.csv')
    Stg_3ANW = DF_Date_Range(Stg_3ANW, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    Stg_2A17 = pd.read_csv(f'{input_dir}/Stg_2A17.csv')
    Stg_2A17 = DF_Date_Range(Stg_2A17, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    Stg_3A3 = pd.read_csv(f'{input_dir}/Stg_3A3.csv')
    Stg_3A3 = DF_Date_Range(Stg_3A3, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    Stg_3A4 = pd.read_csv(f'{input_dir}/Stg_3A4.csv')
    Stg_3A4 = DF_Date_Range(Stg_3A4, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    Stg_3A28 = pd.read_csv(f'{input_dir}/Stg_3A28.csv')
    Stg_3A28 = DF_Date_Range(Stg_3A28, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    WCA_Stg = pd.DataFrame(Stg_3A28['date'], columns=['date'])
    WCA_Stg['3A-NW'] = Stg_3ANW.iloc[:, -1].values
    WCA_Stg['2A-17'] = Stg_2A17.iloc[:, -1].values
    WCA_Stg['3A-3'] = Stg_3A3.iloc[:, -1].values
    WCA_Stg['3A-4'] = Stg_3A4.iloc[:, -1].values
    WCA_Stg['3A-28'] = Stg_3A28.iloc[:, -1].values
    WCA_Stg.to_csv(f'{output_dir}/WCA_Stages_Inputs.csv', index=False)

    # Predict Water Temp Function of Air Temp
    L001_H2OT = pd.read_csv(f'{input_dir}/L001_H2OT_Degrees Celsius.csv')
    L001_H2OT = DF_Date_Range(L001_H2OT, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    L005_H2OT = pd.read_csv(f'{input_dir}/L005_H2OT_Degrees Celsius.csv')
    L005_H2OT = DF_Date_Range(L005_H2OT, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    L006_H2OT = pd.read_csv(f'{input_dir}/L006_H2OT_Degrees Celsius.csv')
    L006_H2OT = DF_Date_Range(L006_H2OT, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    LZ40_H2OT = pd.read_csv(f'{input_dir}/LZ40_H2OT_Degrees Celsius.csv')
    LZ40_H2OT = DF_Date_Range(LZ40_H2OT, St_Yr, St_M, St_D, En_Yr, En_M, En_D)

    Water_Temp_data = pd.DataFrame(L001_H2OT['date'], columns=['date'])

    Water_Temp_data['L001_WaterT'] = L001_H2OT['L001_H2OT_Degrees Celsius']
    Water_Temp_data['L005_WaterT'] = L005_H2OT['L005_H2OT_Degrees Celsius']
    Water_Temp_data['L006_WaterT'] = L006_H2OT['L006_H2OT_Degrees Celsius']
    Water_Temp_data['LZ40_WaterT'] = LZ40_H2OT['LZ40_H2OT_Degrees Celsius']

    Water_Temp_data = DF_Date_Range(Water_Temp_data, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    water_temp_filter_cols = ['L001_WaterT', 'L005_WaterT', 'L006_WaterT', 'LZ40_WaterT']
    Water_Temp_data['WaterT_Mean'] = Water_Temp_data[water_temp_filter_cols].mean(axis=1)

    L001_AirT = pd.read_csv(f'{input_dir}/L001_AIRT_Degrees Celsius.csv')
    L001_AirT = DF_Date_Range(L001_AirT, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    L005_AirT = pd.read_csv(f'{input_dir}/L005_AIRT_Degrees Celsius.csv')
    L005_AirT = DF_Date_Range(L005_AirT, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    L006_AirT = pd.read_csv(f'{input_dir}/L006_AIRT_Degrees Celsius.csv')
    L006_AirT = DF_Date_Range(L006_AirT, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    LZ40_AirT = pd.read_csv(f'{input_dir}/LZ40_AIRT_Degrees Celsius.csv')
    LZ40_AirT = DF_Date_Range(LZ40_AirT, St_Yr, St_M, St_D, En_Yr, En_M, En_D)

    WaterT_pred_df = pd.DataFrame(L001_AirT['date'], columns=['date'])

    WaterT_pred_df['L001_WaterT_pred'] = 1.862667 + 0.936899 * L001_AirT['L001_AIRT_Degrees Celsius'].values
    WaterT_pred_df['L005_WaterT_pred'] = 1.330211 + 0.909713 * L005_AirT['L005_AIRT_Degrees Celsius'].values
    WaterT_pred_df['L006_WaterT_pred'] = -0.88564 + 1.01585 * L006_AirT['L006_AIRT_Degrees Celsius'].values
    WaterT_pred_df['LZ40_WaterT_pred'] = 0.388231 + 0.980154 * LZ40_AirT['LZ40_AIRT_Degrees Celsius'].values
    water_t_pred_filter_cols = ['L001_WaterT_pred', 'L005_WaterT_pred', 'L006_WaterT_pred', 'LZ40_WaterT_pred']
    WaterT_pred_df['WaterT_pred_Mean'] = WaterT_pred_df[water_t_pred_filter_cols].mean(axis=1)
    WaterT_pred_df_1 = DF_Date_Range(WaterT_pred_df, St_Yr, St_M, St_D, 2020, 8, 25)
    WaterT_pred_df_2 = DF_Date_Range(WaterT_pred_df, 2020, 8, 26, En_Yr, En_M, En_D)
    Filled_WaterT_1 = np.zeros(len(WaterT_pred_df_1.index))
    Filled_WaterT_2 = np.zeros(len(WaterT_pred_df_2.index))
    for i in range(len(Water_Temp_data.index)):
        if np.isnan(Water_Temp_data['WaterT_Mean'].iloc[i]):
            Filled_WaterT_1[i] = WaterT_pred_df_1['WaterT_pred_Mean'].iloc[i]
        else:
            Filled_WaterT_1[i] = Water_Temp_data['WaterT_Mean'].iloc[i]

    Filled_WaterT_2 = WaterT_pred_df_2['WaterT_pred_Mean']
    Filled_WaterT_1df = pd.DataFrame(WaterT_pred_df_1['date'], columns=['date'])
    Filled_WaterT_2df = pd.DataFrame(WaterT_pred_df_2['date'], columns=['date'])
    Filled_WaterT_1df['Water_T'] = Filled_WaterT_1
    Filled_WaterT_2df['Water_T'] = Filled_WaterT_2
    Filled_WaterT = pd.concat([Filled_WaterT_1df, Filled_WaterT_2df]).reset_index(drop=True)
    Filled_WaterT.to_csv(f'{output_dir}/Filled_WaterT.csv', index=False)

    # TP Observations in Lake
    L001_TP = pd.read_csv(f'{input_dir}/water_quality_L001_PHOSPHATE, TOTAL AS P.csv')
    L004_TP = pd.read_csv(f'{input_dir}/water_quality_L004_PHOSPHATE, TOTAL AS P.csv')
    L005_TP = pd.read_csv(f'{input_dir}/water_quality_L005_PHOSPHATE, TOTAL AS P.csv')
    L006_TP = pd.read_csv(f'{input_dir}/water_quality_L006_PHOSPHATE, TOTAL AS P.csv')
    L007_TP = pd.read_csv(f'{input_dir}/water_quality_L007_PHOSPHATE, TOTAL AS P.csv')
    L008_TP = pd.read_csv(f'{input_dir}/water_quality_L008_PHOSPHATE, TOTAL AS P.csv')
    LZ40_TP = pd.read_csv(f'{input_dir}/water_quality_LZ40_PHOSPHATE, TOTAL AS P.csv')

    L001_TP.columns = L001_TP.columns.str.replace('days', 'days_L001_TP')
    L004_TP.columns = L004_TP.columns.str.replace('days', 'days_L004_TP')
    L005_TP.columns = L005_TP.columns.str.replace('days', 'days_L005_TP')
    L006_TP.columns = L006_TP.columns.str.replace('days', 'days_L006_TP')
    L007_TP.columns = L007_TP.columns.str.replace('days', 'days_L007_TP')
    L008_TP.columns = L008_TP.columns.str.replace('days', 'days_L008_TP')
    LZ40_TP.columns = LZ40_TP.columns.str.replace('days', 'days_LZ40_TP')

    L001_TP.columns = L001_TP.columns.str.replace('Unnamed: 0', 'Unnamed: 0_L001_TP')
    L004_TP.columns = L004_TP.columns.str.replace('Unnamed: 0', 'Unnamed: 0_L004_TP')
    L005_TP.columns = L005_TP.columns.str.replace('Unnamed: 0', 'Unnamed: 0_L005_TP')
    L006_TP.columns = L006_TP.columns.str.replace('Unnamed: 0', 'Unnamed: 0_L006_TP')
    L007_TP.columns = L007_TP.columns.str.replace('Unnamed: 0', 'Unnamed: 0_L007_TP')
    L008_TP.columns = L008_TP.columns.str.replace('Unnamed: 0', 'Unnamed: 0_L008_TP')
    LZ40_TP.columns = LZ40_TP.columns.str.replace('Unnamed: 0', 'Unnamed: 0_LZ40_TP')

    LO_TP_data = pd.merge(L001_TP, L004_TP, how='left', on='date')
    LO_TP_data = pd.merge(LO_TP_data, L005_TP, how='left', on='date')
    LO_TP_data = pd.merge(LO_TP_data, L006_TP, how='left', on='date')
    LO_TP_data = pd.merge(LO_TP_data, L007_TP, how='left', on='date')
    LO_TP_data = pd.merge(LO_TP_data, L008_TP, how='left', on='date')
    LO_TP_data = pd.merge(LO_TP_data, LZ40_TP, how='left', on='date')
    LO_TP_data = LO_TP_data.loc[:, ~LO_TP_data.columns.str.startswith('Unnamed')]
    LO_TP_data['Mean_TP'] = LO_TP_data.mean(axis=1, numeric_only=True)
    LO_TP_data = LO_TP_data.set_index(['date'])
    LO_TP_data.index = pd.to_datetime(LO_TP_data.index, unit='ns')
    LO_TP_Monthly = LO_TP_data.resample('M').mean()
    LO_TP_Monthly.to_csv(f'{output_dir}/LO_TP_Monthly.csv')

    # Interpolated TP Observations in Lake
    L001_TP_Inter = pd.read_csv(f'{input_dir}/water_quality_L001_PHOSPHATE, TOTAL AS P_Interpolated.csv')
    L004_TP_Inter = pd.read_csv(f'{input_dir}/water_quality_L004_PHOSPHATE, TOTAL AS P_Interpolated.csv')
    L005_TP_Inter = pd.read_csv(f'{input_dir}/water_quality_L005_PHOSPHATE, TOTAL AS P_Interpolated.csv')
    L006_TP_Inter = pd.read_csv(f'{input_dir}/water_quality_L006_PHOSPHATE, TOTAL AS P_Interpolated.csv')
    L007_TP_Inter = pd.read_csv(f'{input_dir}/water_quality_L007_PHOSPHATE, TOTAL AS P_Interpolated.csv')
    L008_TP_Inter = pd.read_csv(f'{input_dir}/water_quality_L008_PHOSPHATE, TOTAL AS P_Interpolated.csv')
    LZ40_TP_Inter = pd.read_csv(f'{input_dir}/water_quality_LZ40_PHOSPHATE, TOTAL AS P_Interpolated.csv')

    L001_TP_Inter.columns = L001_TP_Inter.columns.str.replace('Data', 'Data_L001_TP_Inter')
    L004_TP_Inter.columns = L004_TP_Inter.columns.str.replace('Data', 'Data_L004_TP_Inter')
    L005_TP_Inter.columns = L005_TP_Inter.columns.str.replace('Data', 'Data_L005_TP_Inter')
    L006_TP_Inter.columns = L006_TP_Inter.columns.str.replace('Data', 'Data_L006_TP_Inter')
    L007_TP_Inter.columns = L007_TP_Inter.columns.str.replace('Data', 'Data_L007_TP_Inter')
    L008_TP_Inter.columns = L008_TP_Inter.columns.str.replace('Data', 'Data_L008_TP_Inter')
    LZ40_TP_Inter.columns = LZ40_TP_Inter.columns.str.replace('Data', 'Data_LZ40_TP_Inter')

    LO_TP_data_Inter = pd.merge(L001_TP_Inter, L004_TP_Inter, how='left', on='date')
    LO_TP_data_Inter = pd.merge(LO_TP_data_Inter, L005_TP_Inter, how='left', on='date')
    LO_TP_data_Inter = pd.merge(LO_TP_data_Inter, L006_TP_Inter, how='left', on='date')
    LO_TP_data_Inter = pd.merge(LO_TP_data_Inter, L007_TP_Inter, how='left', on='date')
    LO_TP_data_Inter = pd.merge(LO_TP_data_Inter, L008_TP_Inter, how='left', on='date')
    LO_TP_data_Inter = pd.merge(LO_TP_data_Inter, LZ40_TP_Inter, how='left', on='date')
    LO_TP_data_Inter = LO_TP_data_Inter.loc[:, ~LO_TP_data_Inter.columns.str.startswith('Unnamed')]
    LO_TP_data_Inter['Mean_TP'] = LO_TP_data_Inter.mean(axis=1, numeric_only=True)
    LO_TP_data_Inter = LO_TP_data_Inter.set_index(['date'])
    LO_TP_data_Inter.index = pd.to_datetime(LO_TP_data_Inter.index, unit='ns')
    LO_TP_Monthly_Inter = LO_TP_data_Inter.resample('ME').mean()
    Max = LO_TP_Monthly_Inter.max(axis=1)
    Min = LO_TP_Monthly_Inter.min(axis=1)
    LO_TP_Monthly_Inter['Max'] = Max.values
    LO_TP_Monthly_Inter['Min'] = Min.values
    LO_TP_Monthly_Inter.to_csv(f'{output_dir}/LO_TP_Monthly_inter.csv')

    # Interpolated OP Observations in Lake
    # Create File (LO_Avg_OP)
    L001_OP_Inter = pd.read_csv(f'{input_dir}/water_quality_L001_PHOSPHATE, ORTHO AS P_Interpolated.csv')
    L004_OP_Inter = pd.read_csv(f'{input_dir}/water_quality_L004_PHOSPHATE, ORTHO AS P_Interpolated.csv')
    L005_OP_Inter = pd.read_csv(f'{input_dir}/water_quality_L005_PHOSPHATE, ORTHO AS P_Interpolated.csv')
    L006_OP_Inter = pd.read_csv(f'{input_dir}/water_quality_L006_PHOSPHATE, ORTHO AS P_Interpolated.csv')
    L007_OP_Inter = pd.read_csv(f'{input_dir}/water_quality_L007_PHOSPHATE, ORTHO AS P_Interpolated.csv')
    L008_OP_Inter = pd.read_csv(f'{input_dir}/water_quality_L008_PHOSPHATE, ORTHO AS P_Interpolated.csv')
    LZ40_OP_Inter = pd.read_csv(f'{input_dir}/water_quality_LZ40_PHOSPHATE, ORTHO AS P_Interpolated.csv')

    L001_OP_Inter.columns = L001_OP_Inter.columns.str.replace('Data', 'Data_L001_OP_Inter')
    L004_OP_Inter.columns = L004_OP_Inter.columns.str.replace('Data', 'Data_L004_OP_Inter')
    L005_OP_Inter.columns = L005_OP_Inter.columns.str.replace('Data', 'Data_L005_OP_Inter')
    L006_OP_Inter.columns = L006_OP_Inter.columns.str.replace('Data', 'Data_L006_OP_Inter')
    L007_OP_Inter.columns = L007_OP_Inter.columns.str.replace('Data', 'Data_L007_OP_Inter')
    L008_OP_Inter.columns = L008_OP_Inter.columns.str.replace('Data', 'Data_L008_OP_Inter')
    LZ40_OP_Inter.columns = LZ40_OP_Inter.columns.str.replace('Data', 'Data_LZ40_OP_Inter')

    LO_OP_data_Inter = pd.merge(L001_OP_Inter, L004_OP_Inter, how='left', on='date')
    LO_OP_data_Inter = pd.merge(LO_OP_data_Inter, L005_OP_Inter, how='left', on='date')
    LO_OP_data_Inter = pd.merge(LO_OP_data_Inter, L006_OP_Inter, how='left', on='date')
    LO_OP_data_Inter = pd.merge(LO_OP_data_Inter, L007_OP_Inter, how='left', on='date')
    LO_OP_data_Inter = pd.merge(LO_OP_data_Inter, L008_OP_Inter, how='left', on='date')
    LO_OP_data_Inter = pd.merge(LO_OP_data_Inter, LZ40_OP_Inter, how='left', on='date')
    LO_OP_data_Inter = LO_OP_data_Inter.loc[:, ~LO_OP_data_Inter.columns.str.startswith('Unnamed')]
    LO_OP_data_Inter['Mean_OP'] = LO_OP_data_Inter.mean(axis=1, numeric_only=True)
    LO_OP_data_Inter = DF_Date_Range(LO_OP_data_Inter, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    LO_OP_data_Inter.to_csv(f'{output_dir}/LO_OP.csv', index=False)
    
    # Create File (N_OP) (L001, L005, L008)
    n_op = LO_OP_data_Inter[['date', 'Data_L001_OP_Inter', 'Data_L005_OP_Inter', 'Data_L008_OP_Inter']]
    n_op['OP'] = n_op.mean(axis=1, numeric_only=True) * 1000 # mg/L to mg/m3
    n_op.drop(['Data_L001_OP_Inter', 'Data_L005_OP_Inter', 'Data_L008_OP_Inter'], axis=1, inplace=True)
    n_op.to_csv(f'{output_dir}/N_OP.csv', index=False)
    
    # Create File (S_OP) (L004, L006, L007, L008, and LZ40)
    s_op = LO_OP_data_Inter[['date', 'Data_L004_OP_Inter', 'Data_L006_OP_Inter', 'Data_L007_OP_Inter', 'Data_L008_OP_Inter', 'Data_LZ40_OP_Inter']]
    s_op['OP'] = s_op.mean(axis=1, numeric_only=True) * 1000 # mg/L to mg/m3
    s_op.drop(['Data_L004_OP_Inter', 'Data_L006_OP_Inter', 'Data_L007_OP_Inter', 'Data_L008_OP_Inter', 'Data_LZ40_OP_Inter'], axis=1, inplace=True)
    s_op.to_csv(f'{output_dir}/S_OP.csv', index=False)

    # Interpolated NH4 Observations in Lake
    # Create File (LO_Avg_NH4)
    L001_NH4_Inter = pd.read_csv(f'{input_dir}/water_quality_L001_AMMONIA-N_Interpolated.csv')
    L004_NH4_Inter = pd.read_csv(f'{input_dir}/water_quality_L004_AMMONIA-N_Interpolated.csv')
    L005_NH4_Inter = pd.read_csv(f'{input_dir}/water_quality_L005_AMMONIA-N_Interpolated.csv')
    L006_NH4_Inter = pd.read_csv(f'{input_dir}/water_quality_L006_AMMONIA-N_Interpolated.csv')
    L007_NH4_Inter = pd.read_csv(f'{input_dir}/water_quality_L007_AMMONIA-N_Interpolated.csv')
    L008_NH4_Inter = pd.read_csv(f'{input_dir}/water_quality_L008_AMMONIA-N_Interpolated.csv')
    LZ40_NH4_Inter = pd.read_csv(f'{input_dir}/water_quality_LZ40_AMMONIA-N_Interpolated.csv')

    L001_NH4_Inter.columns = L001_NH4_Inter.columns.str.replace('Data', 'Data_L001_NH4_Inter')
    L004_NH4_Inter.columns = L004_NH4_Inter.columns.str.replace('Data', 'Data_L004_NH4_Inter')
    L005_NH4_Inter.columns = L005_NH4_Inter.columns.str.replace('Data', 'Data_L005_NH4_Inter')
    L006_NH4_Inter.columns = L006_NH4_Inter.columns.str.replace('Data', 'Data_L006_NH4_Inter')
    L007_NH4_Inter.columns = L007_NH4_Inter.columns.str.replace('Data', 'Data_L007_NH4_Inter')
    L008_NH4_Inter.columns = L008_NH4_Inter.columns.str.replace('Data', 'Data_L008_NH4_Inter')
    LZ40_NH4_Inter.columns = LZ40_NH4_Inter.columns.str.replace('Data', 'Data_LZ40_NH4_Inter')

    LO_NH4_data_Inter = pd.merge(L001_NH4_Inter, L004_NH4_Inter, how='left', on='date')
    LO_NH4_data_Inter = pd.merge(LO_NH4_data_Inter, L005_NH4_Inter, how='left', on='date')
    LO_NH4_data_Inter = pd.merge(LO_NH4_data_Inter, L006_NH4_Inter, how='left', on='date')
    LO_NH4_data_Inter = pd.merge(LO_NH4_data_Inter, L007_NH4_Inter, how='left', on='date')
    LO_NH4_data_Inter = pd.merge(LO_NH4_data_Inter, L008_NH4_Inter, how='left', on='date')
    LO_NH4_data_Inter = pd.merge(LO_NH4_data_Inter, LZ40_NH4_Inter, how='left', on='date')
    LO_NH4_data_Inter.to_csv(f'{output_dir}/LO_NH4_Inter.csv', index=False)
    # Read clean LO_NH4 data
    LO_NH4_Clean_Inter = pd.read_csv(f'{output_dir}/LO_NH4_Inter.csv')
    LO_NH4_Clean_Inter['Mean_NH4'] = LO_NH4_Clean_Inter.mean(axis=1, numeric_only=True)
    LO_NH4_Clean_Inter.to_csv(f'{output_dir}/LO_NH4_Clean_daily.csv', index=False)
    LO_NH4_Clean_Inter = LO_NH4_Clean_Inter.set_index(['date'])
    LO_NH4_Clean_Inter.index = pd.to_datetime(LO_NH4_Clean_Inter.index, unit='ns')
    LO_NH4_Monthly_Inter = LO_NH4_Clean_Inter.resample('ME').mean()
    LO_NH4_Monthly_Inter.to_csv(f'{output_dir}/LO_NH4_Monthly_Inter.csv')

    # Interpolated NO Observations in Lake
    # Create File (LO_Avg_NO) and (LO_NO_Obs)
    L001_NO_Inter = pd.read_csv(f'{input_dir}/water_quality_L001_NITRATE+NITRITE-N_Interpolated.csv')
    L004_NO_Inter = pd.read_csv(f'{input_dir}/water_quality_L004_NITRATE+NITRITE-N_Interpolated.csv')
    L005_NO_Inter = pd.read_csv(f'{input_dir}/water_quality_L005_NITRATE+NITRITE-N_Interpolated.csv')
    L006_NO_Inter = pd.read_csv(f'{input_dir}/water_quality_L006_NITRATE+NITRITE-N_Interpolated.csv')
    L007_NO_Inter = pd.read_csv(f'{input_dir}/water_quality_L007_NITRATE+NITRITE-N_Interpolated.csv')
    L008_NO_Inter = pd.read_csv(f'{input_dir}/water_quality_L008_NITRATE+NITRITE-N_Interpolated.csv')
    LZ40_NO_Inter = pd.read_csv(f'{input_dir}/water_quality_LZ40_NITRATE+NITRITE-N_Interpolated.csv')

    L001_NO_Inter.columns = L001_NO_Inter.columns.str.replace('Data', 'Data_L001_NO_Inter')
    L004_NO_Inter.columns = L004_NO_Inter.columns.str.replace('Data', 'Data_L004_NO_Inter')
    L005_NO_Inter.columns = L005_NO_Inter.columns.str.replace('Data', 'Data_L005_NO_Inter')
    L006_NO_Inter.columns = L006_NO_Inter.columns.str.replace('Data', 'Data_L006_NO_Inter')
    L007_NO_Inter.columns = L007_NO_Inter.columns.str.replace('Data', 'Data_L007_NO_Inter')
    L008_NO_Inter.columns = L008_NO_Inter.columns.str.replace('Data', 'Data_L008_NO_Inter')
    LZ40_NO_Inter.columns = LZ40_NO_Inter.columns.str.replace('Data', 'Data_LZ40_NO_Inter')

    LO_NO_data_Inter = pd.merge(L001_NO_Inter, L004_NO_Inter, how='left', on='date')
    LO_NO_data_Inter = pd.merge(LO_NO_data_Inter, L005_NO_Inter, how='left', on='date')
    LO_NO_data_Inter = pd.merge(LO_NO_data_Inter, L006_NO_Inter, how='left', on='date')
    LO_NO_data_Inter = pd.merge(LO_NO_data_Inter, L007_NO_Inter, how='left', on='date')
    LO_NO_data_Inter = pd.merge(LO_NO_data_Inter, L008_NO_Inter, how='left', on='date')
    LO_NO_data_Inter = pd.merge(LO_NO_data_Inter, LZ40_NO_Inter, how='left', on='date')
    LO_NO_data_Inter = LO_NO_data_Inter.loc[:, ~LO_NO_data_Inter.columns.str.startswith('Unnamed')]
    LO_NO_data_Inter['Mean_NO'] = LO_NO_data_Inter.mean(axis=1, numeric_only=True)
    # LO_NO_data_Inter.to_csv(f'{output_dir}/LO_NO_Clean_daily.csv')
    LO_NO_data_Inter = LO_NO_data_Inter.set_index(['date'])
    LO_NO_data_Inter.index = pd.to_datetime(LO_NO_data_Inter.index, unit='ns')
    LO_NO_Monthly_Inter = LO_NO_data_Inter.resample('M').mean()
    NO_Max = LO_NO_Monthly_Inter.max(axis=1)
    NO_Min = LO_NO_Monthly_Inter.min(axis=1)
    LO_NO_Monthly_Inter['Max'] = NO_Max.values
    LO_NO_Monthly_Inter['Min'] = NO_Min.values
    LO_NO_Monthly_Inter.to_csv(f'{output_dir}/LO_NO_Monthly_Inter.csv')

    # Create File (LO_DIN)
    date_DIN = pd.date_range(start='%s/%s/%s' % (St_M, St_D, St_Yr), end='%s/%s/%s' % (En_M, En_D, En_Yr), freq='D')
    LO_DIN = pd.DataFrame(date_DIN, columns=['date'])
    LO_NH4_Clean_Inter['date'] = LO_NH4_Clean_Inter.index
    LO_NH4_Clean_Inter = DF_Date_Range(LO_NH4_Clean_Inter, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    LO_NO_data_Inter['date'] = LO_NO_data_Inter.index
    LO_NO_Clean_Inter = DF_Date_Range(LO_NO_data_Inter, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    LO_DIN['NH4'] = LO_NH4_Clean_Inter['Mean_NH4'].values
    LO_DIN['NO'] = LO_NO_Clean_Inter['Mean_NO'].values
    LO_DIN['DIN_mg/m3'] = LO_DIN[['NH4', 'NO']].sum(axis=1)*1000
    LO_DIN.to_csv(f'{output_dir}/LO_DIN.csv', index=False)
    
    # Create File (N_DIN) (L001, L005, L008)
    n_din = pd.DataFrame(date_DIN, columns=['date'])
    n_din.set_index('date', inplace=True)
    n_din['NH4'] = LO_NH4_Clean_Inter[['date', 'Data_L001_NH4_Inter', 'Data_L005_NH4_Inter', 'Data_L008_NH4_Inter']].mean(axis=1, numeric_only=True)
    n_din['NO'] = LO_NO_Clean_Inter[['date', 'Data_L001_NO_Inter', 'Data_L005_NO_Inter', 'Data_L008_NO_Inter']].mean(axis=1, numeric_only=True)*1000    # mg/L to mg/m3
    n_din['DIN'] = n_din[['NH4', 'NO']].sum(axis=1)*1000    # mg/L to mg/m3
    n_din.to_csv(f'{output_dir}/N_DIN.csv')
    
    # Create File (S_DIN) (L004, L006, L007, L008, LZ40)
    s_din = pd.DataFrame(date_DIN, columns=['date'])
    s_din.set_index('date', inplace=True)
    s_din['NH4'] = LO_NH4_Clean_Inter[['date', 'Data_L004_NH4_Inter', 'Data_L006_NH4_Inter', 'Data_L007_NH4_Inter', 'Data_L008_NH4_Inter', 'Data_LZ40_NH4_Inter']].mean(axis=1, numeric_only=True)
    s_din['NO'] = LO_NO_Clean_Inter[['date', 'Data_L004_NO_Inter', 'Data_L006_NO_Inter', 'Data_L007_NO_Inter', 'Data_L008_NO_Inter', 'Data_LZ40_NO_Inter']].mean(axis=1, numeric_only=True)*1000    # mg/L to mg/m3
    s_din['DIN'] = s_din[['NH4', 'NO']].sum(axis=1)*1000    # mg/L to mg/m3
    s_din.to_csv(f'{output_dir}/S_DIN.csv')

    # Interpolated DO Observations in Lake
    # Create File (LO_Avg_DO)
    L001_DO_Inter = pd.read_csv(f'{input_dir}/water_quality_L001_DISSOLVED OXYGEN_Interpolated.csv')
    L004_DO_Inter = pd.read_csv(f'{input_dir}/water_quality_L004_DISSOLVED OXYGEN_Interpolated.csv')
    L005_DO_Inter = pd.read_csv(f'{input_dir}/water_quality_L005_DISSOLVED OXYGEN_Interpolated.csv')
    L006_DO_Inter = pd.read_csv(f'{input_dir}/water_quality_L006_DISSOLVED OXYGEN_Interpolated.csv')
    L007_DO_Inter = pd.read_csv(f'{input_dir}/water_quality_L007_DISSOLVED OXYGEN_Interpolated.csv')
    L008_DO_Inter = pd.read_csv(f'{input_dir}/water_quality_L008_DISSOLVED OXYGEN_Interpolated.csv')
    LZ40_DO_Inter = pd.read_csv(f'{input_dir}/water_quality_LZ40_DISSOLVED OXYGEN_Interpolated.csv')

    L001_DO_Inter.columns = L001_DO_Inter.columns.str.replace('Data', 'Data_L001_DO_Inter')
    L004_DO_Inter.columns = L004_DO_Inter.columns.str.replace('Data', 'Data_L004_DO_Inter')
    L005_DO_Inter.columns = L005_DO_Inter.columns.str.replace('Data', 'Data_L005_DO_Inter')
    L006_DO_Inter.columns = L006_DO_Inter.columns.str.replace('Data', 'Data_L006_DO_Inter')
    L007_DO_Inter.columns = L007_DO_Inter.columns.str.replace('Data', 'Data_L007_DO_Inter')
    L008_DO_Inter.columns = L008_DO_Inter.columns.str.replace('Data', 'Data_L008_DO_Inter')
    LZ40_DO_Inter.columns = LZ40_DO_Inter.columns.str.replace('Data', 'Data_LZ40_DO_Inter')

    LO_DO_data_Inter = pd.merge(L001_DO_Inter, L004_DO_Inter, how='left', on='date')
    LO_DO_data_Inter = pd.merge(LO_DO_data_Inter, L005_DO_Inter, how='left', on='date')
    LO_DO_data_Inter = pd.merge(LO_DO_data_Inter, L006_DO_Inter, how='left', on='date')
    LO_DO_data_Inter = pd.merge(LO_DO_data_Inter, L007_DO_Inter, how='left', on='date')
    LO_DO_data_Inter = pd.merge(LO_DO_data_Inter, L008_DO_Inter, how='left', on='date')
    LO_DO_data_Inter = pd.merge(LO_DO_data_Inter, LZ40_DO_Inter, how='left', on='date')
    LO_DO_data_Inter = LO_DO_data_Inter.loc[:, ~LO_DO_data_Inter.columns.str.startswith('Unnamed')]
    # Read clean LO_DO data
    LO_DO_data_Inter['Mean_DO'] = LO_DO_data_Inter.mean(axis=1, numeric_only=True)
    LO_DO_data_Inter = DF_Date_Range(LO_DO_data_Inter, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    LO_DO_data_Inter.to_csv(f'{output_dir}/LO_DO_Clean_daily.csv', index=False)
    LO_DO_data_Inter = LO_DO_data_Inter.set_index(['date'])
    LO_DO_data_Inter.index = pd.to_datetime(LO_DO_data_Inter.index, unit='ns')
    LO_DO_Monthly_Inter = LO_DO_data_Inter.resample('M').mean()
    LO_DO_Monthly_Inter.to_csv(f'{output_dir}/LO_DO_Monthly_Inter.csv')

    # RADT Data in Lake Okeechobee
    # Create File (LO_RADT)
    L001_RADT = pd.read_csv(f'{input_dir}/L001_RADT.csv')
    L005_RADT = pd.read_csv(f'{input_dir}/L005_RADT.csv')
    L006_RADT = pd.read_csv(f'{input_dir}/L006_RADT.csv')
    LZ40_RADT = pd.read_csv(f'{input_dir}/LZ40_RADT.csv')

    L001_RADT.columns = L001_RADT.columns.str.replace('Unnamed: 0', 'Unnamed: 0_L001_RADT')
    L005_RADT.columns = L005_RADT.columns.str.replace('Unnamed: 0', 'Unnamed: 0_L005_RADT')
    L006_RADT.columns = L006_RADT.columns.str.replace('Unnamed: 0', 'Unnamed: 0_L006_RADT')
    LZ40_RADT.columns = LZ40_RADT.columns.str.replace('Unnamed: 0', 'Unnamed: 0_LZ40_RADT')

    LO_RADT_data = pd.merge(L006_RADT, L001_RADT, how='left', on='date')
    LO_RADT_data = pd.merge(LO_RADT_data, L005_RADT, how='left', on='date')
    LO_RADT_data = pd.merge(LO_RADT_data, LZ40_RADT, how='left', on='date')
    LO_RADT_data = LO_RADT_data.loc[:, ~LO_RADT_data.columns.str.startswith('Unnamed')]
    LO_RADT_data['Mean_RADT'] = LO_RADT_data.mean(axis=1, numeric_only=True)
    LO_RADT_data = DF_Date_Range(LO_RADT_data, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    LO_RADT_data.to_csv(f'{output_dir}/LO_RADT_data.csv', index=False)

    # RADP Data in Lake Okeechobee
    # Create File (LO_RADP)
    L001_RADP = pd.read_csv(f'{input_dir}/L001_RADP.csv')
    L005_RADP = pd.read_csv(f'{input_dir}/L005_RADP.csv')
    L006_RADP = pd.read_csv(f'{input_dir}/L006_RADP.csv')
    LZ40_RADP = pd.read_csv(f'{input_dir}/LZ40_RADP.csv')

    L001_RADP.columns = L001_RADP.columns.str.replace('Unnamed: 0', 'Unnamed: 0_L001_RADP')
    L005_RADP.columns = L005_RADP.columns.str.replace('Unnamed: 0', 'Unnamed: 0_L005_RADP')
    L006_RADP.columns = L006_RADP.columns.str.replace('Unnamed: 0', 'Unnamed: 0_L006_RADP')
    LZ40_RADP.columns = LZ40_RADP.columns.str.replace('Unnamed: 0', 'Unnamed: 0_LZ40_RADP')

    LO_RADP_data = pd.merge(L006_RADP, L001_RADP, how='left', on='date')
    LO_RADP_data = pd.merge(LO_RADP_data, L005_RADP, how='left', on='date')
    LO_RADP_data = pd.merge(LO_RADP_data, LZ40_RADP, how='left', on='date')
    LO_RADP_data = LO_RADP_data.loc[:, ~LO_RADP_data.columns.str.startswith('Unnamed')]
    LO_RADP_data['Mean_RADP'] = LO_RADP_data.mean(axis=1, numeric_only=True)
    LO_RADP_data = DF_Date_Range(LO_RADP_data, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    LO_RADP_data.to_csv(f'{output_dir}/LO_RADP_data.csv', index=False)

    # Interpolated Chla Corrected Observations in Lake
    L001_Chla_Inter = pd.read_csv(f'{input_dir}/water_quality_L001_CHLOROPHYLL-A, CORRECTED_Interpolated.csv')
    L004_Chla_Inter = pd.read_csv(f'{input_dir}/water_quality_L004_CHLOROPHYLL-A, CORRECTED_Interpolated.csv')
    L005_Chla_Inter = pd.read_csv(f'{input_dir}/water_quality_L005_CHLOROPHYLL-A, CORRECTED_Interpolated.csv')
    L006_Chla_Inter = pd.read_csv(f'{input_dir}/water_quality_L006_CHLOROPHYLL-A, CORRECTED_Interpolated.csv')
    L007_Chla_Inter = pd.read_csv(f'{input_dir}/water_quality_L007_CHLOROPHYLL-A, CORRECTED_Interpolated.csv')
    L008_Chla_Inter = pd.read_csv(f'{input_dir}/water_quality_L008_CHLOROPHYLL-A, CORRECTED_Interpolated.csv')
    LZ40_Chla_Inter = pd.read_csv(f'{input_dir}/water_quality_LZ40_CHLOROPHYLL-A, CORRECTED_Interpolated.csv')

    L001_Chla_Inter.columns = L001_Chla_Inter.columns.str.replace('Data', 'Data_L001_Chla_Inter')
    L004_Chla_Inter.columns = L004_Chla_Inter.columns.str.replace('Data', 'Data_L004_Chla_Inter')
    L005_Chla_Inter.columns = L005_Chla_Inter.columns.str.replace('Data', 'Data_L005_Chla_Inter')
    L006_Chla_Inter.columns = L006_Chla_Inter.columns.str.replace('Data', 'Data_L006_Chla_Inter')
    L007_Chla_Inter.columns = L007_Chla_Inter.columns.str.replace('Data', 'Data_L007_Chla_Inter')
    L008_Chla_Inter.columns = L008_Chla_Inter.columns.str.replace('Data', 'Data_L008_Chla_Inter')
    LZ40_Chla_Inter.columns = LZ40_Chla_Inter.columns.str.replace('Data', 'Data_LZ40_Chla_Inter')

    LO_Chla_data_Inter = pd.merge(L001_Chla_Inter, L004_Chla_Inter, how='left', on='date')
    LO_Chla_data_Inter = pd.merge(LO_Chla_data_Inter, L005_Chla_Inter, how='left', on='date')
    LO_Chla_data_Inter = pd.merge(LO_Chla_data_Inter, L006_Chla_Inter, how='left', on='date')
    LO_Chla_data_Inter = pd.merge(LO_Chla_data_Inter, L007_Chla_Inter, how='left', on='date')
    LO_Chla_data_Inter = pd.merge(LO_Chla_data_Inter, L008_Chla_Inter, how='left', on='date')
    LO_Chla_data_Inter = pd.merge(LO_Chla_data_Inter, LZ40_Chla_Inter, how='left', on='date')
    LO_Chla_data_Inter = LO_Chla_data_Inter.loc[:, ~LO_Chla_data_Inter.columns.str.startswith('Unnamed')]
    # Read clean LO_Chla data
    LO_Chla_data_Inter['Mean_Chla'] = LO_Chla_data_Inter.mean(axis=1, numeric_only=True)
    LO_Chla_data_Inter.to_csv(f'{output_dir}/LO_Chla_Clean_daily.csv', index=False)
    # Monthly
    LO_Chla_data_Inter = LO_Chla_data_Inter.set_index(['date'])
    LO_Chla_data_Inter.index = pd.to_datetime(LO_Chla_data_Inter.index, unit='ns')
    LO_Chla_Monthly_Inter = LO_Chla_data_Inter.resample('M').mean()
    LO_Chla_Monthly_Inter.to_csv(f'{output_dir}/LO_Chla_Monthly_Inter.csv')

    # Interpolated Chla LC Observations in Lake
    L001_Chla_LC_Inter = pd.read_csv(f'{input_dir}/water_quality_L001_CHLOROPHYLL-A(LC)_Interpolated.csv')
    L004_Chla_LC_Inter = pd.read_csv(f'{input_dir}/water_quality_L004_CHLOROPHYLL-A(LC)_Interpolated.csv')
    L005_Chla_LC_Inter = pd.read_csv(f'{input_dir}/water_quality_L005_CHLOROPHYLL-A(LC)_Interpolated.csv')
    L006_Chla_LC_Inter = pd.read_csv(f'{input_dir}/water_quality_L006_CHLOROPHYLL-A(LC)_Interpolated.csv')
    L007_Chla_LC_Inter = pd.read_csv(f'{input_dir}/water_quality_L007_CHLOROPHYLL-A(LC)_Interpolated.csv')
    L008_Chla_LC_Inter = pd.read_csv(f'{input_dir}/water_quality_L008_CHLOROPHYLL-A(LC)_Interpolated.csv')
    LZ40_Chla_LC_Inter = pd.read_csv(f'{input_dir}/water_quality_LZ40_CHLOROPHYLL-A(LC)_Interpolated.csv')

    L001_Chla_LC_Inter.columns = L001_Chla_LC_Inter.columns.str.replace('Data', 'Data_L001_Chla_LC_Inter')
    L004_Chla_LC_Inter.columns = L004_Chla_LC_Inter.columns.str.replace('Data', 'Data_L004_Chla_LC_Inter')
    L005_Chla_LC_Inter.columns = L005_Chla_LC_Inter.columns.str.replace('Data', 'Data_L005_Chla_LC_Inter')
    L006_Chla_LC_Inter.columns = L006_Chla_LC_Inter.columns.str.replace('Data', 'Data_L006_Chla_LC_Inter')
    L007_Chla_LC_Inter.columns = L007_Chla_LC_Inter.columns.str.replace('Data', 'Data_L007_Chla_LC_Inter')
    L008_Chla_LC_Inter.columns = L008_Chla_LC_Inter.columns.str.replace('Data', 'Data_L008_Chla_LC_Inter')
    LZ40_Chla_LC_Inter.columns = LZ40_Chla_LC_Inter.columns.str.replace('Data', 'Data_LZ40_Chla_LC_Inter')

    LO_Chla_LC_data_Inter = pd.merge(L001_Chla_LC_Inter, L004_Chla_LC_Inter, how='left', on='date')
    LO_Chla_LC_data_Inter = pd.merge(LO_Chla_LC_data_Inter, L005_Chla_LC_Inter, how='left', on='date')
    LO_Chla_LC_data_Inter = pd.merge(LO_Chla_LC_data_Inter, L006_Chla_LC_Inter, how='left', on='date')
    LO_Chla_LC_data_Inter = pd.merge(LO_Chla_LC_data_Inter, L007_Chla_LC_Inter, how='left', on='date')
    LO_Chla_LC_data_Inter = pd.merge(LO_Chla_LC_data_Inter, L008_Chla_LC_Inter, how='left', on='date')
    LO_Chla_LC_data_Inter = pd.merge(LO_Chla_LC_data_Inter, LZ40_Chla_LC_Inter, how='left', on='date')
    LO_Chla_LC_data_Inter = LO_Chla_LC_data_Inter.loc[:, ~LO_Chla_LC_data_Inter.columns.str.startswith('Unnamed')]
    # Read clean LO_Chla_LC data
    LO_Chla_LC_data_Inter['Mean_Chla_LC'] = LO_Chla_LC_data_Inter.mean(axis=1, numeric_only=True)
    LO_Chla_LC_data_Inter.to_csv(f'{output_dir}/LO_Chla_LC_Clean_daily.csv', index=False)
    # Monthly
    LO_Chla_LC_data_Inter = LO_Chla_LC_data_Inter.set_index(['date'])
    LO_Chla_LC_data_Inter.index = pd.to_datetime(LO_Chla_LC_data_Inter.index, unit='ns')
    LO_Chla_LC_Monthly_Inter = LO_Chla_LC_data_Inter.resample('M').mean()
    LO_Chla_LC_Monthly_Inter.to_csv(f'{output_dir}/LO_Chla_LC_Monthly_Inter.csv')

    # Merge the Chla Data
    # Create Files LO_Avg_Chla and Obs_Chla_LO
    # Chla_date = pd.date_range(start=LO_Chla_data_Inter['date'].iloc[0], end=LO_Chla_LC_data_Inter['date'].iloc[-1], freq='D')  # noqa: E501
    LO_Chla_data_Inter['date'] = LO_Chla_data_Inter.index
    LO_Chla_data_Inter = DF_Date_Range(LO_Chla_data_Inter, St_Yr, St_M, St_D, 2010, 10, 19)
    LO_Chla_df = pd.DataFrame(LO_Chla_data_Inter['date'], columns=['date'])
    LO_Chla_df['Chla'] = LO_Chla_data_Inter['Mean_Chla']
    LO_Chla_LC_df = pd.DataFrame(LO_Chla_LC_data_Inter.index, columns=['date'])
    LO_Chla_LC_df['Chla'] = LO_Chla_LC_data_Inter['Mean_Chla_LC']

    LO_Chla_Merge = pd.concat([LO_Chla_df, LO_Chla_LC_df]).reset_index(drop=True)
    LO_Chla_Merge.to_csv(f'{output_dir}/LO_Merged_Chla.csv', index=False)

    LO_Chla_Merge = LO_Chla_Merge.set_index(['date'])
    LO_Chla_Merge.index = pd.to_datetime(LO_Chla_Merge.index, unit='ns')
    LO_Chla_Merge_Monthly_Inter = LO_Chla_Merge.resample('M').mean()
    LO_Chla_Merge_Monthly_Inter.to_csv(f'{output_dir}/LO_Chla_Merge_Monthly_Inter.csv')

    # Create files (LO_Chla_Obs.csv, N_Merged_Chla.csv, and S_Merged_Chla.csv)
    L001_Chla = pd.read_csv(f'{input_dir}/water_quality_L001_CHLOROPHYLL-A, CORRECTED.csv')
    L001_Chla.drop(columns=['days'], inplace=True)
    L004_Chla = pd.read_csv(f'{input_dir}/water_quality_L004_CHLOROPHYLL-A, CORRECTED.csv')
    L004_Chla.drop(columns=['days'], inplace=True)
    L005_Chla = pd.read_csv(f'{input_dir}/water_quality_L005_CHLOROPHYLL-A, CORRECTED.csv')
    L005_Chla.drop(columns=['days'], inplace=True)
    L006_Chla = pd.read_csv(f'{input_dir}/water_quality_L006_CHLOROPHYLL-A, CORRECTED.csv')
    L006_Chla.drop(columns=['days'], inplace=True)
    L007_Chla = pd.read_csv(f'{input_dir}/water_quality_L007_CHLOROPHYLL-A, CORRECTED.csv')
    L007_Chla.drop(columns=['days'], inplace=True)
    L008_Chla = pd.read_csv(f'{input_dir}/water_quality_L008_CHLOROPHYLL-A, CORRECTED.csv')
    L008_Chla.drop(columns=['days'], inplace=True)
    LZ40_Chla = pd.read_csv(f'{input_dir}/water_quality_LZ40_CHLOROPHYLL-A, CORRECTED.csv')
    LZ40_Chla.drop(columns=['days'], inplace=True)
    L001_Chla_LC = pd.read_csv(f'{input_dir}/water_quality_L001_CHLOROPHYLL-A(LC).csv')
    L001_Chla_LC.drop(columns=['days'], inplace=True)
    L004_Chla_LC = pd.read_csv(f'{input_dir}/water_quality_L004_CHLOROPHYLL-A(LC).csv')
    L004_Chla_LC.drop(columns=['days'], inplace=True)
    L005_Chla_LC = pd.read_csv(f'{input_dir}/water_quality_L005_CHLOROPHYLL-A(LC).csv')
    L005_Chla_LC.drop(columns=['days'], inplace=True)
    L006_Chla_LC = pd.read_csv(f'{input_dir}/water_quality_L006_CHLOROPHYLL-A(LC).csv')
    L006_Chla_LC.drop(columns=['days'], inplace=True)
    L007_Chla_LC = pd.read_csv(f'{input_dir}/water_quality_L007_CHLOROPHYLL-A(LC).csv')
    L007_Chla_LC.drop(columns=['days'], inplace=True)
    L008_Chla_LC = pd.read_csv(f'{input_dir}/water_quality_L008_CHLOROPHYLL-A(LC).csv')
    L008_Chla_LC.drop(columns=['days'], inplace=True)
    LZ40_Chla_LC = pd.read_csv(f'{input_dir}/water_quality_LZ40_CHLOROPHYLL-A(LC).csv')
    LZ40_Chla_LC.drop(columns=['days'], inplace=True)
    
    LO_Chla = pd.merge(L001_Chla, L004_Chla, how='left', on='date')
    LO_Chla = LO_Chla.loc[:, ~LO_Chla.columns.str.startswith('Unnamed')]
    LO_Chla = pd.merge(LO_Chla, L005_Chla, how='left', on='date')
    LO_Chla = LO_Chla.loc[:, ~LO_Chla.columns.str.startswith('Unnamed')]
    LO_Chla = pd.merge(LO_Chla, L006_Chla, how='left', on='date')
    LO_Chla = LO_Chla.loc[:, ~LO_Chla.columns.str.startswith('Unnamed')]
    LO_Chla = pd.merge(LO_Chla, L007_Chla, how='left', on='date')
    LO_Chla = LO_Chla.loc[:, ~LO_Chla.columns.str.startswith('Unnamed')]
    LO_Chla = pd.merge(LO_Chla, L008_Chla, how='left', on='date')
    LO_Chla = LO_Chla.loc[:, ~LO_Chla.columns.str.startswith('Unnamed')]
    LO_Chla = pd.merge(LO_Chla, LZ40_Chla, how='left', on='date')
    LO_Chla = LO_Chla.loc[:, ~LO_Chla.columns.str.startswith('Unnamed')]
    LO_Chla = LO_Chla.set_index('date')
    LO_Chla['Mean_Chla'] = LO_Chla.mean(axis=1)
    LO_Chla = LO_Chla.reset_index()
    LO_Chla_N_cols = ['L001_CHLOROPHYLL-A, CORRECTED_ug/L', 'L005_CHLOROPHYLL-A, CORRECTED_ug/L', 'L008_CHLOROPHYLL-A, CORRECTED_ug/L']
    LO_Chla['Chla_North'] = LO_Chla[LO_Chla_N_cols].mean(axis=1)
    LO_Chla_S_cols = ['L004_CHLOROPHYLL-A, CORRECTED_ug/L', 'L006_CHLOROPHYLL-A, CORRECTED_ug/L', 'L007_CHLOROPHYLL-A, CORRECTED_ug/L','L008_CHLOROPHYLL-A, CORRECTED_ug/L','LZ40_CHLOROPHYLL-A, CORRECTED_ug/L']
    LO_Chla['Chla_South'] = LO_Chla[LO_Chla_S_cols].mean(axis=1)

    LO_Chla_LC = pd.merge(L001_Chla_LC, L004_Chla_LC, how='left', on='date')
    LO_Chla_LC = LO_Chla_LC.loc[:, ~LO_Chla_LC.columns.str.startswith('Unnamed')]
    LO_Chla_LC = pd.merge(LO_Chla_LC, L005_Chla_LC, how='left', on='date')
    LO_Chla_LC = LO_Chla_LC.loc[:, ~LO_Chla_LC.columns.str.startswith('Unnamed')]
    LO_Chla_LC = pd.merge(LO_Chla_LC, L006_Chla_LC, how='left', on='date')
    LO_Chla_LC = LO_Chla_LC.loc[:, ~LO_Chla_LC.columns.str.startswith('Unnamed')]
    LO_Chla_LC = pd.merge(LO_Chla_LC, L007_Chla_LC, how='left', on='date')
    LO_Chla_LC = LO_Chla_LC.loc[:, ~LO_Chla_LC.columns.str.startswith('Unnamed')]
    LO_Chla_LC = pd.merge(LO_Chla_LC, L008_Chla_LC, how='left', on='date')
    LO_Chla_LC = LO_Chla_LC.loc[:, ~LO_Chla_LC.columns.str.startswith('Unnamed')]
    LO_Chla_LC = pd.merge(LO_Chla_LC, LZ40_Chla_LC, how='left', on='date')
    LO_Chla_LC = LO_Chla_LC.loc[:, ~LO_Chla_LC.columns.str.startswith('Unnamed')]
    LO_Chla_LC = LO_Chla_LC.set_index('date')
    LO_Chla_LC['Mean_Chla'] = LO_Chla_LC.mean(axis=1)
    LO_Chla_LC = LO_Chla_LC.reset_index()
    LO_Chla_LC_N_cols = ['L001_CHLOROPHYLL-A(LC)_ug/L', 'L005_CHLOROPHYLL-A(LC)_ug/L', 'L008_CHLOROPHYLL-A(LC)_ug/L']
    LO_Chla_LC['Chla_North'] = LO_Chla_LC[LO_Chla_LC_N_cols].mean(axis=1)
    LO_Chla_LC_S_cols = ['L004_CHLOROPHYLL-A(LC)_ug/L', 'L006_CHLOROPHYLL-A(LC)_ug/L', 'L007_CHLOROPHYLL-A(LC)_ug/L','L008_CHLOROPHYLL-A(LC)_ug/L','LZ40_CHLOROPHYLL-A(LC)_ug/L']
    LO_Chla_LC['Chla_South'] = LO_Chla_LC[LO_Chla_LC_S_cols].mean(axis=1)

    LO_Chla = DF_Date_Range(LO_Chla, 2008, 1, 1, 2010, 10, 19)
    LO_Chla_df = pd.DataFrame(LO_Chla['date'], columns=['date'])
    LO_Chla_df['Chla'] = LO_Chla['Mean_Chla']
    LO_Chla_df['Chla_N'] = LO_Chla['Chla_North']
    LO_Chla_df['Chla_S'] = LO_Chla['Chla_South']

    LO_Chla_LC = DF_Date_Range(LO_Chla_LC, 2010, 10, 20, 2023, 6, 30)
    LO_Chla_LC_df = pd.DataFrame(LO_Chla_LC['date'], columns=['date'])
    LO_Chla_LC_df['Chla'] = LO_Chla_LC['Mean_Chla']
    LO_Chla_LC_df['Chla_N'] = LO_Chla_LC['Chla_North']
    LO_Chla_LC_df['Chla_S'] = LO_Chla_LC['Chla_South']

    LO_Chla_Merge = pd.concat([LO_Chla_df, LO_Chla_LC_df]).reset_index(drop=True)
    LO_Chla_Merge.to_csv(f'{output_dir}/LO_Chla_Obs.csv')
    LO_Chla_Merge[['date', 'Chla_N']].rename(columns={'Chla_N': 'Chla'}).to_csv(f'{output_dir}/N_Merged_Chla.csv', index=False)
    LO_Chla_Merge[['date', 'Chla_S']].rename(columns={'Chla_S': 'Chla'}).to_csv(f'{output_dir}/S_Merged_Chla.csv', index=False)

    # Create Files S65E_Avg_Chla
    S65E_Chla_Inter = pd.read_csv(f'{input_dir}/water_quality_S65E_CHLOROPHYLL-A, CORRECTED_Interpolated.csv')
    S65E_Chla_LC_Inter = pd.read_csv(f'{input_dir}/water_quality_S65E_CHLOROPHYLL-A(LC)_Interpolated.csv')

    S65E_Chla_Merge = pd.concat([S65E_Chla_Inter, S65E_Chla_LC_Inter]).reset_index(drop=True)
    S65E_Chla_Merge = S65E_Chla_Merge.drop_duplicates(subset="date", keep='first')  # there are duplicates in the data
    # S65E_Chla_Merge.rename(columns={S65E_Chla_Merge.columns[-1]: 'Chla'}, inplace=True)
    S65E_Chla_Merge = S65E_Chla_Merge.loc[:, ~S65E_Chla_Merge.columns.str.contains('^Unnamed')]
    S65E_Chla_Merge.to_csv(f'{output_dir}/S65E_Chla_Merged.csv', index=False)

    # NO Loads
    # Create File (Daily_NOx_External_Loads)
    S65_NO = pd.read_csv(f'{input_dir}/water_quality_S65E_NITRATE+NITRITE-N_Interpolated.csv')
    S71_NO = pd.read_csv(f'{input_dir}/water_quality_S71_NITRATE+NITRITE-N_Interpolated.csv')
    S72_NO = pd.read_csv(f'{input_dir}/water_quality_S72_NITRATE+NITRITE-N_Interpolated.csv')
    S84_NO = pd.read_csv(f'{input_dir}/water_quality_S84_NITRATE+NITRITE-N_Interpolated.csv')
    S127_NO = pd.read_csv(f'{input_dir}/water_quality_S127_NITRATE+NITRITE-N_Interpolated.csv')
    S133_NO = pd.read_csv(f'{input_dir}/water_quality_S133_NITRATE+NITRITE-N_Interpolated.csv')
    # S135_NO = pd.read_csv(f'{input_dir}/water_quality_S135_NITRATE+NITRITE-N_Interpolated.csv')
    S154_NO = pd.read_csv(f'{input_dir}/water_quality_S154_NITRATE+NITRITE-N_Interpolated.csv')
    S191_NO = pd.read_csv(f'{input_dir}/water_quality_S191_NITRATE+NITRITE-N_Interpolated.csv')
    S308_NO = pd.read_csv(f'{input_dir}/water_quality_S308C_NITRATE+NITRITE-N_Interpolated.csv')
    FISHP_NO = pd.read_csv(f'{input_dir}/water_quality_FECSR78_NITRATE+NITRITE-N_Interpolated.csv')
    L8_NO = pd.read_csv(f'{input_dir}/water_quality_CULV10A_NITRATE+NITRITE-N_Interpolated.csv')
    S4_NO = pd.read_csv(f'{input_dir}/water_quality_S4_NITRATE+NITRITE-N_Interpolated.csv')

    NO_names = ['S65_NO', 'S71_NO', 'S72_NO', 'S84_NO', 'S127_NO', 'S133_NO', 'S154_NO', 'S191_NO',
                'S308_NO', 'FISHP_NO', 'L8_NO', 'S4_NO']
    NO_list = {'S65_NO': S65_NO, 'S71_NO': S71_NO, 'S72_NO': S72_NO, 'S84_NO': S84_NO, 'S127_NO': S127_NO,
               'S133_NO': S133_NO, 'S154_NO': S154_NO, 'S191_NO': S191_NO, 'S308_NO': S308_NO,
               'FISHP_NO': FISHP_NO, 'L8_NO': L8_NO, 'S4_NO': S4_NO}
    #TODO: Why is this date hard coded into this part?
    date_NO = pd.date_range(start='1/1/2008', end='3/31/2023', freq='D')

    NO_df = pd.DataFrame(date_NO, columns=['date'])
    for i in range(len(NO_names)):
        y = DF_Date_Range(NO_list[NO_names[i]], St_Yr, St_M, St_D, En_Yr, En_M, En_D)

        if len(y.iloc[:, -1:].values) == len(NO_df['date']):
            NO_df[NO_names[i]] = y.iloc[:, -1:].values
        else:
            y.rename(columns={y.columns[-1]: NO_names[i]}, inplace=True)
            NO_df = pd.merge(NO_df, y[['date', NO_names[i]]], on='date', how='left')

    Flow_df = DF_Date_Range(Flow_df, St_Yr, St_M, St_D, En_Yr, En_M, En_D)

    # Determine NO Loads
    # Ensure 'date' is datetime
    NO_df['date'] = pd.to_datetime(NO_df['date'])
    Flow_df['date'] = pd.to_datetime(Flow_df['date'])

    # Merge the two dataframes on date - this will ensure that the dates match
    merged = pd.merge(NO_df, Flow_df, on='date', how='inner')

    # Compute NO Loads
    NO_Loads_In = merged[['date']].copy()
    NO_Loads_In['S65_NO_Ld'] = merged['S65_Q'] * merged['S65_NO'] * 1000
    NO_Loads_In['S71_NO_Ld'] = merged['S71_Q'] * merged['S71_NO'] * 1000
    NO_Loads_In['S71_NO_Ld'] = merged['S71_Q'] * merged['S71_NO'] * 1000
    NO_Loads_In['S72_NO_Ld'] = merged['S72_Q'] * merged['S72_NO'] * 1000
    NO_Loads_In['S84_NO_Ld'] = merged['S84_Q'] * merged['S84_NO'] * 1000
    NO_Loads_In['S127_NO_Ld'] = merged['S127_In'] * merged['S127_NO'] * 1000
    NO_Loads_In['S133_NO_Ld'] = merged['S133_P_Q'] * merged['S133_NO'] * 1000
    # NO_Loads_In['S135_NO_Ld'] = Flow_df['S135_In'].values * NO_df['S135_NO'].values * 1000
    NO_Loads_In['S154_NO_Ld'] = merged['S154_Q'] * merged['S154_NO'] * 1000
    NO_Loads_In['S191_NO_Ld'] = merged['S191_Q'] * merged['S191_NO'] * 1000
    NO_Loads_In['S308_NO_Ld'] = merged['S308_In'] * merged['S308_NO'] * 1000
    NO_Loads_In['FISHP_NO_Ld'] = merged['FISHP_Q'] * merged['FISHP_NO'] * 1000
    NO_Loads_In['L8_NO_Ld'] = merged['L8_In'] * merged['L8_NO'] * 1000
    NO_Loads_In['S4_NO_Ld'] = merged['S4_P_Q'] * merged['S4_NO'] * 1000
    # Calculate the total External Loads to Lake Okeechobee
    NO_Loads_In['External_NO_Ld_mg'] = NO_Loads_In.sum(axis=1, numeric_only=True)
    NO_Loads_In.to_csv(f'{output_dir}/LO_External_Loadings_NO.csv', index=False)

    # Determine Chla Loads
    # Create File (Chla_Loads_In)
    # Read and date-filter Chla data
    S65E_Chla = pd.read_csv(f'{output_dir}/S65E_Chla_Merged.csv')
    S65E_Chla['date'] = pd.to_datetime(S65E_Chla['date'])  # Ensure date column is datetime
    S65E_Chla = DF_Date_Range(S65E_Chla, St_Yr, St_M, St_D, En_Yr, En_M, En_D)
    # Merge on date
    merged = pd.merge(Flow_df[['date', 'Inflows']], S65E_Chla[['date', 'Data']], on='date', how='inner')
    # Calculate Chlorophyll-a loads
    merged['Chla_Loads'] = merged['Inflows'] * merged['Data']
    # Save results
    Chla_Loads_In = merged[['date', 'Chla_Loads']]
    Chla_Loads_In.to_csv(f'{output_dir}/Chla_Loads_In.csv', index=False)


    # Write Data into csv files
    # write Avg Stage (ft, m) Storage (acft, m3) SA (acres) to csv
    LO_Stg_Sto_SA_df.to_csv(f'{output_dir}/Average_LO_Storage_3MLag.csv', index=False)
    # Write S65 TP concentrations (mg/L)
    S65_total_TP.to_csv(f'{output_dir}/S65_TP_3MLag.csv', index=False)
    # TP External Loads 3 Months Lag (mg)
    TP_Loads_In_3MLag_df.to_csv(f'{output_dir}/LO_External_Loadings_3MLag.csv', index=False)
    # Flow dataframe including Inflows, NetFlows, and Outflows (all in m3/day)
    Flow_df.to_csv(f'{output_dir}/Flow_df_3MLag.csv', index=False)
    # Inflows (cmd)
    LO_Inflows_BK.to_csv(f'{output_dir}/LO_Inflows_BK.csv', index=False)
    # Outflows (cmd)
    Outflows_consd.to_csv(f'{output_dir}/Outflows_consd.csv', index=False)
    # NetFlows (cmd)
    Netflows.to_csv(f'{output_dir}/Netflows_acft.csv', index=False)
    # Total flows to WCAs (acft)
    TotalQWCA.to_csv(f'{output_dir}/TotalQWCA_Obs.csv', index=False)
    # INDUST Outflows (cmd)
    INDUST_Outflows.to_csv(f'{output_dir}/INDUST_Outflows.csv', index=False)


if __name__ == "__main__":
    main(sys.argv[1].rstrip("/"), sys.argv[2].rstrip("/"))
