import sys
import os
from glob import glob
import pandas as pd
from loone_data_prep.utils import get_dbkeys, find_last_date_in_csv, dbhydro_data_is_latest
from loone_data_prep.flow_data import hydro

STATION_IDS = [
    "S308.DS",
    "S77_S",
    "L8.441",
    "S127_C",
    "S129_C",
    "S135_C",
    "S351_S",
    "S352_S",
    "S354_S",
    "INDUST",
    "S79",
    "S80_S",
    "S2_NNR",
    "S3",
    "S48_S",
    "S49_S",
]


DBKEYS = {
    "91370": "S127_C",
    "91373": "S129_C",
    "91379": "S135_C",
    "91508": "S351_S",
    "91510": "S352_S",
    "91513": "S354_S",
    "91677": "S77_S",
    "15628": "INDUST",
    "15640": "L8.441",
    "15626": "S308.DS",
    "00865": "S79_TOT",
    "JW224": "S80_S",
    "00436": "S2 NNR",
    "15018": "S3",
    "91606": "S48_S",
    "JW223": "S49_S",
}


def _get_outflow_data_from_station_ids(workspace: str, station_ids: list) -> dict:
    """Attempt to download outflow data from station ids.
    
    Args:
        workspace (str): Path to workspace where data will be downloaded.
        station_ids (list): List of station ids to download data for.
        
    Returns:
        dict: Success or error message
    """
    # Get dbkeys from station ids
    dbkeys = list(get_dbkeys(station_ids, "SW", "FLOW", "MEAN", "PREF", detail_level="dbkey"))
    dbkeys.extend(list(get_dbkeys(station_ids, "SW", "FLOW", "MEAN", "DRV", detail_level="dbkey")))

    for dbkey in dbkeys:
        hydro.get(workspace, dbkey, "2000-01-01")

    # Check if all files were downloaded
    files = glob(f"{workspace}/*FLOW*_cmd.csv")

    for file in files:
        file_dbkey = file.split("_")[-2]

        if file_dbkey in dbkeys:
            # Remove dbkey from file name
            new_file_name = file.replace(f"_{file_dbkey}", "")
            os.rename(file, new_file_name)

            # Remove dbkey from dbkeys so we know it successfully downloaded
            dbkeys.remove(file_dbkey)

    if len(dbkeys) > 0:
        return {"error": f"The data from the following dbkeys could not be downloaded: {dbkeys}"}

    return {"success": "Completed outflow flow data download."}


def main(workspace: str, dbkeys: dict = DBKEYS, station_ids: list = STATION_IDS) -> dict:
    """
    Retrieve the outflow data used by LOONE. 
    
    Args:
        workspace (str): Path to workspace where data will be downloaded.
        dbkeys (dict): Dictionary of dbkeys and corresponding station names.
        station_ids (list): List of station ids to download data for if the dbkeys argument is not provided.
        
    Returns:
        dict: Success or error message
    """
    
    # No dbkeys given, attempt to get data from station ids
    if dbkeys is None:
        return _get_outflow_data_from_station_ids(workspace, station_ids)

    # Get outflow data from dbkeys
    for dbkey, station in dbkeys.copy().items():
        # Get the date of the latest data in the csv file (if any)
        date_latest = find_last_date_in_csv(workspace, f"{station}_FLOW_cmd.csv")
        
        # File with data for this dbkey does NOT already exist (or possibly some other error occurred)
        if date_latest is None:
            # Download all data
            print(f'Downloading all outflow data for {station}')
            hydro.get(workspace, dbkey, "2000-01-01")
        else:
            # Check whether the latest data is already up to date.
            if dbhydro_data_is_latest(date_latest):
                # Notify that the data is already up to date
                print(f'Downloading of new outflow data skipped for Station {station} (dbkey: {dbkey}). Data is already up to date.')
                
                # Remove dbkey from dbkeys so we know it didn't fail
                del dbkeys[dbkey]
                continue
            
            # Download only the new data
            print(f'Downloading new outflow data for {station} starting from date {date_latest}')
            hydro.get(workspace, dbkey, date_latest)
            
            # Make sure both our original data and newly downloaded data exist
            df_old_path = os.path.join(workspace, f"{station}_FLOW_cmd.csv")
            df_new_path = os.path.join(workspace, f"{station}_FLOW_{dbkey}_cmd.csv")
            
            if os.path.exists(df_old_path) and os.path.exists(df_new_path):
                # Merge the new data with the old data
                df_original = pd.read_csv(df_old_path, index_col=0)
                df_new = pd.read_csv(df_new_path, index_col=0)
                df_merged = pd.concat([df_original, df_new], ignore_index=True)
                
                # Write the merged data to the new file
                df_merged.to_csv(os.path.join(workspace, f"{station}_FLOW_{dbkey}_cmd.csv"))
                
                # Remove the old file
                os.remove(os.path.join(workspace, f"{station}_FLOW_cmd.csv"))

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

    if len(dbkeys) > 0:
        return {"error": f"The data from the following dbkeys could not be downloaded: {dbkeys}"}

    return {"success": "Completed outflow flow data download."}


if __name__ == "__main__":
    workspace = sys.argv[1].rstrip("/")
    main(workspace)
