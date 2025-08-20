import os
from herbie import FastHerbie
from datetime import datetime
import pandas as pd
from retry_requests import retry as retry_requests
from retry import retry
import warnings
from typing import Tuple
from loone_data_prep.herbie_utils import get_fast_herbie_object


def generate_wind_forecasts(output_dir):
    # Ensure output directory exists
    warnings.filterwarnings("ignore", message="Will not remove GRIB file because it previously existed.")
    os.makedirs(output_dir, exist_ok=True)

    # Define points of interest
    points = pd.DataFrame({
        "longitude": [-80.7934, -80.9724, -80.7828, -80.7890],
        "latitude": [27.1389, 26.9567, 26.8226, 26.9018]
    })

    # Station-specific file and column names
    file_map = {
        "Point_1": ("L001_WNDS_MPH_predicted.csv", "L001_WNDS_MPH"),
        "Point_2": ("L005_WNDS_MPH_predicted.csv", "L005_WNDS_MPH"),
        "Point_3": ("L006_WNDS_MPH_predicted.csv", "L006_WNDS_MPH"),
        "Point_4": ("LZ40_WNDS_MPH_predicted.csv", "LZ40_WNDS_MPH")
    }

    today_str = datetime.today().strftime('%Y-%m-%d 00:00')
    FH = get_fast_herbie_object(today_str)
    print("FastHerbie initialized.")
    dfs = []

    variables = {
        "10u": "10u",
        "10v": "10v",
        "2t": "2t",
        
    }

    # Loop through points and extract data
    for index, point in points.iterrows():
        print(f"\nProcessing Point {index + 1}: ({point.latitude}, {point.longitude})")

        point_df = pd.DataFrame({
            "longitude": [point.longitude],
            "latitude": [point.latitude]
        })

        # Loop through variables for current point and extract data
        for var_key, var_name in variables.items():
            # Get the current variable data at the current point
            print(f"  Variable: {var_key}")
            try:
                df, var_name_actual = _download_herbie_variable(FH, var_key, var_name, point_df)
            except Exception as e:
                print(f"Error processing {var_key} for Point {index + 1} ({point.latitude}, {point.longitude}): {e}")
                print(f'Skipping {var_key}')
                continue

            # Append the DataFrame and variable name to the list
            if not df.empty:
                dfs.append((index, var_name_actual, df))

    # Merge and process data per point
    results = {}
    for point_index in range(len(points)):
        u_df = [df for idx, name, df in dfs if idx == point_index and name == "u10"][0]
        v_df = [df for idx, name, df in dfs if idx == point_index and name == "v10"][0]
        merged = u_df.merge(v_df, on="datetime", how="outer")

        # Compute wind speed and correction
        merged["wind_speed"] = (merged["u10"] ** 2 + merged["v10"] ** 2) ** 0.5
        merged["wind_speed_corrected"] = 0.4167 * merged["wind_speed"] + 4.1868
        merged["wind_speed_corrected"] = merged["wind_speed_corrected"] * 2.23694  # m/s to mph

        results[f"Point_{point_index + 1}"] = merged

    # Save outputs with station-specific column names
    for key, (filename, new_col_name) in file_map.items():
        df = results[key].copy()
        df = df[["datetime", "wind_speed_corrected"]].rename(columns={
            "wind_speed_corrected": new_col_name,
            "datetime": "date"
        })
        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath, index=False)
    # Save 2-meter air temperature data
    airt_file_map = {
        "Point_1": "L001_AIRT_Degrees Celsius_forecast.csv",
        "Point_2": "L005_AIRT_Degrees Celsius_forecast.csv",
        "Point_3": "L006_AIRT_Degrees Celsius_forecast.csv",
        "Point_4": "LZ40_AIRT_Degrees Celsius_forecast.csv"
    }
    airt_column_map = {
        "Point_1": "L001_AIRT_Degrees Celsius",
        "Point_2": "L005_AIRT_Degrees Celsius",
        "Point_3": "L006_AIRT_Degrees Celsius",
        "Point_4": "LZ40_AIRT_Degrees Celsius"
    }

    for key in airt_file_map:
        point_index = int(key.split("_")[1]) - 1
        df_airt = [df for idx, name, df in dfs if idx == point_index and name == "t2m"][0].copy()
        df_airt["t2m"] = df_airt["t2m"] - 273.15  # Convert from Kelvin to Celsius
        df_airt = df_airt.rename(columns={
            "datetime": "date",
            "t2m": airt_column_map[key]
        })
        filepath = os.path.join(output_dir, airt_file_map[key])
        df_airt.to_csv(filepath, index=False)


@retry(Exception, tries=5, delay=15, max_delay=60, backoff=2)
def _download_herbie_variable(fast_herbie_object: FastHerbie, variable_key: str, variable_name: str, point_df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """
    Download a specific variable from the Herbie API.
    
    Args:
        fast_herbie_object: An instance of the FastHerbie class.
        variable_key: The key of the variable to download.
        variable_name: The name of the variable to download.
        point_df: A DataFrame containing the point of interest (longitude and latitude).

    Returns:
        A DataFrame containing the downloaded variable data.
        
    Example:
        point_df = pd.DataFrame({"longitude": [-80.7934], "latitude": [27.1389]})
        df, var_name_actual = _download_herbie_variable(FastHerbie('2020-05-16 00:00', model='ifs', fxx=range(0, 360, 3)), '10u', '10u', point_df)
    """
    # Download and load dataset
    fast_herbie_object.download(f":{variable_key}")
    ds = fast_herbie_object.xarray(f":{variable_key}", backend_kwargs={"decode_timedelta": True})

    # Extract point data
    dsi = ds.herbie.pick_points(point_df, method="nearest")

    # Close and delete the original dataset to free up resources
    ds.close()
    del ds

    # Get actual variable name
    if variable_name == "10u":
        var_name_actual = "u10"  # Map 10u to u10
    elif variable_name == "10v":
        var_name_actual = "v10"  # Map 10v to v10
    elif variable_name == "2t":
        var_name_actual = "t2m" #TODO: check that this is correct

    # Convert to DataFrame
    time_series = dsi[var_name_actual].squeeze()
    df = time_series.to_dataframe().reset_index()

    # Handle datetime columns
    if "valid_time" in df.columns:
        df = df.rename(columns={"valid_time": "datetime"})
    elif "step" in df.columns and "time" in dsi.coords:
        df["datetime"] = dsi.time.values[0] + df["step"]

    # Close and delete the intermediate dataset to free memory
    dsi.close()
    del dsi, time_series

    # Retain necessary columns
    df = df[["datetime", var_name_actual]].drop_duplicates()
    
    return df, var_name_actual
