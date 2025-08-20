import sys
from datetime import datetime
from retry import retry
from rpy2.robjects import r
from rpy2.rinterface_lib.embedded import RRuntimeError
import pandas as pd

DEFAULT_DBKEYS = ["16022", "12509", "12519", "16265", "15611"]
DATE_NOW = datetime.now().strftime("%Y-%m-%d")


@retry(RRuntimeError, tries=5, delay=15, max_delay=60, backoff=2)
def get(
    workspace: str,
    name: str,
    dbkeys: list = DEFAULT_DBKEYS,
    date_min: str = "1950-01-01",
    date_max: str = DATE_NOW,
    datum: str = "",
    **kwargs: str | list
) -> None:
    # Get the type and units for the station
    data_type = "STG"
    units = "ft NGVD29"
    
    if name in ["Stg_3A3", "Stg_2A17", "Stg_3A4", "Stg_3A28"]:
        data_type = "GAGHT"
        units = "feet"
    
    dbkeys_str = "\"" + "\", \"".join(dbkeys) + "\""
    r(
        f"""
        # Load the required libraries
        library(rio)
        library(dbhydroR)
        library(dplyr)
        
        # Stage Data
        if ("{datum}" == "")
        {{
            {name} <- get_hydro(dbkey = c({dbkeys_str}), date_min = "{date_min}", date_max = "{date_max}", raw = TRUE)
        }}
        
        if (nchar("{datum}") > 0)
        {{
            {name} <- get_hydro(dbkey = c({dbkeys_str}), date_min = "{date_min}", date_max = "{date_max}", raw = TRUE, datum = "{datum}")
        }}
        
        # Give data.frame correct column names so it can be cleaned using the clean_hydro function
        colnames({name}) <- c("station", "dbkey", "date", "data.value", "qualifer", "revision.date")
        
        # Check if the data.frame has any rows
        if (nrow({name}) == 0) 
        {{
            # No data given back, It's possible that the dbkey has reached its end date.
            print(paste("Empty data.frame returned for dbkeys", "{dbkeys}", "It's possible that the dbkey has reached its end date. Skipping to the next dbkey."))
            return(list(success = FALSE, dbkey = "{dbkeys}"))
        }}
        
        # Get the station
        station <- {name}$station[1]
        
        # Add a type and units column to data so it can be cleaned using the clean_hydro function
        {name}$type <- "{data_type}"
        {name}$units <- "{units}"
        
        # Clean the data.frame
        {name} <- clean_hydro({name})
        
        # Drop the " _STG_ft NGVD29" column
        {name} <- {name} %>% select(-` _{data_type}_{units}`)
        
        # Write the data to a csv file
        write.csv({name},file ='{workspace}/{name}.csv')
        """
    )
    
    _reformat_water_level_file(workspace, name)

def _reformat_water_level_file(workspace: str, name: str):
    # Read in the data
    df = pd.read_csv(f"{workspace}/{name}.csv")
    
    # Drop the "Unnamed: 0" column
    df.drop(columns=['Unnamed: 0'], inplace=True)
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'], format='%d-%b-%Y')
    
    # Sort the data by date
    df.sort_values('date', inplace=True)
    
    # Renumber the index
    df.reset_index(drop=True, inplace=True)
    
    # Drop rows that are missing all their values
    df.dropna(how='all', inplace=True)
    
    # Write the updated data back to the file
    df.to_csv(f"{workspace}/{name}.csv")

if __name__ == "__main__":
    args = [sys.argv[1].rstrip("/"), sys.argv[2]]
    if len(sys.argv) >= 4:
        dbkeys = sys.argv[3].strip("[]").replace(" ", "").split(',')
        args.append(dbkeys)
    if len(sys.argv) >= 5:
        date_min = sys.argv[4]
        args.append(date_min)
    if len(sys.argv) >= 6:
        date_max = sys.argv[5]
        args.append(date_max)

    get(*args)
