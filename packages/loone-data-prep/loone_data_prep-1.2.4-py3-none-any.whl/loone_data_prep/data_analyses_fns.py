# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 00:42:20 2022

@author: osama
"""

# Data Analyses Functions
import pandas as pd
from datetime import datetime


def Data_Daily_Spread(File_Name):
    Data_In = pd.read_csv('./%s.csv' % File_Name)
    Data_In = Data_In.set_index(['Date'])
    Data_In.index = pd.to_datetime(Data_In.index, unit='ns')
    Data_Out_df = Data_In.resample('D').mean()
    Data_Out_df.to_csv('./%s_daily.csv' % File_Name)


def Data_to_Monthly(File_Name, method):
    Data_In = pd.read_csv('./%s.csv' % File_Name)
    # Set date as index
    Data_In = Data_In.set_index('Date')
    Data_In.index = pd.to_datetime(Data_In.index, unit='ns')
    # convert time series to monthly (mean, or sum)
    if method == 'mean':
        Data_Monthly = Data_In.resample('M').mean()
    elif method == 'sum':
        Data_Monthly = Data_In.resample('M').sum()
    # Export weekly average TP concentrations
    Data_Monthly.to_csv('./%s_Monthly.csv' % File_Name)


def Data_to_Annual(File_Name, method):
    Data_In = pd.read_csv('./%s.csv' % File_Name)
    # Set date as index
    Data_In = Data_In.set_index('Date')
    Data_In.index = pd.to_datetime(Data_In.index, unit='ns')
    # convert time series to monthly (mean, or sum)
    if method == 'mean':
        Data_Annual = Data_In.resample('Y').mean()
    elif method == 'sum':
        Data_Annual = Data_In.resample('Y').sum()
    # Export weekly average TP concentrations
    Data_Annual.to_csv('./%s_Annual.csv' % File_Name)


def Data_Merge(File_Names):
    File_Names_df = pd.read_csv('./%s.csv' % File_Names)
    Data_0 = pd.read_csv('./%s.csv' % File_Names_df['File_Names'].iloc[0])
    Data_1 = pd.read_csv('./%s.csv' % File_Names_df['File_Names'].iloc[1])
    Data_Merge = pd.merge(Data_0, Data_1, how='outer', on='date')
    for i in range(2, len(File_Names_df.index)):
        Data = pd.read_csv('./%s.csv' % File_Names_df['File_Names'].iloc[i])
        Data_Merge = Data_Merge.merge(Data, how='outer', on='date')
    Data_Merge.to_csv('./Data_Merged.csv')


# Define date range for a csv file
def Csv_Date_Range(File_Name, start_year, start_month, start_day, end_year, end_month, end_day):
    # Identify the date ranges
    startyear = start_year
    startmonth = start_month
    startday = start_day
    endyear = end_year
    endmonth = end_month
    endday = end_day

    startdate = startyear, startmonth, startday
    year, month, day = map(int, startdate)
    startdate = datetime(year, month, day).date()
    enddate = endyear, endmonth, endday
    year, month, day = map(int, enddate)
    enddate = datetime(year, month, day).date()

    Data = pd.read_csv('./%s' % File_Name)
    Data['date'] = pd.to_datetime(Data['date'])
    mask = ((Data['date'] >= startdate) & (Data['date'] <= enddate))
    Data_Date_Range = Data.loc[mask]
    Data_Date_Range.to_csv('./%s_%s-%s.csv' % (File_Name[:-4], start_year, end_year))


# Define Date Range for dataframe
def DF_Date_Range(df_Name, start_year, start_month, start_day, end_year, end_month, end_day):
    # Identify the date ranges
    startyear = start_year
    startmonth = start_month
    startday = start_day
    endyear = end_year
    endmonth = end_month
    endday = end_day

    startdate = startyear, startmonth, startday
    year, month, day = map(int, startdate)
    startdate = datetime(year, month, day).date()
    enddate = endyear, endmonth, endday
    year, month, day = map(int, enddate)
    enddate = datetime(year, month, day).date()

    Data = df_Name
    Data['date'] = pd.to_datetime(Data['date'])
    mask = ((Data['date'].dt.date >= startdate) & (Data['date'].dt.date <= enddate))
    Data_Date_Range = Data.loc[mask]
    return (Data_Date_Range)


# This Following Loop assigns the 366 values of the predifined WCA3a_REG_Zone (One random year) in the WCA3A_REG
# dataframe to the entire study period.
def Replicate_oneyear(ReferenceYear, year, day_num):
    # Define the Leap Year
    def leap_year(y):
        if y % 400 == 0:
            return True
        if y % 100 == 0:
            return False
        if y % 4 == 0:
            return True
        else:
            return False
    leap_day_val = ReferenceYear['Data'].iloc[59]
    if leap_year(year):
        day_num_adj = day_num
    else:
        day_num_adj = day_num + (1 if day_num >= 60 else 0)
    day_value = leap_day_val if day_num_adj == 60 and leap_year(year) else ReferenceYear['Data'].iloc[day_num_adj-1]  # noqa: E501
    return (day_value)
