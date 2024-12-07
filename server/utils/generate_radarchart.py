import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def generate_radar_chart(hourly_counts, output_name):
    """
    Generates a radar chart for message activity by hour with numbers displayed at each time.

    Parameters:
    - hourly_counts (list): A list of message counts for each hour (0 to 23).
    - output_name (str): The filename for the generated radar chart image.

    Returns:
    - str: The file path to the saved radar chart image.
    """
    # Prepare data for the radar chart
    angles = np.linspace(0, 2 * np.pi, 24, endpoint=False).tolist()
    angles += angles[:1]  # Repeat the first angle to close the circle

    data = hourly_counts + hourly_counts[:1]  # Repeat the first data point to close the circle

    # Set up the polar plot
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.fill(angles, data, color='slategray', alpha=0.7, label="Message Count")
    ax.plot(angles, data, color='slategray', linewidth=2)

    # Add radial labels (hours of the day)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])  # Exclude the repeated angle
    ax.set_xticklabels([f"{hour} h" for hour in range(24)])

    max_value = max(data)
    adaptive_interval = max(1, max_value // 5)  # Divide into roughly 5 intervals, minimum interval is 1

    # Add polygons for numeric value representation
    for i in range(0, max_value + 1, adaptive_interval):  # Use adaptive intervals
        if i > 0:  # Skip the center
            ax.plot(angles, [i] * len(angles), color='gray', linestyle='--', linewidth=0.7)
            ax.text(
                0,  # Angle at the top
                i,  # Radius
                str(i),  # Numeric label
                ha='center',
                va='center',
                fontsize=10,
                color='black'
            )


    # Add a title
    ax.set_title("Activity by Time of Day", va='bottom', fontsize=16, fontweight='bold')

    # Remove y-ticks and set background color
    ax.yaxis.set_visible(False)
    ax.set_facecolor('lightgray')

    # Save the radar chart image to the static directory
    output_path = os.path.join('static', output_name)
    plt.savefig(output_path, bbox_inches='tight', dpi=1000)
    plt.close()

    return output_path

