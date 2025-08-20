import sys
import os
import math
import numpy as np
import pandas as pd
import geoglows
from scipy import interpolate


SECONDS_IN_DAY = 86400


def get_bias_corrected_data(
    station_id: str,
    reach_id: str,
    observed_data_path: str,
    station_ensembles: pd.DataFrame,
    station_stats: pd.DataFrame,
    cache_path: str = None,
) -> dict:
    # Load the observed data from a CSV file
    observed_data = pd.read_csv(
        observed_data_path,
        index_col=0,
        usecols=["date", f"{station_id}_FLOW_cmd"],
    )
    # Convert the index to datetime and localize it to UTC
    observed_data.index = pd.to_datetime(observed_data.index).tz_localize(
        "UTC"
    )
    # Transform the data by dividing it by the number of seconds in a day
    observed_data = observed_data.transform(lambda x: x / SECONDS_IN_DAY)
    # Rename the value column to "Streamflow (m3/s)"
    observed_data.rename(
        columns={f"{station_id}_FLOW_cmd": "Streamflow (m3/s)"}, inplace=True
    )

    # Prepare the observed data by filling NaN values with the 10yr average
    prepared_od = prep_observed_data(observed_data)
    historical_data = geoglows.data.retro_daily(reach_id)
    # Get the historical simulation data for the given reach ID - TODO: Do we for sure want to cache the historical data?
    # I am reading the observed data that we queried earlier instead of caching it
    # historical_data = None

    # if cache_path is None:
    #     historical_data = geoglows.streamflow.historic_simulation(reach_id)
    # else:
    #     # Create the geoglows cache directory if it doesn't exist
    #     geoglows_cache_path = os.path.join(cache_path, "geoglows_cache")
    #     if not os.path.exists(geoglows_cache_path):
    #         os.makedirs(geoglows_cache_path)

    #     # Check if the historical simulation data is already cached
    #     if os.path.exists(
    #         os.path.join(
    #             geoglows_cache_path, f"{reach_id}_historic_simulation.csv"
    #         )
    #     ):
    #         historical_data = pd.read_csv(
    #             os.path.join(
    #                 geoglows_cache_path, f"{reach_id}_historic_simulation.csv"
    #             ),
    #             index_col=0,
    #         )
    #         historical_data.index = pd.to_datetime(historical_data.index)
    #     else:
    #         historical_data = geoglows.streamflow.historic_simulation(reach_id)
    #         historical_data.to_csv(
    #             os.path.join(
    #                 geoglows_cache_path, f"{reach_id}_historic_simulation.csv"
    #             )
    #         )
    # Drop 'ensemble_52' column if it exists - not necessary but we don't need it
    station_ensembles.drop(columns=['ensemble_52'], inplace=True, errors='ignore')

    # Drop all rows with any NaN values - again not necessary but we can drop them because we don't need it
    station_ensembles.dropna(inplace=True)

    # Correct the forecast bias in the station ensembles
    station_ensembles = geoglows.bias.correct_forecast(
        station_ensembles, historical_data, prepared_od
    )

    # Correct the forecast bias in the station stats
    station_stats = geoglows.bias.correct_forecast(
        station_stats, historical_data, prepared_od
    )
    #This is to clean out any infinite values that may have occurred during bias correction
    station_ensembles = station_ensembles.replace([np.inf, -np.inf], np.nan)
    station_ensembles = station_ensembles.interpolate(axis=0, limit_direction='both')

    # Fill any remaining NaNs (e.g., at column ends)
    station_ensembles = station_ensembles.ffill(axis=0).bfill(axis=0)
    station_stats = station_stats.replace([np.inf, -np.inf], np.nan)
    station_stats = station_stats.interpolate(axis=0, limit_direction='both')

    # Fill any remaining NaNs (e.g., at column ends)
    station_stats = station_stats.ffill(axis=0).bfill(axis=0)

    # Return the bias-corrected station ensembles and station stats
    return station_ensembles, station_stats


def prep_observed_data(observed_data: pd.DataFrame) -> pd.DataFrame:
    # Group the data by month and day
    grouped_data = observed_data.groupby(
        [observed_data.index.month, observed_data.index.day]
    )

    # Calculate the rolling average of 'Streamflow (m3/s)' for each group
    daily_10yr_avg = (
        grouped_data["Streamflow (m3/s)"]
        .rolling(window=10, min_periods=1, center=True)
        .mean()
    )

    # Reset the multi-index of daily_10yr_avg and sort it by index
    fill_val = daily_10yr_avg.reset_index(level=[0, 1], drop=True).sort_index()

    # Fill NaN in 'Streamflow (m3/s)' with corresponding values from fill_val
    observed_data["Streamflow (m3/s)"] = observed_data[
        "Streamflow (m3/s)"
    ].fillna(fill_val)

    # Return the modified observed_data DataFrame
    return observed_data


