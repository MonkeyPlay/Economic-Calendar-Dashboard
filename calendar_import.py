import investpy
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta, date
from collections import Counter
import tkinter as tk
from tkinter import ttk
import pandas as pd
import pytz

def fetch_and_prepare_data_with_investpy():
    """
    Fetches economic calendar data for the current day using the investpy library
    and converts it into the list of dictionaries format required by other functions.
    The fetched time is correctly localized to the 'Europe/London' timezone.
    
    Returns:
        list: A list of dictionaries, where each dictionary represents an event.
    """
    try:
        # Define the date range for the request.
        # To handle the investpy requirement that to_date > from_date, we fetch for today and tomorrow,
        # then filter the results for today only.
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        from_date_str = today.strftime('%d/%m/%Y')
        to_date_str = tomorrow.strftime('%d/%m/%Y')

        print(f"Fetching data for today ({from_date_str}) using investpy...")

        # Fetch data using investpy for a two-day range to avoid the library error.
        df = investpy.economic_calendar(from_date=from_date_str, to_date=to_date_str)
        
        # Filter the DataFrame to only include events from today.
        df = df[df['date'] == from_date_str].copy()
        
        # Map importance strings to integer impact levels
        importance_map = {'low': 1, 'medium': 2, 'high': 3}
        
        # Define the target timezone
        london_tz = pytz.timezone('Europe/London')
        
        events = []
        for index, row in df.iterrows():
            # Combine 'date' and 'time' columns to create a proper datetime object.
            date_str = row['date']
            time_str = row.get('time', 'All Day')
            
            naive_datetime = None
            if time_str and time_str.lower() != 'all day':
                datetime_str = f"{date_str} {time_str}"
                try:
                    naive_datetime = datetime.strptime(datetime_str, '%d/%m/%Y %H:%M')
                except ValueError:
                    naive_datetime = datetime.strptime(datetime_str, '%d/%m/%Y %H')
            else:
                naive_datetime = datetime.strptime(date_str, '%d/%m/%Y')
            
            # The time from investpy appears to be naive but correct for the London wall clock.
            # We just need to make it timezone-aware by localizing it.
            local_datetime = london_tz.localize(naive_datetime)
            
            # Convert the importance string to our numeric impact level
            impact_level = importance_map.get(row['importance'], 0)
            
            events.append({
                # Store date and time separately in the format our functions expect
                'date': local_datetime.strftime('%b %d, %Y'),
                'time': local_datetime.strftime('%H:%M') if time_str.lower() != 'all day' else 'All Day',
                'datetime': local_datetime, # Store the full timezone-aware datetime object
                'currency': row.get('currency', 'N/A'),
                'event': row.get('event', 'N/A'),
                'impact': impact_level,
                'actual': row.get('actual', ''),
                'consensus': row.get('forecast', ''), # investpy uses 'forecast' for consensus
                'previous': row.get('previous', '')
            })
        
        return events

    except Exception as e:
        print(f"An error occurred while fetching or processing data with investpy: {e}")
        print("Please ensure you have the 'investpy' and 'pytz' libraries installed and have a working internet connection.")
        return []

def filter_events(events, currencies=None, min_impact=0):
    """
    Filters a list of economic events by currency and minimum impact level.
    """
    filtered_events = []
    for event in events:
        if event.get('impact', 0) < min_impact:
            continue
        if currencies and event.get('currency') not in currencies:
            continue
        filtered_events.append(event)
    return filtered_events

def plot_economic_events(events_data, fig, start_time_str='09:00', end_time_str='19:00'):
    """
    Plots economic events on a timeline within a given figure. 
    The left Y-axis shows the count of events.
    The right Y-axis shows the accumulated weighted impact score.
    The time range is controlled by user input.
    """
    # Clear the figure in case of replotting
    fig.clear()
    ax1 = fig.add_subplot(111)

    if not events_data:
        ax1.text(0.5, 0.5, 'No data to plot for the selected filters.', horizontalalignment='center', verticalalignment='center')
        return

    events_by_impact = {1: [], 2: [], 3: []}
    all_events_with_dt = []
    for event in events_data:
        impact = event.get('impact', 0)
        dt = event.get('datetime')
        if impact in events_by_impact and dt:
            events_by_impact[impact].append(dt)
            all_events_with_dt.append(event)

    colors = {1: 'green', 2: 'orange', 3: 'red'}
    labels = {1: 'Low Impact', 2: 'Medium Impact', 3: 'High Impact'}
    
    max_event_count = 0

    # Plot event counts on the primary y-axis (ax1)
    for impact_level in sorted(events_by_impact.keys()):
        datetimes = events_by_impact[impact_level]
        if datetimes:
            datetime_counts = Counter(datetimes)
            sorted_events = sorted(datetime_counts.items())
            
            x_values = [item[0] for item in sorted_events]
            y_values = [item[1] for item in sorted_events]
            
            if y_values and max(y_values) > max_event_count:
                max_event_count = max(y_values)

            ax1.plot(x_values, y_values, marker='o', linestyle='-', color=colors[impact_level], label=f"{labels[impact_level]} (Count)")

    # --- Calculate and plot accumulated weighted score on secondary y-axis ---
    ax2 = None
    if all_events_with_dt:
        sorted_all_events = sorted(all_events_with_dt, key=lambda x: x['datetime'])
        accumulated_score = 0
        score_timeline = []
        score_values = []
        
        for event in sorted_all_events:
            accumulated_score += event['impact']
            score_timeline.append(event['datetime'])
            score_values.append(accumulated_score)
            
        ax2 = ax1.twinx()
        ax2.plot(score_timeline, score_values, color='blue', linestyle='--', label='Accumulated Score')
        ax2.set_ylabel('Accumulated Weighted Score', color='blue', fontsize=12)
        ax2.tick_params(axis='y', labelcolor='blue')

    today_str = date.today().strftime('%B %d, %Y')
    ax1.set_title(f"Economic Events for {today_str}", fontsize=16, weight='bold')
    ax1.set_xlabel('Time of Day (London)', fontsize=12)
    ax1.set_ylabel('Number of Events at a Time', fontsize=12)
    
    if max_event_count > 0:
        ax1.set_yticks(range(1, int(max_event_count) + 2))
        ax1.set_ylim(0.5, max_event_count + 0.5)

    london_tz = pytz.timezone('Europe/London')
    
    # --- Set X-axis limits based on user input ---
    try:
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
        plot_date = date.today()
        start_dt = london_tz.localize(datetime.combine(plot_date, start_time))
        end_dt = london_tz.localize(datetime.combine(plot_date, end_time))
        ax1.set_xlim(start_dt, end_dt)
    except ValueError:
        print("Invalid time format. Please use HH:MM. Using full day view.")

    # Set locator for 30-minute ticks and formatter
    ax1.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0, 30], tz=london_tz))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=london_tz))
    fig.autofmt_xdate(rotation=45)

    # Combine legends from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    if ax2 and ax2.lines:
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, title="Metrics", loc='upper left')
    else:
        ax1.legend(lines1, labels1, title="Metrics", loc='upper left')
    
    fig.tight_layout()


