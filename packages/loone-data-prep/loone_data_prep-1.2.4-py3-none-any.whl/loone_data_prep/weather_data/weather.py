import sys
from datetime import datetime
from retry import retry
from rpy2.robjects import r
from rpy2.rinterface_lib.embedded import RRuntimeError
import pandas as pd


DEFAULT_DBKEYS = ["16021", "12515", "12524", "13081"]
DATE_NOW = datetime.now().strftime("%Y-%m-%d")


@retry(RRuntimeError, tries=5, delay=15, max_delay=60, backoff=2)
def get(
    workspace: str,
    param: str,
    dbkeys: list = DEFAULT_DBKEYS,
    date_min: str = "2000-01-01",
    date_max: str = DATE_NOW,
    **kwargs: str | list
) -> None:
    dbkeys_str = "\"" + "\", \"".join(dbkeys) + "\""

    data_type = param
    data_units_file = None
    data_units_header = None
    
    # Get the units for the file name and column header based on the type of data
    data_units_file, data_units_header = _get_file_header_data_units(data_type)
    
    r_str = f"""
        download_weather_data <- function()#workspace, dbkeys, date_min, date_max, data_type, data_units_file, data_units_header)
        {{
            library(dbhydroR)
            library(dplyr)

            dbkeys <- c({dbkeys_str})
            successful_stations <- list()
            
            for (i in dbkeys) 
            {{
                # Retrieve data for the dbkey
                data <- get_hydro(dbkey = i, date_min = "{date_min}", date_max = "{date_max}", raw = TRUE)
                
                # Give data.frame correct column names so it can be cleaned using the clean_hydro function
                column_names <- c("station", "dbkey", "date", "data.value", "qualifer", "revision.date")
                colnames(data) <- column_names
                
                # Check if the data.frame has any rows
                if (nrow(data) > 0) 
                {{
                    # Get the station
                    station <- data$station[1]
                    
                    # Add a type and units column to data so it can be cleaned using the clean_hydro function
                    data$type <- "{data_type}"
                    data$units <- "{data_units_header}"
                    
                    # Clean the data.frame
                    data <- clean_hydro(data)
                    
                    # Get the filename of the output file
                    filename <- ""
                    
                    if ("{param}" %in% c("RADP", "RADT")) 
                    {{
                        filename <- paste(station, "{data_type}", sep = "_")
                    }}
                    else
                    {{
                        filename <- paste(station, "{data_type}", "{data_units_file}", sep = "_")
                    }}
                    
                    filename <- paste0(filename, ".csv")
                    filename <- paste0("{workspace}/", filename)

                    # Save data to a CSV file
                    write.csv(data, file = filename)

                    # Print a message indicating the file has been saved
                    cat("CSV file", filename, "has been saved.\n")

                    # Append the station to the list of successful stations
                    successful_stations <- c(successful_stations, station)
                }}
                else
                {{
                    # No data given back, It's possible that the dbkey has reached its end date.
                    print(paste("Empty data.frame returned for dbkey", i, "It's possible that the dbkey has reached its end date. Skipping to the next dbkey."))
                }}

                # Add a delay between requests
                Sys.sleep(2) # Wait for 2 seconds before the next iteration
            }}
            
            # Return the station and dbkey to the python code
            return(successful_stations)
        }}
        """  # noqa: E501
    
    # Download the weather data
    r(r_str)
    result = r.download_weather_data()
    
    # Get the stations of the dbkeys who's data were successfully downloaded
    stations = []
    for value in result:
        stations.append(value[0])
    
    # Format files to expected layout
    for station in stations:
        if station in ["L001", "L005", "L006", "LZ40"]:
            _reformat_weather_file(workspace, station, data_type, data_units_file, data_units_header)
            
            # Print a message indicating the file has been saved
            print(f"CSV file {workspace}/{station}_{data_type}_{data_units_file}.csv has been reformatted.")


