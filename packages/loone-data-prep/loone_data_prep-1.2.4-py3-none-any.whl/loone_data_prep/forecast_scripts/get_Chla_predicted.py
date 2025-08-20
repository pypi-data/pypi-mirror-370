import os
import pandas as pd
import datetime
from loone_data_prep.utils import get_synthetic_data

def get_Chla_predicted(input_dir, output_dir):
    """
    input_dir: Directory where the input files are located.
    output_dir: Directory where the output files will be saved.
    """
    # Read forecast inflow file and get overall date range
    # TODO: Should this be an average/median of all of the ensembles? worst case?
    Q_in = pd.read_csv(os.path.join(input_dir, 'LO_Inflows_BK_forecast_01.csv'))
    Q_in['date'] = pd.to_datetime(Q_in['date'])
    date_start = Q_in['date'].min()
    date_end = Q_in['date'].max()

    # Define stations
    stations = {
        "L001": True,
        "L004": True,
        "L005": True,
        "L006": True,
        "L007": True,
        "L008": True,
        "LZ40": True
    }

    def load_and_check_forecast(station, suffix, start_date, end_date, forecast_suffix="_forecast"):
        fname = f"water_quality_{station}_CHLOROPHYLL-A{suffix}.csv"
        fpath = os.path.join(input_dir, fname)
        df_full = pd.read_csv(fpath).drop(columns=["days"], errors="ignore")
        df_full['date'] = pd.to_datetime(df_full['date'])
        # Rename the specific column if it exists
        possible_cols = [
            f"{station}_CHLOROPHYLL-A, CORRECTED_ug/L",
            f"{station}_CHLOROPHYLL-A(LC)_ug/L"
        ]

        original_col_name = None
        for col in possible_cols:
            if col in df_full.columns:
                df_full.rename(columns={col: "Data"}, inplace=True)
                original_col_name = col
                break

        # Filter df to only rows between start_date and end_date
        df_filtered = df_full[(df_full['date'] >= start_date) & (df_full['date'] <= end_date)]

        # Check if full date range is covered; if not, fill with synthetic data
        missing_dates = pd.date_range(start_date, end_date).difference(df_filtered['date'])
        if len(missing_dates) > 0:
            # Pass the original full historical df_full to get_synthetic_data, along with the forecast start_date
            synthetic_df = get_synthetic_data(start_date, df_full)

            # Rename "Data" back to original column name before saving
            if original_col_name is not None:
                synthetic_df.rename(columns={"Data": original_col_name}, inplace=True)

            # Save synthetic forecast file
            forecast_fname = f"water_quality_{station}_CHLOROPHYLL-A{suffix}{forecast_suffix}.csv"
            synthetic_df.to_csv(os.path.join(input_dir, forecast_fname), index=False)

            return synthetic_df

        return df_filtered

    # Load data for all stations and both suffix types
    chla_data = {}
    chla_data_lc = {}

    for station in stations:
        chla_data[station] = load_and_check_forecast(station, ", CORRECTED", date_start, date_end)
        chla_data_lc[station] = load_and_check_forecast(station, "(LC)", date_start, date_end)

    # Merge function
    def merge_chla_sources(chla_dict):
        merged = None
        for df in chla_dict.values():
            if merged is None:
                merged = df
            else:
                merged = pd.merge(merged, df, on="date", how="left")
            merged = merged.loc[:, ~merged.columns.str.startswith("Unnamed")]
        return merged

    # Calculate aggregates
    def calculate_chla_aggregates(df, suffix=""):
        df = df.set_index("date")
        df["Mean_Chla"] = df.mean(axis=1)
        df["Chla_North"] = df[[col for col in df.columns if any(site in col for site in ["L001", "L005", "L008"])]].mean(axis=1)
        df["Chla_South"] = df[[col for col in df.columns if any(site in col for site in ["L004", "L006", "L007", "L008", "LZ40"])]].mean(axis=1)
        df = df.reset_index()
        return df[["date", "Mean_Chla", "Chla_North", "Chla_South"]].rename(
            columns={"Mean_Chla": f"Chla{suffix}", "Chla_North": f"Chla_N{suffix}", "Chla_South": f"Chla_S{suffix}"}
        )

    # Process and merge
    LO_Chla = calculate_chla_aggregates(merge_chla_sources(chla_data))
    LO_Chla_LC = calculate_chla_aggregates(merge_chla_sources(chla_data_lc))

    # Merge the two dataframes (no date slicing here since all are limited by Q_in dates)
    LO_Chla_Merge = pd.concat([LO_Chla, LO_Chla_LC]).reset_index(drop=True)

    # Export
    LO_Chla_Merge.to_csv(os.path.join(output_dir, "LO_Chla_Obs_predicted.csv"), index=False)
    LO_Chla_Merge[["date", "Chla_N"]].rename(columns={"Chla_N": "Chla"}).to_csv(os.path.join(output_dir, "N_Merged_Chla_predicted.csv"), index=False)
    LO_Chla_Merge[["date", "Chla_S"]].rename(columns={"Chla_S": "Chla"}).to_csv(os.path.join(output_dir, "S_Merged_Chla_predicted.csv"), index=False)
    return