def create_main_window(all_events_data):
    """
    Creates the main GUI window containing the event table, plot, and controls.
    """
    root = tk.Tk()
    root.title("Economic Calendar Dashboard")
    root.geometry("1200x900")

    # --- Top Frame for the Table ---
    table_frame = ttk.Frame(root, height=300)
    table_frame.pack(side='top', fill='x', expand=False, padx=10, pady=10)
    table_frame.pack_propagate(False)

    columns = ('date', 'time', 'currency', 'impact', 'event')
    tree = ttk.Treeview(table_frame, columns=columns, show='headings')
    tree.heading('date', text='Date')
    tree.heading('time', text='Time')
    tree.heading('currency', text='Currency')
    tree.heading('impact', text='Impact')
    tree.heading('event', text='Event Name')
    tree.column('date', width=120, anchor='center')
    tree.column('time', width=80, anchor='center')
    tree.column('currency', width=80, anchor='center')
    tree.column('impact', width=80, anchor='center')
    tree.column('event', width=750)

    scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side='right', fill='y')
    tree.pack(side='left', expand=True, fill='both')
    
    # --- Controls Frame ---
    controls_frame = ttk.Frame(root)
    controls_frame.pack(side='top', fill='x', padx=10, pady=(0, 10))

    ttk.Label(controls_frame, text="Start Time (HH:MM):").pack(side='left', padx=(0, 5))
    start_time_entry = ttk.Entry(controls_frame, width=8)
    start_time_entry.pack(side='left', padx=5)
    start_time_entry.insert(0, "09:00")

    ttk.Label(controls_frame, text="End Time (HH:MM):").pack(side='left', padx=(10, 5))
    end_time_entry = ttk.Entry(controls_frame, width=8)
    end_time_entry.pack(side='left', padx=5)
    end_time_entry.insert(0, "19:00")

    ttk.Label(controls_frame, text="Min Impact:").pack(side='left', padx=(10, 5))
    impact_filter_entry = ttk.Entry(controls_frame, width=4)
    impact_filter_entry.pack(side='left', padx=5)
    impact_filter_entry.insert(0, "2")

    # --- Plot Frame ---
    plot_frame = ttk.Frame(root)
    plot_frame.pack(side='top', fill='both', expand=True, padx=10, pady=10)

    fig = plt.figure(figsize=(12, 6))
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def update_view():
        # Get filter values from UI
        start_str = start_time_entry.get()
        end_str = end_time_entry.get()
        try:
            min_impact = int(impact_filter_entry.get())
        except ValueError:
            min_impact = 0 # Default to 0 if input is invalid
        
        # Hardcoded currency filter
        target_currencies = ['USD', 'EUR', 'GBP', 'JPY']
        
        # Filter the original full dataset based on the new criteria
        filtered_data = filter_events(all_events_data, currencies=target_currencies, min_impact=min_impact)
        
        # Update the table view
        # First, clear all existing items
        for i in tree.get_children():
            tree.delete(i)
        # Then, populate with the newly filtered data
        for event in filtered_data:
            tree.insert('', tk.END, values=(
                event.get('date', 'N/A'),
                event.get('time', 'N/A'),
                event.get('currency', 'N/A'),
                event.get('impact', 'N/A'),
                event.get('event', 'N/A')
            ))

        # Update the plot with the same filtered data
        plot_economic_events(filtered_data, fig, start_time_str=start_str, end_time_str=end_str)
        canvas.draw()

    update_button = ttk.Button(controls_frame, text="Update View", command=update_view)
    update_button.pack(side='left', padx=10)

    # Initial population of the view with default filters
    update_view()

    root.mainloop()


if __name__ == "__main__":
    # Fetch all data for the day
    all_calendar_data = fetch_and_prepare_data_with_investpy()

    if all_calendar_data:
        print(f"\nExtracted {len(all_calendar_data)} total economic events for today.")
        # Create the main window and pass the full, unfiltered dataset to it
        create_main_window(all_calendar_data)
    else:
        print("Could not fetch or parse any event data.")
