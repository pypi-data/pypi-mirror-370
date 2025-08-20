import os
import pandas as pd
from datetime import datetime, timedelta

def generate_historical_predictions(workspace, forecast_days=16):
    """
    Generate predictions for the next `forecast_days` days using historical daily averages
    from the same calendar dates across previous years. Includes all the files for loone_q.
    
    Args:
    workspace : str
        Path to the folder containing the CSV files.

    forecast_days : int
        Number of future days to predict (default = 16).

    """

    file_list = [
        "Estuary_needs_water_Input.csv",
        "Multi_Seasonal_LONINO.csv", 
        "Seasonal_LONINO.csv",
        "SFWMM_Daily_Outputs.csv",
        "Water_dmd.csv",
        "EAA_MIA_RUNOFF_Inputs.csv",
    ]

    possible_date_cols = ['date', 'Date']
    today = datetime.today()
    current_year = today.year

    for filename in file_list:
        path = os.path.join(workspace, filename)
        
        try:
            df = pd.read_csv(path)
        except Exception as e:
            print(f"Could not read {filename}. Error: {e}")
            continue
        
        if filename in ["Multi_Seasonal_LONINO.csv", "Seasonal_LONINO.csv"]:
            if "Year" not in df.columns:
                print(f"No 'Year' column in {filename}. Skipping.")
                continue

            # ➤ Skip if current year already exists
            if current_year in df["Year"].values:
                print(f"{current_year} already present in {filename}. No changes made.")
                continue

            # Otherwise calculate averages and append
            month_cols = [col for col in df.columns if col != "Year"]
            monthly_means = df[month_cols].mean()

            new_row = {"Year": current_year}
            new_row.update(monthly_means.to_dict())

            updated_df = pd.concat(
                [df, pd.DataFrame([new_row])],
                ignore_index=True
            )
            output_name = filename.replace(".csv", f"_forecast.csv")
            output_path = os.path.join(workspace, output_name)
            updated_df.to_csv(output_path, index=False)
            print(f"Appended {current_year} row and saved to {output_path}")
            continue

        # Identify date column
        date_col = None
        for col in df.columns:
            if col in possible_date_cols:
                date_col = col
                break

        if date_col is None:
            print(f"Could not detect date column in {filename}. Skipping.")
            continue

        # Parse dates
        if filename in ["SFWMM_Daily_Outputs.csv", "Water_dmd.csv"]:
            df[date_col] = pd.to_datetime(
                df[date_col],
                format="%d-%b-%y",
                errors="coerce"
            )
        else:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
        df["month_day"] = df[date_col].dt.strftime("%m-%d")

        predictions_list = []

        # Check if special handling is needed for the boolean file
        if filename == "Estuary_needs_water_Input.csv":
            bool_col = "Estuary Needs Water?"

            if bool_col not in df.columns:
                print(f"Column '{bool_col}' not found in {filename}. Skipping.")
                continue

            # Convert string "True"/"False" to boolean if necessary
            if df[bool_col].dtype == object:
                df[bool_col] = df[bool_col].map({"True": True, "False": False}).fillna(df[bool_col])

            # Compute mode (most frequent value) for each day for each boolean column
            mode_series = df.groupby("month_day")[bool_col].agg(
                lambda x: x.mode().iloc[0] if not x.mode().empty else None
            )
            for i in range(1, forecast_days + 1):
                future_date = today + timedelta(days=i)
                mmdd = future_date.strftime("%m-%d")

                if mmdd in mode_series.index:
                    pred_value = mode_series.loc[mmdd]
                else:
                    print(f"No historical data for {mmdd} in {filename}. Skipping that day.")
                    pred_value = None

                predictions_list.append({
                    date_col: future_date,
                    bool_col: pred_value
                })

            pred_df = pd.DataFrame(predictions_list)
            pred_df = pred_df[[date_col, bool_col]]

        else:
            # Numeric file handling
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            if not numeric_cols:
                print(f"No numeric columns in {filename}. Skipping.")
                continue

            historical_means = df.groupby("month_day")[numeric_cols].mean()

            for i in range(0, forecast_days + 1):
                future_date = (today + timedelta(days=i)).date()
                mmdd = future_date.strftime("%m-%d")
                if mmdd in historical_means.index:
                    row = historical_means.loc[mmdd].copy()
                    row[date_col] = future_date
                    predictions_list.append(row)
                else:
                    print(f"No historical data for {mmdd} in {filename}. Skipping that day.")

            if predictions_list:
                pred_df = pd.DataFrame(predictions_list)
                pred_df = pred_df[[date_col] + [col for col in pred_df.columns if col != date_col]]
            else:
                print(f"No predictions generated for {filename}.")
                continue

        # Save predictions
        output_name = filename.replace(".csv", f"_forecast.csv")
        output_path = os.path.join(workspace, output_name)
        pred_df.to_csv(output_path, index=False)
        print(f"Predictions saved to {output_path}")

    return