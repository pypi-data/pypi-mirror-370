import sys
import os
import uuid
from datetime import datetime, timedelta
import pandas as pd
from loone_data_prep.water_quality_data import wq
from loone_data_prep.utils import find_last_date_in_csv, dbhydro_data_is_latest


D = {
    "PHOSPHATE, TOTAL AS P": {"station_ids": ['S191', 'S65E', 'S84', 'S154', 'S71', 'S72', 'S4', 'FECSR78', 'S308C',
                                              'CULV10A', 'S133', 'S127', 'S135']},
    "AMMONIA-N": {"station_ids": ['S191', 'S65E', 'S84', 'S154', 'S71', 'S72', 'S4', 'FECSR78', 'S308C',
                                  'CULV10A', 'S133', 'S127', 'S135']},
    "NITRATE+NITRITE-N": {"station_ids": ['S191', 'S65E', 'S84', 'S154', 'S71', 'S72', 'S4', 'FECSR78', 'S308C',
                                          'CULV10A', 'S133', 'S127', 'S135']},
    "TOTAL NITROGEN": {"station_ids": ['S191', 'S65E', 'S84', 'S154', 'S71', 'S72', 'S4', 'FECSR78', 'S308C',
                                       'CULV10A', 'S133', 'S127', 'S135']},
    "CHLOROPHYLL-A": {"station_ids": ['S65E', 'S84', 'S154', 'S71', 'S72', 'S4', 'FECSR78', 'S308C', 'CULV10A', 'S133',
                                      'S127', 'S135', 'S191']},
    "CHLOROPHYLL-A(LC)": {"station_ids": ['S65E', 'S84', 'S154', 'S71', 'S72', 'S4', 'FECSR78', 'S308C', 'CULV10A',
                                          'S133', 'S127', 'S135', 'S191']},
    "CHLOROPHYLL-A, CORRECTED": {"station_ids": ['S65E', 'S84', 'S154', 'S71', 'S72', 'S4', 'FECSR78', 'S308C',
                                                 'CULV10A', 'S133', 'S127', 'S135', 'S191']}
}


DEFAULT_DATE_MIN = "1950-01-01"


def main(workspace: str, d: dict = D) -> dict:
    missing_files = []
    failed_downloads = []   # List of file names that the script failed to get the latest data for (but the files still exist)
    for name, params in d.items():
        print(f"Getting {name} for the following station IDs: {params['station_ids']}.")
        
        # Get the date of the latest data in the csv file for each station id
        station_date_latest = {}
        for station_id in params["station_ids"]:
            station_date_latest[station_id] = find_last_date_in_csv(workspace, f"water_quality_{station_id}_{name}.csv")
        
        # Get the water quality data
        for station_id, date_latest in station_date_latest.items():
            # File with data for this station/name combination does NOT already exist (or possibly some other error occurred)
            if date_latest is None:
                # Get all the water quality data for the name/station combination
                print(f"Getting all {name} data for station ID: {station_id}.")
                wq.get(workspace, name, [station_id])
            else:
                # Check whether we already have the latest data
                if dbhydro_data_is_latest(date_latest):
                    # Notify that the data is already up to date
                    print(f'Downloading of new water quality data for test name: {name} station: {station} skipped. Data is already up to date.')
                    continue
                
                # Temporarily rename current data file so it isn't over written
                original_file_name = f"water_quality_{station_id}_{name}.csv"
                original_file_name_temp = f"water_quality_{station_id}_{name}_{uuid.uuid4()}.csv"
                os.rename(os.path.join(workspace, original_file_name), os.path.join(workspace, original_file_name_temp))
                
                try:
                    # Get only the water quality data that is newer than the latest data in the csv file
                    print(f"Downloading new water quality data for test name: {name} station ID: {station_id} starting from date: {date_latest}.")
                    date_latest = (datetime.strptime(date_latest, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
                    wq.get(workspace, name, [station_id], date_min=date_latest)
                    
                    # Data failed to download - It's possible the data's end date has been reached
                    if not os.path.exists(os.path.join(workspace, original_file_name)):
                        raise Exception(f"It's possible that the data for test name: {name} station ID: {station_id} has reached its end date.")
                    
                    # Read in the original data
                    df_original = pd.read_csv(os.path.join(workspace, original_file_name_temp), index_col=0)
                    
                    # Calculate the days column for the newly downloaded data
                    df_original_date_min = df_original['date'].min()
                    wq._calculate_days_column(workspace, original_file_name, df_original_date_min)
                    
                    # Read in the newly downloaded data
                    df_new = pd.read_csv(os.path.join(workspace, original_file_name), index_col=0)
                    df_new.reset_index(inplace=True)
                    
                    # Merge the new data with the original data
                    df_merged = pd.concat([df_original, df_new], ignore_index=True)
                    
                    # Write out the merged data
                    df_merged.to_csv(os.path.join(workspace, original_file_name))
                    
                    # Remove the original renamed data file
                    os.remove(os.path.join(workspace, original_file_name_temp))
                except Exception as e:
                    # Notify of the error
                    print(f"Error occurred while downloading new water quality data: {e}")
                    
                    # Remove the newly downloaded data file if it exists
                    if os.path.exists(os.path.join(workspace, original_file_name)):
                        os.remove(os.path.join(workspace, original_file_name))
                    
                    # Rename the original renamed file back to its original name
                    if os.path.exists(os.path.join(workspace, original_file_name_temp)):
                        os.rename(os.path.join(workspace, original_file_name_temp), os.path.join(workspace, original_file_name))
                    
                    # Add the file name to the list of failed downloads
                    failed_downloads.append(original_file_name)
        
        # Check for any download failures
        for station in params["station_ids"]:
            if not os.path.exists(os.path.join(workspace, f"water_quality_{station}_{name}.csv")):
                missing_files.append(f"water_quality_{station}_{name}.csv")
                print(f"{name} station ID: {station} could not be downloaded after various tries.")

    if missing_files or failed_downloads:
        error_string = ""
        
        if missing_files:
            error_string += f"The following files could not be downloaded: {missing_files}"
            
        if failed_downloads:
            error_string += f"\nThe following files could not be updated: {failed_downloads}"
            
        return {"error": error_string}

    return {"success": "Completed water quality data download."}


if __name__ == "__main__":
    workspace = sys.argv[1].rstrip("/")
    main(workspace)
