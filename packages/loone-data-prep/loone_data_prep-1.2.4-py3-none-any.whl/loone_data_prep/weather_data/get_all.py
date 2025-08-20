import sys
from glob import glob
import uuid
import os
import pandas as pd
from loone_data_prep.weather_data import weather
from loone_data_prep.utils import find_last_date_in_csv, dbhydro_data_is_latest


D = {
    "RAIN": {"dbkeys": ["16021", "12515", "12524", "13081"]},
    "ETPI": {"dbkeys": ["UT736", "VM675", "UT743", "UT748"]},
    "H2OT": {"dbkeys": ["16031", "12518", "12527", "16267"]},
    "RADP": {"dbkeys": ["16025", "12516", "12525", "15649"]},
    "RADT": {"dbkeys": ["16024", "12512", "12522", "13080"]},
    "AIRT": {"dbkeys": ["16027", "12514", "12911", "13078"]},
    "WNDS": {"dbkeys": ["16023", "12510", "12520", "13076"]}
}


DBKEY_STATIONS = {
    "16021": "L001",
    "12515": "L005",
    "12524": "L006",
    "13081": "LZ40",
    "UT736": "L001",
    "VM675": "L005",
    "UT743": "L006",
    "UT748": "LZ40",
    "16031": "L001",
    "12518": "L005",
    "12527": "L006",
    "16267": "LZ40",
    "16025": "L001",
    "12516": "L005",
    "12525": "L006",
    "15649": "LZ40",
    "16024": "L001",
    "12512": "L005",
    "12522": "L006",
    "13080": "LZ40",
    "16027": "L001",
    "12514": "L005",
    "12911": "L006",
    "13078": "LZ40",
    "16023": "L001",
    "12510": "L005",
    "12520": "L006",
    "13076": "LZ40",
}

def main(workspace: str, d: dict = D, dbkey_stations: dict = DBKEY_STATIONS) -> dict:
    """
    Retrieves all weather data used by LOONE. When the dbkey_stations argument is provided
    the function will download only the latest data it doesn't have for the dbkeys in the d and dbkey_stations arguments.
    Otherwise, it will download all the data for the dbkeys in the d argument.
    
    Args:
        workspace (str): Path to workspace where data will be downloaded.
        d (dict): A dictionary of data type keys and dict values that hold keyword arguments to be used with weather_data.weather.get().
                  Valid keys are 'RAIN', 'ETPI', 'H2OT', 'RADP', 'RADT', 'AIRT', and 'WNDS'.
        dbkey_stations (dict): Dictionary of dbkeys mapped to their station's name.
    """
    missing_files = []
    failed_downloads = []   # List of (data type name, file name) tuples that the script failed to get the latest data for (but the files still exist)
    
    # Get the data for each data type
    for name, params in d.items():
        
        # Get the data for each dbkey individually for this data type
        for dbkey in params['dbkeys']:
            # Get the file name of the current file being downloaded
            station = dbkey_stations[dbkey]
            date_units_file, _ = weather._get_file_header_data_units(name)
            original_file_name = ""
            if name in ['RADP', 'RADT']:
                original_file_name = f"{station}_{name}.csv"
            else:
                original_file_name = f"{station}_{name}_{date_units_file}.csv"
            
            # Get the date of the latest data in the csv file
            date_latest = find_last_date_in_csv(workspace, original_file_name)
            
            # File with data for this dbkey does NOT already exist (or possibly some other error occurred)
            if date_latest is None:
                print(f"Getting all {name} data for the following dbkey: {dbkey}.")
                weather.get(workspace, name, dbkeys=[dbkey])
                continue

            # Check whether the latest data is already up to date.
            if dbhydro_data_is_latest(date_latest):
                # Notify that the data is already up to date
                print(f'Downloading of new {name} data skipped for dbkey {dbkey}. Data is already up to date.')
                continue
            
            # Temporarily rename current data file so it isn't over written
            original_file_name_temp = original_file_name.replace(".csv", f"_{uuid.uuid4()}.csv")
            os.rename(os.path.join(workspace, original_file_name), os.path.join(workspace, original_file_name_temp))
            
            try:
                # Download only the new data
                print(f'Downloading new {name} data for dbkey {dbkey} starting from date {date_latest}')
                weather.get(workspace, name, dbkeys=[dbkey], date_min=date_latest)
                
                # Data failed to download - It's possible the data's end date has been reached
                if not os.path.exists(os.path.join(workspace, original_file_name)):
                    raise Exception(f"It's possible that the data for {name} dbkey {dbkey} has reached its end date.")
                
                # Read in the original data and the newly downloaded data
                df_original = pd.read_csv(os.path.join(workspace, original_file_name_temp), index_col=0)
                df_new = pd.read_csv(os.path.join(workspace, original_file_name), index_col=0)
                
                # Merge the new data with the original data
                df_merged = pd.concat([df_original, df_new], ignore_index=True)
                
                # Write out the merged data
                df_merged.to_csv(os.path.join(workspace, original_file_name))
                
                # Remove the original renamed data file
                os.remove(os.path.join(workspace, original_file_name_temp))
            except Exception as e:
                # Notify of the error
                print(f"Error occurred while downloading new weather data: {e}")
                
                # Remove the newly downloaded data file if it exists
                if os.path.exists(os.path.join(workspace, original_file_name)):
                    os.remove(os.path.join(workspace, original_file_name))
                
                # Rename the original renamed file back to its original name
                if os.path.exists(os.path.join(workspace, original_file_name_temp)):
                    os.rename(os.path.join(workspace, original_file_name_temp), os.path.join(workspace, original_file_name))
                
                # Add the file name to the list of failed downloads
                failed_downloads.append((name, original_file_name))
        
        # Check if all the files were downloaded
        if len(glob(f"{workspace}/*{name}*.csv")) < len(params["dbkeys"]):
            missing_files.append(True)
            print(f"After various tries, files are still missing for {name}.")
        
        # Check if any files failed to update
        if len(failed_downloads) > 0:
            print(f"Failed to update the following files {failed_downloads}")
    
    # Create LAKE_RAINFALL_DATA.csv and LOONE_AVERAGE_ETPI_DATA.csv
    weather.merge_data(workspace, 'RAIN')
    weather.merge_data(workspace, 'ETPI')

    if True in missing_files:
        return {"error": "Missing files."}

    return {"success": "Completed weather data download."}


if __name__ == "__main__":
    workspace = sys.argv[1].rstrip("/")
    main(workspace)
