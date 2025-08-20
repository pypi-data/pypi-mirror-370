import pandas as pd
def loads_predicted(input_dir, output_dir):
    """
    Calculate Chlorophyll-a loads based on inflows and chlorophyll-a data.
    
    input_dir: Directory where the input files are located.
    output_dir: Directory where the output files will be saved.
    St_Yr, St_M, St_D: Start date (year, month, day).
    En_Yr, En_M, En_D: End date (year, month, day).
    """
    
    # Read forecast inflow file
    # TODO: Should this be an average/median of all of the ensembles? worst case?
    Flow_df = pd.read_csv(f"{input_dir}/geoglows_flow_df_ens_01_predicted.csv")
    Flow_df['date'] = pd.to_datetime(Flow_df['date'])

    
    # Read S65E Chlorophyll-a data
    S65E_Chla = pd.read_csv(f'{output_dir}/S65E_Chla_Merged_forecast.csv')
    S65E_Chla['date'] = pd.to_datetime(S65E_Chla['date'])  # Ensure date column is datetime
    # Merge on date
    merged = pd.merge(Flow_df[['date', 'Inflows']], S65E_Chla[['date', 'Data']], on='date', how='inner')
    # Calculate Chlorophyll-a loads
    merged['Chla_Loads'] = merged['Inflows'] * merged['Data']
    # Save results
    Chla_Loads_In = merged[['date', 'Chla_Loads']]
    Chla_Loads_In.to_csv(f'{output_dir}/Chla_Loads_In_forecast.csv', index=False)