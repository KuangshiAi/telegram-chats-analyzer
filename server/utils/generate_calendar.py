import numpy as np
import pandas as pd
import calmap
import matplotlib.pyplot as plt
import datetime
import matplotlib
matplotlib.use('Agg')

# data = [
#     (datetime.date(2023, 8, 2), 179),
#     (datetime.date(2023, 8, 3), 150),
#     (datetime.date(2023, 9, 1), 200),
#     # Add more data as needed
# ]
# events = pd.Series([dat[1] for dat in data], index=pd.DatetimeIndex([dat[0] for dat in data]))
# print(events)
# x = calmap.calendarplot(events)
# plt.show()

def generate_calendar(data, output_path='./static/', output_name='calendar_both.png'):
    events = pd.Series([dat[1] for dat in data], index=pd.DatetimeIndex([dat[0] for dat in data]))
    plt.figure(figsize=(30, 20))
    calmap.calendarplot(events, vmin=0, vmax=1)
    plt.savefig(output_path + output_name)
    plt.close()


