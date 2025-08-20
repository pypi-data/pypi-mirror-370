import pandas as pd
from datetime import datetime, timedelta
import argparse

def extend_PI(PI_path, output_path):
    df = pd.read_csv(PI_path, header=None, skiprows=1, names=["date", "PI"])
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    # Extract month and day for grouping
    df["month_day"] = df["date"].dt.strftime("%m-%d")
    # Sort data in case it's unordered
    df = df.sort_values(by="date").reset_index(drop=True)

    # Compute historical average PI for each month-day
    average_pi = df.groupby("month_day")["PI"].mean().reset_index()

    # Generate future dates (today + next 16 days)
    today = datetime.today()
    future_dates = [today + timedelta(days=i) for i in range(17)]
    future_df = pd.DataFrame({"date": future_dates})

    # Extract month-day from future dates to match historical data
    future_df["month_day"] = future_df["date"].dt.strftime("%m-%d")

    # Merge with historical averages
    future_df = future_df.merge(average_pi, on="month_day", how="left")

    # Append the new rows to the original dataframe
    df_extended = pd.concat([df, future_df[["date", "PI"]]], ignore_index=True)
    df_extended.drop(columns=["month_day"], inplace=True)
    df_extended.set_index('date', inplace=True)
    df_extended = df_extended.resample('W-FRI').mean().reset_index()

    # Save the updated dataframe to CSV
    df_extended.to_csv(output_path, index=False)
    
def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Download and process weather forecast data.")
    parser.add_argument("PI_path", help="Path to the historical palmer index file.")
    parser.add_argument("output_path", help="Path to save the new output file path.")


    # Parse the arguments
    args = parser.parse_args()

    # Call the function with the provided file path
    extend_PI(args.PI_path, args.output_path)


if __name__ == "__main__":
    main()