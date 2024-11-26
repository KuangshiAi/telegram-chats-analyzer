import matplotlib.pyplot as plt
import calendar
import numpy as np
from datetime import datetime

def generate_calendar(data, output_name="calendar.png"):
    """
    Generate a calendar heatmap for chat activity.

    Parameters:
    - data: List of tuples (date, normalized_value) where normalized_value is between 0 and 1.
    - output_name: Name of the output image file.
    """

    # Convert the data to a dictionary for easier lookup
    data_dict = {datetime.strptime(str(date), "%Y-%m-%d").date(): value for date, value in data}

    # Get the year and month from the data
    dates = list(data_dict.keys())
    if not dates:
        raise ValueError("No data provided for calendar generation.")

    min_date = min(dates)
    max_date = max(dates)
    year = min_date.year

    # Prepare the calendar layout
    months = range(min_date.month, max_date.month + 1)
    ncols = 3
    nrows = int(np.ceil(len(months) / ncols))
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(15, nrows * 5))
    axes = axes.flatten()

    # Iterate over each month and generate the heatmap
    for i, month in enumerate(months):
        ax = axes[i]
        month_days = calendar.monthcalendar(year, month)

        # Create an array for the month data with normalized values
        month_data = np.zeros((len(month_days), 7))  # Weeks x Days
        for week_idx, week in enumerate(month_days):
            for day_idx, day in enumerate(week):
                if day != 0:  # Skip empty days
                    current_date = datetime(year, month, day).date()
                    month_data[week_idx, day_idx] = data_dict.get(current_date, 0)

        # Plot the heatmap for the current month
        im = ax.imshow(month_data, cmap="YlGn", aspect="auto", vmin=0, vmax=1)
        ax.set_title(f"{calendar.month_name[month]} {year}")
        ax.set_xticks(range(7))
        ax.set_xticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        ax.set_yticks(range(len(month_days)))
        ax.set_yticklabels([])  # Hide week numbers

    # Remove unused axes
    for j in range(len(months), len(axes)):
        fig.delaxes(axes[j])

    # Add a colorbar
    fig.colorbar(im, ax=axes, orientation='horizontal', fraction=0.02, pad=0.1)

    # Save the calendar heatmap
    plt.tight_layout()
    plt.savefig(output_name)
    plt.close()
