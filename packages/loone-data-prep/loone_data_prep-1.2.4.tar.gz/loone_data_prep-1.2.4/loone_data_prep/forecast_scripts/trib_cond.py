import pandas as pd
from datetime import datetime
from datetime import date, timedelta
import argparse

def create_trib_cond (weather_data, net_inflows, main_tributary, PI, output, ensemble):
    # TODO - check that all these unit are right
    future_date = date.today() + timedelta(days=15)
    today = date.today()

    all_data = pd.read_csv(weather_data)

    all_data['date'] = pd.to_datetime(all_data['datetime']).dt.date
    all_data = all_data[(all_data['date'] >= today) & (all_data['date'] <= future_date)]
    all_data = all_data.set_index(['date'])
    all_data.index = pd.to_datetime(all_data.index, unit='ns')
    Net_RF_Weekly =  all_data.resample('W-FRI').sum()
    # Net Inflows cfs
    Net_Inflows = pd.read_csv(net_inflows)
    Net_Inflows['date'] = pd.to_datetime(Net_Inflows['date']).dt.date
    Net_Inflows = Net_Inflows[(Net_Inflows['date'] >= today) & (Net_Inflows['date'] <= future_date)]
    #This is just the sum of the inflows that we want to read in 
    Net_Inflows['Net_Inflows'] = Net_Inflows['Netflows_acft']*(43560)  # acft to cf
    Net_Inflows = Net_Inflows.set_index(['date'])
    Net_Inflows.index = pd.to_datetime(Net_Inflows.index, unit='ns')
    Net_Inflow_Weekly = Net_Inflows.resample('W-FRI').mean()
    # S65 cfs
    S65E = pd.read_csv(main_tributary)
    S65E['date'] = pd.to_datetime(S65E['date']).dt.date
    S65E = S65E[(S65E['date'] >= today) & (S65E['date'] <= future_date)]
    #We want specifically S65_Q
    #Check that the units are right
    S65E = S65E.set_index(['date'])
    S65E = S65E / (0.0283168466 * 86400)  # Convert all columns from cmd to cfs  
    S65E.index = pd.to_datetime(S65E.index, unit='ns')  # Ensure index is datetime
    S65E_Weekly = S65E.resample('W-FRI').mean()
    # PI
    PI_week_data = pd.DataFrame(S65E_Weekly.index, columns=['date'])
    PI_week_data['date'] = pd.to_datetime(PI_week_data['date'])

    PI_data = pd.read_csv(PI)
    PI_data['date'] = pd.to_datetime(PI_data['date'])

    PI = PI_week_data.merge(PI_data[['date', 'PI']], on='date', how='left')

    ensemble_col = f"ensemble_{ensemble:02d}"

    # Create the initial DataFrame with the date
    Trib_Cond_Wkly = pd.DataFrame(S65E_Weekly.index, columns=['date'])

    # Calculate NetRF and NetInf
    Trib_Cond_Wkly['NetRF'] = Net_RF_Weekly['tp_corrected'].values - Net_RF_Weekly['evapotranspiration'].values
    # First, reset index so that 'date' becomes a column in Net_Inflow_Weekly
    Net_Inflow_Weekly_reset = Net_Inflow_Weekly.reset_index()

    # Merge the dataframes on 'date'
    Trib_Cond_Wkly = Trib_Cond_Wkly.merge(Net_Inflow_Weekly_reset[['date', 'Net_Inflows']], on='date', how='left')

    # Now Trib_Cond_Wkly will have a new 'Net_Inflows' column aligned by date
    Trib_Cond_Wkly.rename(columns={'Net_Inflows': 'NetInf'}, inplace=True)


    # Select only the desired ensemble column and rename it
    S65E_selected = S65E_Weekly[[ensemble_col]].rename(columns={ensemble_col: "S65E"})

    # Merge it into Trib_Cond_Wkly
    Trib_Cond_Wkly = Trib_Cond_Wkly.merge(S65E_selected, left_on="date", right_index=True, how="left")

    # Add the Palmer Index
    Trib_Cond_Wkly['Palmer'] = PI['PI'].values

    # Export to CSV
    Trib_Cond_Wkly.to_csv(output, index=False)
    
def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Download and process weather forecast data.")
    parser.add_argument("weather_data", help="Path to the weather forecasts.")
    parser.add_argument("net_inflows", help="Path to the net inflow forecasts.")
    parser.add_argument("main_tributary", help="Path to save the S65E forecasts.")
    parser.add_argument("PI", help="Path to the Palmer Index forecasts.")
    parser.add_argument("output", help="Path to save the trib file")

    # Parse the arguments
    args = parser.parse_args()

    # Call the function with the provided file path
    create_trib_cond(args.file_path, args.net_inflows, args.main_tributary, args.PI, args.output)


if __name__ == "__main__":
    main()