import sys
from retry import retry
from rpy2.robjects import r
from rpy2.rinterface_lib.embedded import RRuntimeError
import pandas as pd


@retry(RRuntimeError, tries=5, delay=15, max_delay=60, backoff=2)
def get(
    workspace, 
    date_min: str = "1972-01-01", 
    date_max: str = "2023-06-30"
) -> None:
    r(
        f"""
        # Load the required libraries
        library(dbhydroR)
        library(dplyr)
        
        # Helper Functions
        retrieve_data <- function(dbkey, date_min, date_max) 
        {{
            # Get the data from dbhydro
            df = get_hydro(dbkey = dbkey, date_min = date_min, date_max = date_max, raw = TRUE)
        
            # Give data.frame correct column names so it can be cleaned using the clean_hydro function
            colnames(df) <- c("station", "dbkey", "date", "data.value", "qualifer", "revision.date")
            
            # Add a type and units column to data so it can be cleaned using the clean_hydro function
            df$type <- "FLOW"
            df$units <- "cfs"
            
            # Clean the data.frame
            df <- clean_hydro(df)
            
            # Drop the " _FLOW_cfs" column
            df <- df %>% select(-` _FLOW_cfs`)
            
            # Convert Flow rate from cfs to m³/day
            df[, -1] <- df[, -1] * (0.0283168466 * 86400)
            
            # Return resulting data.frame
            return(df)
        }}
        
        # S65E_S
        S65E_S <- retrieve_data(dbkey = "91656", date_min = "{date_min}", date_max = "{date_max}")
        
        # Wait five seconds before next request to avoid "too many requests" error
        Sys.sleep(5)
        
        # S65EX1_S
        S65EX1_S <- retrieve_data(dbkey = "AL760", date_min = "{date_min}", date_max = "{date_max}")
        
        # Merge the data from each dbkey
        result <- merge(S65E_S, S65EX1_S, by = "date", all = TRUE)
        
        # Write the data to a file
        write.csv(result, file = '{workspace}/S65E_total.csv')
        """
    )
    
    _reformat_s65e_total_file(workspace)

def _reformat_s65e_total_file(workspace: str):
    # Read in the data
    df = pd.read_csv(f"{workspace}/S65E_total.csv")
    
    # Drop unused columns
    df.drop('Unnamed: 0', axis=1, inplace=True)
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'], format='%d-%b-%Y')
    
    # Sort the data by date
    df.sort_values('date', inplace=True)
    
    # Renumber the index
    df.reset_index(drop=True, inplace=True)
    
    # Drop rows that are missing all their values
    df.dropna(how='all', inplace=True)
    
    # Write the updated data back to the file
    df.to_csv(f"{workspace}/S65E_total.csv")

if __name__ == "__main__":
    workspace = sys.argv[1].rstrip("/")
    get(workspace)