def bias_correct_historical(
    simulated_data: pd.DataFrame, observed_data: pd.DataFrame
) -> pd.DataFrame:
    """
    Accepts a historically simulated flow timeseries and observed flow timeseries and attempts to correct biases in the
    simulation on a monthly basis.

    Args:
        simulated_data: A dataframe with a datetime index and a single column of streamflow values
        observed_data: A dataframe with a datetime index and a single column of streamflow values

    Returns:
        pandas DataFrame with a datetime index and a single column of streamflow values
    """
    # list of the unique months in the historical simulation. should always be 1->12 but just in case...
    unique_simulation_months = sorted(set(simulated_data.index.strftime("%m")))
    dates = []
    values = []

    for month in unique_simulation_months:
        # filter historic data to only be current month
        monthly_simulated = simulated_data[
            simulated_data.index.month == int(month)
        ].dropna()
        to_prob = _flow_and_probability_mapper(
            monthly_simulated, to_probability=True
        )
        # filter the observations to current month
        monthly_observed = observed_data[
            observed_data.index.month == int(month)
        ].dropna()
        to_flow = _flow_and_probability_mapper(monthly_observed, to_flow=True)

        dates += monthly_simulated.index.to_list()
        value = to_flow(to_prob(monthly_simulated.values))
        values += value.tolist()

    corrected = pd.DataFrame(
        data=values, index=dates, columns=["Corrected Simulated Streamflow"]
    )
    corrected.sort_index(inplace=True)
    return corrected


def bias_correct_forecast(
    forecast_data: pd.DataFrame,
    simulated_data: pd.DataFrame,
    observed_data: pd.DataFrame,
    use_month: int = 0,
) -> pd.DataFrame:
    """
    Accepts a short term forecast of streamflow, simulated historical flow, and observed flow timeseries and attempts
    to correct biases in the forecasted data

    Args:
        forecast_data: A dataframe with a datetime index and any number of columns of forecasted flow. Compatible with
            forecast_stats, forecast_ensembles, forecast_records
        simulated_data: A dataframe with a datetime index and a single column of streamflow values
        observed_data: A dataframe with a datetime index and a single column of streamflow values
        use_month: Optional: either 0 for correct the forecast based on the first month of the forecast data or -1 if
            you want to correct based on the ending month of the forecast data

    Returns:
        pandas DataFrame with a copy of forecasted data with values updated in each column
    """
    # make a copy of the forecasts which we update and return so the original data is not changed
    forecast_copy = forecast_data.copy()

    # make the flow and probability interpolation functions
    monthly_simulated = simulated_data[
        simulated_data.index.month == forecast_copy.index[use_month].month
    ].dropna()
    monthly_observed = observed_data[
        observed_data.index.month == forecast_copy.index[use_month].month
    ].dropna()
    to_prob = _flow_and_probability_mapper(
        monthly_simulated, to_probability=True, extrapolate=True
    )
    to_flow = _flow_and_probability_mapper(
        monthly_observed, to_flow=True, extrapolate=True
    )

    # for each column of forecast data, make the interpolation function and update the dataframe
    for column in forecast_copy.columns:
        tmp = forecast_copy[column].dropna()
        forecast_copy.update(
            pd.DataFrame(
                to_flow(to_prob(tmp.values)), index=tmp.index, columns=[column]
            )
        )

    return forecast_copy


def _flow_and_probability_mapper(
    monthly_data: pd.DataFrame,
    to_probability: bool = False,
    to_flow: bool = False,
    extrapolate: bool = False,
) -> interpolate.interp1d:
    if not to_flow and not to_probability:
        raise ValueError(
            "You need to specify either to_probability or to_flow as True"
        )

    # get maximum value to bound histogram
    max_val = math.ceil(np.max(monthly_data.max()))
    min_val = math.floor(np.min(monthly_data.min()))

    if max_val == min_val:
        max_val += 0.1

    # determine number of histograms bins needed
    number_of_points = len(monthly_data.values)
    number_of_classes = math.ceil(1 + (3.322 * math.log10(number_of_points)))

    # specify the bin width for histogram (in m3/s)
    step_width = (max_val - min_val) / number_of_classes

    # specify histogram bins
    bins = np.arange(
        -np.min(step_width),
        max_val + 2 * np.min(step_width),
        np.min(step_width),
    )

    if bins[0] == 0:
        bins = np.concatenate((-bins[1], bins))
    elif bins[0] > 0:
        bins = np.concatenate((-bins[0], bins))

    # make the histogram
    counts, bin_edges = np.histogram(monthly_data, bins=bins)

    # adjust the bins to be the center
    bin_edges = bin_edges[1:]

    # normalize the histograms
    counts = counts.astype(float) / monthly_data.size

    # calculate the cdfs
    cdf = np.cumsum(counts)

    # Identify indices where consecutive values are the same
    duplicate_indices = np.where(np.diff(cdf) == 0)[0]

    # Adjust duplicate value to be an extrapolation of the previous value
    for idx in duplicate_indices:
        if idx > 0:
            cdf[idx] = cdf[idx - 1] + (cdf[idx + 1] - cdf[idx - 1]) / 2

    # interpolated function to convert simulated streamflow to prob
    if to_probability:
        if extrapolate:
            func = interpolate.interp1d(
                bin_edges, cdf, fill_value="extrapolate"
            )
        else:
            func = interpolate.interp1d(bin_edges, cdf)
        return lambda x: np.clip(func(x), 0, 1)
    # interpolated function to convert simulated prob to observed streamflow
    elif to_flow:
        if extrapolate:
            return interpolate.interp1d(
                cdf, bin_edges, fill_value="extrapolate"
            )
        return interpolate.interp1d(cdf, bin_edges)


if __name__ == "__main__":
    station_id = sys.argv[1]
    reach_id = sys.argv[2]
    observed_data_path = sys.argv[3].rstrip("/")
    station_ensembles = sys.argv[4]
    station_stats = sys.argv[5]

    get_bias_corrected_data(
        station_id,
        reach_id,
        observed_data_path,
        station_ensembles,
        station_stats,
    )
