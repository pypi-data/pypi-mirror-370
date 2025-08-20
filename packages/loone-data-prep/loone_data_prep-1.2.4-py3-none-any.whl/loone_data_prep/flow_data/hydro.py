import sys
from datetime import datetime
from glob import glob
from retry import retry
import os
import pandas as pd
from rpy2.robjects import r
from rpy2.rinterface_lib.embedded import RRuntimeError


DATE_NOW = datetime.now().strftime("%Y-%m-%d")


@retry(RRuntimeError, tries=5, delay=15, max_delay=60, backoff=2)
def get(
    workspace: str,
    dbkey: str,
    date_min: str = "1990-01-01",
    date_max: str = DATE_NOW
) -> None:
    r_str = f"""
    download_flow_data <- function(workspace, dbkey, date_min, date_max) 
    {{
        # Load the required libraries
        library(dbhydroR)
        library(dplyr)

        # Retrieve data for the dbkey
        data <- get_hydro(dbkey = "{dbkey}", date_min = "{date_min}", date_max = "{date_max}", raw = TRUE)
        
        # Check if data is empty or contains only the "date" column
        if (ncol(data) <= 1) {{
            cat("No data found for dbkey", "{dbkey}", "Skipping to the next dbkey.\n")
        }}
        
        # Give data.frame correct column names so it can be cleaned using the clean_hydro function
        colnames(data) <- c("station", "dbkey", "date", "data.value", "qualifer", "revision.date")
        
        # Check if the data.frame has any rows
        if (nrow(data) == 0) 
        {{
            # No data given back, It's possible that the dbkey has reached its end date.
            print(paste("Empty data.frame returned for dbkey", "{dbkey}", "It's possible that the dbkey has reached its end date. Skipping to the next dbkey."))
            return(list(success = FALSE, dbkey = "{dbkey}"))
        }}
        
        # Add a type and units column to data so it can be cleaned using the clean_hydro function
        data$type <- "FLOW"
        data$units <- "cfs"
        
        # Get the station
        station <- data$station[1]
        
        # Clean the data.frame
        data <- clean_hydro(data)

        # Multiply all columns except "date" column by 0.0283168466 * 86400 to convert Flow rate from cfs to m³/day
        data[, -1] <- data[, -1] * (0.0283168466 * 86400)
        
        # Drop the " _FLOW_cfs" column
        data <- data %>% select(-` _FLOW_cfs`)    
        
        # Sort the data by date
        data <- data[order(data$date), ]
        
        # Get the filename for the output CSV file
        filename <- paste0(station, "_FLOW", "_{dbkey}_cmd.csv")
        
        # Save data to a CSV file
        write.csv(data, file = paste0("{workspace}/", filename))

        # Print a message indicating the file has been saved
        cat("CSV file", filename, "has been saved.\n")

        # Add a delay between requests
        Sys.sleep(1)  # Wait for 1 second before the next iteration
        
        # Return the station and dbkey to the python code
        list(success = TRUE, station = station, dbkey = "{dbkey}")
    }}
    """

    r(r_str)
    
    # Call the R function to download the flow data
    result = r.download_flow_data(workspace, dbkey, date_min, date_max)
    
    # Check for failure
    success = result.rx2("success")[0]

    if not success:
        return
    
    # Get the station name for _reformat_flow_file()
    station = result.rx2("station")[0]
    
    # Reformat the flow data file to the expected layout
    _reformat_flow_file(workspace, station, dbkey)
    
    # Check if the station name contains a space
    if " " in station:
        # Replace space with underscore in the station name
        station_previous = station
        station = station.replace(" ", "_")
        
        # Rename the file
        os.rename(f"{workspace}/{station_previous}_FLOW_{dbkey}_cmd.csv", f"{workspace}/{station}_FLOW_{dbkey}_cmd.csv")

    # column values are converted to cmd in R. This snippet makes sure column names are updated accordingly.
    file = glob(f'{workspace}/*FLOW*{dbkey}_cmd.csv')[0]
    df = pd.read_csv(file, index_col=False)
    df.columns = df.columns.astype(str).str.replace("_cfs", "_cmd")
    df.to_csv(file, index=False)


def _reformat_flow_file(workspace:str, station: str, dbkey: str):
    '''
    Reformat the flow data file to the expected layout.
    Converts the format of the dates in the file to 'YYYY-MM-DD' then sorts the data by date.
    Reads and writes to a .CSV file.
    
    Args:
        workspace (str): The path to the workspace directory.
        station (str): The station name.
        dbkey (str): The dbkey for the station.
        
    Returns:
        None
    '''
    # Read in the data
    df = pd.read_csv(f"{workspace}/{station}_FLOW_{dbkey}_cmd.csv")
    
    # Grab only the columns we need
    df = df[['date', f'{station}_FLOW_cfs']]
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'], format='%d-%b-%Y')
    
    # Sort the data by date
    df.sort_values('date', inplace=True)
    
    # Renumber the index
    df.reset_index(drop=True, inplace=True)
    
    # Drop rows that are missing values for both the date and value columns
    df = df.drop(df[(df['date'].isna()) & (df[f'{station}_FLOW_cfs'].isna())].index)
    
    # Write the updated data back to the file
    df.to_csv(f"{workspace}/{station}_FLOW_{dbkey}_cmd.csv")


if __name__ == "__main__":
    workspace = sys.argv[1].rstrip("/")
    dbkey = sys.argv[2]
    get(workspace, dbkey)
