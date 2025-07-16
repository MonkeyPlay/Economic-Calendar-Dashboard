# Economic-Calendar-Dashboard

<img width="1198" height="930" alt="Screenshot 2025-07-16 095230" src="https://github.com/user-attachments/assets/2840c91a-11e2-4ce0-bf8d-7f094bcb1dc4" />

Economic Calendar Scraper and Plotter
This Python script is designed to scrape economic calendar data from Investing.com, extract key event details including their impact level, and then visualize these events on a timeline, categorized by their importance.
Features
Web Scraping: Fetches the HTML content of the Investing.com economic calendar page.
Data Parsing: Extracts event details such as:
Date
Time
Currency
Event Name
Impact Level (Low, Medium, High - represented as 1, 2, or 3 'bull' icons)
Actual Value
Consensus/Forecast Value
Previous Value
Data Visualization: Plots the extracted economic events on a timeline using matplotlib, with each impact level displayed distinctly using different colors and markers.
How It Works
Access Webpage: The access_webpage function uses the requests library to send an HTTP GET request to the specified URL (https://uk.investing.com/economic-calendar/) and retrieves the page's HTML content.
Parse Data: The parse_economic_calendar function then takes this HTML content and uses BeautifulSoup to:
Locate the main economic calendar table (identified by its id).
Iterate through each row of the table.
Identify date headers to associate events with their correct dates.
Extract specific data points (time, currency, event name, actual, consensus, previous) from the table columns.
Determine the "impact level" by counting specific <i> (bull) icons within the importance column.
Plot Data: The plot_economic_events function processes the extracted event data:
It converts the date and time strings into datetime objects for plotting.
Events are grouped by their impact level.
matplotlib is used to create a scatter plot where events are positioned on a time axis (x-axis) and grouped by their impact level on the y-axis.
Different colors and markers are assigned to each impact level for easy differentiation.
Getting Started
Prerequisites
Before running the script, ensure you have the following Python libraries installed:
requests: For making HTTP requests to fetch web pages.
BeautifulSoup4 (bs4): For parsing HTML and XML documents.
matplotlib: For creating static, animated, and interactive visualizations in Python.
You can install them using pip:
pip install requests beautifulsoup4 matplotlib


Usage
Save the Script: Save the provided Python code (from the python_script_access_page immersive) as a .py file (e.g., economic_calendar_analyzer.py).
Run the Script: Execute the script from your terminal:
python calendar_import.py.py


The script will first print a preview of the accessed page content, then a summary of the extracted economic events (the first 10 for brevity), and finally, it will display a matplotlib plot visualizing these events on a timeline.
Important Considerations
Website Structure Changes: Web scraping scripts are highly dependent on the HTML structure of the target website. If Investing.com changes its layout, element IDs, or class names, the parse_economic_calendar function will need to be updated accordingly.
Rate Limiting: Be mindful of making too many requests in a short period, as websites might implement rate limiting or block your IP address. This script makes a single request, so it's generally safe for casual use.


