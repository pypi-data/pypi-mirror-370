import sys
import os
from glob import glob
from datetime import datetime
import uuid
import pandas as pd
from loone_data_prep.flow_data import hydro, S65E_total
from loone_data_prep.utils import find_last_date_in_csv, dbhydro_data_is_latest


# Database keys for needed inflow data mapped to their stations
DBKEYS = {
    "91370": "S127_C",
    "91371": "S127_P",
    "91373": "S129_C",
    "91377": "S133_P",
    "91379": "S135_C",
    "91401": "S154_C",
    "91429": "S191_S",
    "91473": "S2_P",
    "91508": "S351_S",
    "91510": "S352_S",
    "91513": "S354_S",
    "91599": "S3_P",
    "91608": "S4_P",
    "91656": "S65E_S",
    "91668": "S71_S",
    "91675": "S72_S",
    "91687": "S84_S",
    "15627": "FISHP",
    "15640": "L8.441",
    "15626": "S308.DS",
    "15642": "S129 PMP_P",
    "15638": "S135 PMP_P",
}

def main(workspace: str, dbkeys: dict = DBKEYS) -> dict:
    """
    Retrieve the inflows data used by LOONE. 
    
    Args:
        workspace (str): Path to workspace where data will be downloaded.
        dbkeys (dict): Dictionary of dbkeys and corresponding station names.
        
    Returns:
        dict: Success or error message
    """
    
    # Retrieve inflow data
    for dbkey, station in dbkeys.copy().items():
        file_name = f"{station}_FLOW_cmd.csv"
        date_latest = find_last_date_in_csv(workspace, file_name)
        
        # File with data for this dbkey does NOT already exist (or possibly some other error occurred)
        if date_latest is None:
            # Download all the data
            print(f'Downloading all inflow data for {station}')
            hydro.get(workspace, dbkey)
        else:
            # Check whether the latest data is already up to date.
            if dbhydro_data_is_latest(date_latest):
                # Notify that the data is already up to date
                print(f'Downloading of new inflow data skipped for Station {station} (dbkey: {dbkey}). Data is already up to date.')
                
                # Remove dbkey from dbkeys so we know it didn't fail
                del dbkeys[dbkey]
                continue
            
            # Download only the new data
            print(f'Downloading new inflow data for {station} starting from date {date_latest}')
            hydro.get(workspace, dbkey, date_latest)
            
            # Make sure both our original data and newly downloaded data exist
            df_original_path = os.path.join(workspace, f"{station}_FLOW_cmd.csv")
            df_new_path = os.path.join(workspace, f"{station}_FLOW_{dbkey}_cmd.csv")
            
            if os.path.exists(df_original_path) and os.path.exists(df_new_path):
                # Merge the new data with the old data
                df_original = pd.read_csv(df_original_path, index_col=0)
                df_new = pd.read_csv(df_new_path, index_col=0)
                df_merged = pd.concat([df_original, df_new], ignore_index=True)
                
                # Write the merged data to the new file
                df_merged.to_csv(os.path.join(workspace, f"{station}_FLOW_{dbkey}_cmd.csv"))
                
                # Remove the old file
                os.remove(os.path.join(workspace, f"{station}_FLOW_cmd.csv"))

    # Download S65E_total.csv Data
    date_latest = find_last_date_in_csv(workspace, "S65E_total.csv")

    if date_latest is None:
        print('Downloading all S65E_total data')
        S65E_total.get(workspace, date_max=datetime.now().strftime("%Y-%m-%d"))
    else:
        # Check whether the latest data is already up to date.
        if dbhydro_data_is_latest(date_latest):
            # Notify that the data is already up to date
            print(f'Downloading of new inflow data skipped for S65E_total. Data is already up to date.')
        else:
            # Temporarily rename current data file so it isn't over written
            original_file_name = F"S65E_total_old_{uuid.uuid4()}.csv"
            os.rename(os.path.join(workspace, "S65E_total.csv"), os.path.join(workspace, original_file_name))
            
            try:
                # Download only the new data
                print(f'Downloading new S65E_total data starting from date {date_latest}')
                S65E_total.get(workspace, date_min=date_latest, date_max=datetime.now().strftime("%Y-%m-%d"))
                
                # Merge the new data with the original data
                df_original = pd.read_csv(os.path.join(workspace, original_file_name), index_col=0)
                df_new = pd.read_csv(os.path.join(workspace, "S65E_total.csv"), index_col=0)
                df_merged = pd.concat([df_original, df_new], ignore_index=True)
                
                # Write out the merged data
                df_merged.to_csv(os.path.join(workspace, original_file_name))
                
                # Remove the newly downloaded data file
                os.remove(os.path.join(workspace, "S65E_total.csv"))
            except Exception as e:
                print(f"Error occurred while downloading new S65E_total data: {e}")
            finally:
                # Rename the original updated file back to its original name
                os.rename(os.path.join(workspace, original_file_name), os.path.join(workspace, "S65E_total.csv"))
                
    # Check if all files were downloaded
    files = glob(f"{workspace}/*FLOW*_cmd.csv")

    for file in files:
        file_dbkey = file.split("_")[-2]

        if file_dbkey in dbkeys:
            # Remove dbkey from file name
            new_file_name = file.replace(f"_{file_dbkey}", "")
            os.rename(file, new_file_name)

            # Remove dbkey from dbkeys so we know it successfully downloaded
            del dbkeys[file_dbkey]
    
    # Check for failed downloads
    if len(dbkeys) > 0 or not os.path.exists(f"{workspace}/S65E_total.csv"):
        error_message = ""
        
        # dbkeys
        if len(dbkeys) > 0:
            error_message += f"The data from the following dbkeys could not be downloaded: {list(dbkeys.keys())}\n"
        
        # S65E_total.csv
        if not os.path.exists(f"{workspace}/S65E_total.csv"):
            error_message += "S65E_total.csv file could not be downloaded.\n"
        
        return {"error": error_message}

    return {"success": "Completed inflow flow data download."}


if __name__ == "__main__":
    workspace = sys.argv[1].rstrip("/")
    main(workspace)
