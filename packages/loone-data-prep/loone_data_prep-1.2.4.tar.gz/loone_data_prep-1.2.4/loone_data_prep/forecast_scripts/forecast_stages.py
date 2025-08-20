import pandas as pd
from datetime import timedelta

def forecast_stages(workspace_path: str):
    """
    Forecasts the next 15 days of WCA stages based on historical data.
    
    Args:
        workspace_path (str): Path to the workspace directory.
    """
    # Load historical data
    stages = pd.read_csv(f"{workspace_path}/WCA_Stages_Inputs.csv")

    # Convert 'date' column to datetime
    stages['date'] = pd.to_datetime(stages['date'])

    # Start forecast from today (normalized to remove time)
    start_date = pd.Timestamp.today().normalize()

    # Generate forecast for the next 15 days
    forecast_rows = []
    for i in range(16):
        forecast_date = start_date + timedelta(days=i)
        month = forecast_date.month
        day = forecast_date.day

        # Filter historical rows for the same month and day
        same_day_rows = stages[(stages['date'].dt.month == month) & (stages['date'].dt.day == day)]

        if not same_day_rows.empty:
            mean_values = same_day_rows.drop(columns='date').mean()
            forecast_row = {'date': forecast_date}
            forecast_row.update(mean_values.to_dict())
            forecast_rows.append(forecast_row)

    # Create forecast DataFrame
    forecast_df = pd.DataFrame(forecast_rows)

    forecast_df.to_csv(f"{workspace_path}/WCA_Stages_Inputs_Predicted.csv", index=False)
    return
