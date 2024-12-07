import matplotlib.pyplot as plt
import os
from datetime import datetime
import matplotlib
matplotlib.use('Agg')

def generate_pie_chart(chat_counts, output_name):
    """
    Generates a pie chart with a legend for message counts and saves it as an image.

    Parameters:
    - chat_counts (dict): A dictionary where keys are user names and values are chat counts.
    - output_name (str): The filename for the generated pie chart image.

    Returns:
    - str: The file path to the saved pie chart image.
    """
    # Extract labels and sizes from the chat_counts dictionary
    labels = list(chat_counts.keys())
    sizes = list(chat_counts.values())

    # Handle the case where there are too many users by grouping smaller counts into "Others"
    if len(labels) > 10:
        # Sort users by count in descending order
        sorted_users = sorted(chat_counts.items(), key=lambda item: item[1], reverse=True)
        # Take the top 9 users
        top_users = sorted_users[:9]
        # Sum the remaining counts
        others_count = sum(count for _, count in sorted_users[9:])
        # Update labels and sizes
        labels = [user for user, _ in top_users] + ["Others"]
        sizes = [count for _, count in top_users] + [others_count]

    # Define colors
    cmap = plt.get_cmap("tab20")
    colors = cmap.colors[:len(labels)]

    # Create a pie chart
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts = ax.pie(
        sizes,
        labels=labels,
        labeldistance=1.15,
        colors=colors,
        startangle=90,
        wedgeprops=dict(width=0.4, edgecolor="w"),
        textprops=dict(color="black", fontsize=10)
    )

    # Add a legend
    ax.legend(wedges, [f"{label}: {size}" for label, size in zip(labels, sizes)],
              title="User Message Counts", loc="upper center", bbox_to_anchor=(1, 0, 0.5, 1))

    # Add a title
    ax.set_title("Chat Numbers by User", fontsize=16, fontweight="bold", y=1.05)

    # Save the pie chart image to the static directory
    output_path = os.path.join('static', output_name)
    plt.savefig(output_path, bbox_inches='tight', dpi=1000)
    plt.close()

    return output_path