def merge_data(workspace: str, data_type: str):
    """
    Merge the data files for the different stations to create either the LAKE_RAINFALL_DATA.csv or LOONE_AVERAGE_ETPI_DATA.csv file.
    
    Args:
        workspace (str): The path to the workspace directory.
        data_type (str): The type of data. Either 'RAIN' for LAKE_RAINFALL_DATA.csv or 'ETPI' for LOONE_AVERAGE_ETPI_DATA.csv.
    """
    
    # Merge the data files for the different stations (LAKE_RAINFALL_DATA.csv)
    if data_type == "RAIN":
        r(
            f"""
            L001_RAIN_Inches <- read.csv("{workspace}/L001_RAIN_Inches.csv", colClasses = c("NULL", "character", "numeric"))
            L005_RAIN_Inches = read.csv("{workspace}/L005_RAIN_Inches.csv", colClasses = c("NULL", "character", "numeric"))
            L006_RAIN_Inches = read.csv("{workspace}/L006_RAIN_Inches.csv", colClasses = c("NULL", "character", "numeric"))
            LZ40_RAIN_Inches = read.csv("{workspace}/LZ40_RAIN_Inches.csv", colClasses = c("NULL", "character", "numeric"))
            #Replace NA values with zero
            L001_RAIN_Inches[is.na(L001_RAIN_Inches)] <- 0
            L005_RAIN_Inches[is.na(L005_RAIN_Inches)] <- 0
            L006_RAIN_Inches[is.na(L006_RAIN_Inches)] <- 0
            LZ40_RAIN_Inches[is.na(LZ40_RAIN_Inches)] <- 0
            # Merge the files by the "date" column
            merged_data <- merge(L001_RAIN_Inches, L005_RAIN_Inches, by = "date",all = TRUE)
            merged_data <- merge(merged_data, L006_RAIN_Inches, by = "date",all = TRUE)
            merged_data <- merge(merged_data, LZ40_RAIN_Inches, by = "date",all = TRUE)
            # Calculate the average rainfall per day
            merged_data$average_rainfall <- rowMeans(merged_data[, -1],na.rm = TRUE)

            # View the updated merged data
            head(merged_data)
            # Save merged data as a CSV file
            write.csv(merged_data, "{workspace}/LAKE_RAINFALL_DATA.csv", row.names = TRUE)
            """  # noqa: E501
        )

    # Merge the data files for the different stations (LOONE_AVERAGE_ETPI_DATA.csv)
    if data_type == "ETPI":
        r(
            f"""
            L001_ETPI_Inches <- read.csv("{workspace}/L001_ETPI_Inches.csv", colClasses = c("NULL", "character", "numeric"))
            L005_ETPI_Inches = read.csv("{workspace}/L005_ETPI_Inches.csv", colClasses = c("NULL", "character", "numeric"))
            L006_ETPI_Inches = read.csv("{workspace}/L006_ETPI_Inches.csv", colClasses = c("NULL", "character", "numeric"))
            LZ40_ETPI_Inches = read.csv("{workspace}/LZ40_ETPI_Inches.csv", colClasses = c("NULL", "character", "numeric"))

            # Replace NA values with zero
            L001_ETPI_Inches[is.na(L001_ETPI_Inches)] <- 0
            L005_ETPI_Inches[is.na(L005_ETPI_Inches)] <- 0
            L006_ETPI_Inches[is.na(L006_ETPI_Inches)] <- 0
            LZ40_ETPI_Inches[is.na(LZ40_ETPI_Inches)] <- 0
            # Merge the files by the "date" column
            merged_data <- merge(L001_ETPI_Inches, L005_ETPI_Inches, by = "date",all = TRUE)
            merged_data <- merge(merged_data, L006_ETPI_Inches, by = "date",all = TRUE)
            merged_data <- merge(merged_data, LZ40_ETPI_Inches, by = "date",all = TRUE)
            # Calculate the average rainfall per day
            merged_data$average_ETPI <- rowMeans(merged_data[, -1],na.rm = TRUE)

            # View the updated merged data
            head(merged_data)
            # Save merged data as a CSV file
            write.csv(merged_data, "{workspace}/LOONE_AVERAGE_ETPI_DATA.csv", row.names = TRUE)
            """  # noqa: E501
        )


def _reformat_weather_file(workspace: str, station: str, data_type: str, data_units_file: str, data_units_header: str) -> None:
    '''
    Reformats the dbhydro weather file to the layout expected by the rest of the LOONE scripts.
    This function reads in and writes out a .csv file.
    
    Args:
        workspace (str): The path to the workspace directory.
        station (str): The station name. Ex: L001, L005, L006, LZ40.
        data_type (str): The type of data. Ex: RAIN, ETPI, H2OT, RADP, RADT, AIRT, WNDS.
        data_units_file (str): The units for the file name. Ex: Inches, Degrees Celsius, etc.
        data_units_header (str): The units for the column header. Ex: Inches, Degrees Celsius, etc. Can differ from data_units_file when data_type is either RADP or RADT.
        
    Returns:
        None
    '''
    # Read in the data
    df = None
    if data_type in ['RADP', 'RADT']:
        df = pd.read_csv(f"{workspace}/{station}_{data_type}.csv")
    else:
        df = pd.read_csv(f"{workspace}/{station}_{data_type}_{data_units_file}.csv")
    
    # Remove unneeded column columns
    df.drop(f' _{data_type}_{data_units_header}', axis=1, inplace=True)
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
    if data_type in ['RADP', 'RADT']:
        df.to_csv(f"{workspace}/{station}_{data_type}.csv")
    else:
        df.to_csv(f"{workspace}/{station}_{data_type}_{data_units_file}.csv")


def _get_file_header_data_units(data_type: str) -> tuple[str, str]:
    """
    Retrieves the units of measurement for a given environmental data type to be used in file names and column headers.

    This function maps a specified environmental data type to its corresponding units of measurement. 
    These units are used for naming files and for the column headers within those files. 

    Args:
        data_type (str): The type of environmental data for which units are being requested. Supported types include "RAIN", "ETPI", "H2OT", "RADP", "RADT", "AIRT", and "WNDS".

    Returns:
        tuple[str, str]: A tuple containing two strings. The first string represents the unit of measurement for the file name, and the second string represents the unit of measurement for the column header in the data file.
    """
    # Get the units for the file name and column header based on the type of data
    if data_type == "RAIN":
        data_units_file = "Inches"
        data_units_header = "Inches"
    elif data_type == "ETPI":
        data_units_file = "Inches"
        data_units_header = "Inches"
    elif data_type == "H2OT":
        data_units_file = "Degrees Celsius"
        data_units_header = "Degrees Celsius"
    elif data_type == "RADP":
        data_units_file = ""
        data_units_header = "MICROMOLE/m^2/s"
    elif data_type == "RADT":
        data_units_file = ""
        data_units_header = "kW/m^2"
    elif data_type == "AIRT":
        data_units_file = "Degrees Celsius"
        data_units_header = "Degrees Celsius"
    elif data_type == "WNDS":
        data_units_file = "MPH"
        data_units_header = "MPH"
        
    return data_units_file, data_units_header


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
