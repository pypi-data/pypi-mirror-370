import pandas as pd
import os

def create_forecasts(workspace):
    """
    Reads the four specified CSV files from `workspace`,
    creates forecast versions using historical daily averages,
    and writes new CSV files into the same folder.
    
    The forecast always starts today and goes 16 days forward.
    """

    # List of filenames
    files = [
        'N_OP.csv',
        'S_OP.csv',
        'N_DIN.csv',
        'S_DIN.csv',
        'LO_DO_Clean_daily.csv'
    ]

    def forecast_df(df, date_column='date'):
        # Parse dates
        df[date_column] = pd.to_datetime(df[date_column])

        # Add month and day columns
        df['month'] = df[date_column].dt.month
        df['day'] = df[date_column].dt.day

        # Identify numeric columns to forecast
        value_columns = df.columns.difference([date_column, 'month', 'day'])

        # Compute historical averages
        avg = df.groupby(['month', 'day'])[value_columns].mean().reset_index()

        # Create forecast dates: today + next 15 days
        forecast_dates = pd.date_range(
            start=pd.Timestamp.today().normalize(),
            periods=16,
            freq='D'
        )

        forecast_df = pd.DataFrame({date_column: forecast_dates})
        forecast_df['month'] = forecast_df[date_column].dt.month
        forecast_df['day'] = forecast_df[date_column].dt.day

        # Merge with historical averages
        forecast_df = forecast_df.merge(avg, on=['month', 'day'], how='left')

        # Drop helper columns
        forecast_df.drop(columns=['month', 'day'], inplace=True)

        return forecast_df

    # Process each file
    for filename in files:
        # Read file
        file_path = os.path.join(workspace, filename)
        df = pd.read_csv(file_path)

        # Build forecast
        forecast = forecast_df(df, date_column='date')

        # Save new file
        forecast_filename = filename.replace('.csv', '_forecast.csv')
        forecast_path = os.path.join(workspace, forecast_filename)
        forecast.to_csv(forecast_path, index=False)

    print("Forecast files created successfully.")


