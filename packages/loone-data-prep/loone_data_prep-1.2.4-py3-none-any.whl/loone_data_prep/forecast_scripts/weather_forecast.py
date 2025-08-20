from herbie import FastHerbie
from datetime import datetime
import pandas as pd
import openmeteo_requests
import argparse
import requests_cache
from retry_requests import retry as retry_requests
from retry import retry
import warnings
from loone_data_prep.herbie_utils import get_fast_herbie_object

warnings.filterwarnings("ignore", message="Will not remove GRIB file because it previously existed.")


def download_weather_forecast(file_path):
    # Get today's date in the required format
    today_str = datetime.today().strftime('%Y-%m-%d 00:00')

    # Define variables to download and extract
    variables = {
        "10u": "10u", 
        "ssrd": "ssrd", 
        "tp": "tp",
        "10v": "10v",
    }

    # Initialize FastHerbie
    FH = get_fast_herbie_object(today_str)
    print("FastHerbie initialized.")
    
    dfs = []

    for var_key, var_name in variables.items():
        # Download the current variable
        print(f"Processing {var_key}...")
        try:
            df = _download_herbie_variable(FH, var_key, var_name)
        except Exception as e:
            print(f"Error processing {var_key}: {e}")
            print(f'Skipping {var_key}')
            continue

        # Append to list
        if not df.empty:
            dfs.append(df)

    try:
        # Merge all variables into a single DataFrame
        final_df = dfs[0]
        for df in dfs[1:]:
            final_df = final_df.merge(df, on="datetime", how="outer")
        print(final_df)
        # Calculate wind speed
        final_df["wind_speed"] = (final_df["u10"] ** 2 + final_df["v10"] ** 2) ** 0.5

        #rainfall corrected: OLS Regression Equation: Corrected Forecast = 0.7247 * Forecast + 0.1853
        final_df["tp_corrected"] = 0.7247 * final_df["tp"] + 0.1853

        #wind speed correction: Corrected Forecast = 0.4167 * Forecast + 4.1868
        final_df["wind_speed_corrected"] = 0.4167 * final_df["wind_speed"] + 4.1868

        #radiation correction will need to be fixed because it was done on fdir instead of ssdr
        #radiation corrected: Corrected Forecast = 0.0553 * Forecast - 0.0081
        final_df["ssrd_corrected"] = 0.0553 * final_df["ssrd"] - 0.0081
    except Exception as e:
        print(f'Error correcting herbie weather data: {e}')

    try:
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry_requests(cache_session, retries = 5, backoff_factor = 0.2)
        openmeteo = openmeteo_requests.Client(session = retry_session)

        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 26.9690,
            "longitude": -80.7976,
            "hourly": "evapotranspiration",
            "forecast_days": 16,
            "models": "gfs_seamless"
        }
        responses = openmeteo.weather_api(url, params=params)


        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]

        hourly = response.Hourly()
        hourly_evapotranspiration = hourly.Variables(0).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}

        hourly_data["evapotranspiration"] = hourly_evapotranspiration

        hourly_dataframe = pd.DataFrame(data = hourly_data)

        # Convert datetime to date for merging
        final_df['date'] = final_df['datetime']
        # Ensure final_df['date'] is timezone-aware (convert to UTC)
        final_df['date'] = pd.to_datetime(final_df['date'], utc=True)

        # Ensure hourly_dataframe['date'] is also timezone-aware (convert to UTC)
        hourly_dataframe['date'] = pd.to_datetime(hourly_dataframe['date'], utc=True)

        # Merge while keeping only matching dates from final_df
        merged_df = final_df.merge(hourly_dataframe, on='date', how='left')

        # Print final combined DataFrame
        merged_df.drop(columns=['date'], inplace=True)
        # print(merged_df)

        merged_df.to_csv(file_path, index=False)
    except Exception as e:
        print(f'Error retrieving openmeteo weather data: {e}')


@retry(Exception, tries=5, delay=15, max_delay=60, backoff=2)
def _download_herbie_variable(fast_herbie_object: FastHerbie, variable_key: str, variable_name: str) -> pd.DataFrame:
    """
    Download a specific variable from the Herbie API.
    
    Args:
        fast_herbie_object: An instance of the FastHerbie class.
        variable_key: The key of the variable to download.
        variable_name: The name of the variable to download.

    Returns:
        A DataFrame containing the downloaded variable data.
        
    Example:
        df = _download_herbie_variable(FastHerbie('2020-05-16 00:00', model='ifs', fxx=range(0, 360, 3)), '10u', '10u')
    """
    # Define point of interest
    points = pd.DataFrame({"longitude": [-80.7976], "latitude": [26.9690]})
    
    # Download and load the dataset
    fast_herbie_object.download(f":{variable_key}")
    ds = fast_herbie_object.xarray(f":{variable_key}", backend_kwargs={"decode_timedelta": True})

    # Extract point data
    dsi = ds.herbie.pick_points(points, method="nearest")
    
    # Close and delete the original dataset to free up resources
    ds.close()
    del ds

    # Extract the correct variable name dynamically
    if variable_name == "10u":
        var_name_actual = "u10"  # Map 10u to u10
    elif variable_name == "10v":
        var_name_actual = "v10"  # Map 10v to v10
    else:
        var_name_actual = variable_name  # For ssrd and tp, use the same name

    # Extract time series
    time_series = dsi[var_name_actual].squeeze()

    # Convert to DataFrame
    df = time_series.to_dataframe().reset_index()

    # Convert `valid_time` to datetime
    if "valid_time" in df.columns:
        df = df.rename(columns={"valid_time": "datetime"})
    elif "step" in df.columns and "time" in dsi.coords:
        df["datetime"] = dsi.time.values[0] + df["step"]

    # Keep only datetime and variable of interest
    df = df[["datetime", var_name_actual]].drop_duplicates()

    # Print extracted data
    # print(df)
    
    # Clean up intermediate datasets to free memory
    del dsi, time_series
    
    return df


def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Download and process weather forecast data.")
    parser.add_argument("file_path", help="Path to save the resulting CSV file.")

    # Parse the arguments
    args = parser.parse_args()

    # Call the function with the provided file path
    download_weather_forecast(args.file_path)


if __name__ == "__main__":
    main()