import os
import pandas as pd
import datetime
from loone_data_prep.utils import photo_period, get_synthetic_data

def get_NO_Loads_predicted(input_dir, output_dir):
    """
    input_dir: Directory where the input files are located.
    output_dir: Directory where the output files will be saved.
    This function reads the forecast inflow file, retrieves nitrate data for specified stations,
    """
    # TODO: Should this be an average/median of all of the ensembles? worst case?
    Q_in = pd.read_csv(os.path.join(input_dir, 'LO_Inflows_BK_forecast_01.csv'))

    datetime_str = Q_in['date'].iloc[0]
    date_start = datetime.datetime.strptime(datetime_str, '%Y-%m-%d')
    stations = [
        "S65E", "S71", "S72", "S84", "S127", "S133", 
        "S154", "S191", "S308C", "FECSR78", "CULV10A", "S4"
    ]

    station_alias_map = {
        "S65E": "S65_NO",
        "S71": "S71_NO",
        "S72": "S72_NO",
        "S84": "S84_NO",
        "S127": "S127_NO",
        "S133": "S133_NO",
        "S154": "S154_NO",
        "S191": "S191_NO",
        "S308C": "S308_NO",
        "FECSR78": "FISHP_NO",
        "CULV10A": "L8_NO",
        "S4": "S4_NO"
    }

    NO_list = {}
    NO_names = []

    for station, alias in station_alias_map.items():
        filename = f'water_quality_{station}_NITRATE+NITRITE-N_Interpolated.csv'
        file_path = os.path.join(input_dir, filename)
        
        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            print(f"{filename} not found.")
            continue

        # Forecast if needed
        if datetime_str not in df['date'].values:
            df = get_synthetic_data(date_start, df)
            df.to_csv(os.path.join(input_dir, f'water_quality_{station}_NITRATE+NITRITE-N_Interpolated_forecast.csv'), index=False)

        NO_list[alias] = df
        NO_names.append(alias)

    # date_NO = pd.date_range(start='1/1/2008', end='3/31/2023', freq='D')
    # Because of the flow df, I think this will be generated for every single ensemble member
    for ensemble in range(1, 52):
        Flow_df =pd.read_csv(f"{input_dir}/geoglows_flow_df_ens_{ensemble:02d}_predicted.csv")
        Flow_df['date'] = pd.to_datetime(Flow_df['date'])

        # Use Flow_df as the base for merging nitrate data
        NO_df = Flow_df[['date']].copy()

        for name in NO_names:
            y = NO_list[name]
            y.rename(columns={y.columns[-1]: name}, inplace=True)
            NO_df = pd.merge(NO_df, y[['date', name]], on='date', how='left')

        # Flow_df = DF_Date_Range(Flow_df, St_Yr, St_M, St_D, En_Yr, En_M, En_D)

        NO_df['date'] = pd.to_datetime(NO_df['date'])

        merged = pd.merge(NO_df, Flow_df, on='date', how='inner')

        NO_Loads_In = merged[['date']].copy()

        # Compute individual loads (edit flow variable names if needed)
        NO_Loads_In['S65_NO_Ld'] = merged['S65_Q'] * merged['S65_NO'] * 1000
        NO_Loads_In['S71_NO_Ld'] = merged['S71_Q'] * merged['S71_NO'] * 1000
        # NO_Loads_In['S72_NO_Ld'] = merged['S72_Q'] * merged['S72_NO'] * 1000 # No RFS forecast data
        NO_Loads_In['S84_NO_Ld'] = merged['S84_Q'] * merged['S84_NO'] * 1000
        # NO_Loads_In['S127_NO_Ld'] = merged['S127_In'] * merged['S127_NO'] * 1000 # This should be in here, figure out where it went
        NO_Loads_In['S133_NO_Ld'] = merged['S133_P_Q'] * merged['S133_NO'] * 1000
        NO_Loads_In['S154_NO_Ld'] = merged['S154_Q'] * merged['S154_NO'] * 1000
        # NO_Loads_In['S191_NO_Ld'] = merged['S191_Q'] * merged['S191_NO'] * 1000 #This should be in here, figure out where it went
        NO_Loads_In['S308_NO_Ld'] = merged['S308_In'] * merged['S308_NO'] * 1000
        NO_Loads_In['FISHP_NO_Ld'] = merged['FISHP_Q'] * merged['FISHP_NO'] * 1000
        # NO_Loads_In['L8_NO_Ld'] = merged['L8_In'] * merged['L8_NO'] * 1000 # No RFS forecast data
        # NO_Loads_In['S4_NO_Ld'] = merged['S4_P_Q'] * merged['S4_NO'] * 1000 # No RFS Forecast data

        NO_Loads_In['External_NO_Ld_mg'] = NO_Loads_In.sum(axis=1, numeric_only=True)

        NO_Loads_In.to_csv(f'{output_dir}/LO_External_Loadings_NO_ens_{ensemble:02d}_predicted.csv', index=False)
    return
