# Economic-Calendar-Dashboard

<img width="1198" height="930" alt="Screenshot 2025-07-16 095230" src="https://github.com/user-attachments/assets/2840c91a-11e2-4ce0-bf8d-7f094bcb1dc4" />

# Economic Calendar Scraper and Plotter

This Python script is designed to scrape economic calendar data from [Investing.com](https://uk.investing.com/economic-calendar/), extract key event details including their impact level, and then visualize these events on a timeline, categorized by their importance.

---

## Features

- **Web Scraping**: Fetches the HTML content of the Investing.com economic calendar page.
- **Data Parsing**: Extracts event details such as:
  - Date  
  - Time  
  - Currency  
  - Event Name  
  - Impact Level (Low, Medium, High — represented as 1, 2, or 3 _bull_ icons)  
  - Actual Value  
  - Consensus/Forecast Value  
  - Previous Value  
- **Data Visualization**: Plots the extracted economic events on a timeline using `matplotlib`, with each impact level displayed distinctly using different colors and markers.

---

## How It Works

1. **Access Webpage**  
   The `access_webpage` function uses the `requests` library to send an HTTP GET request to the specified URL and retrieves the page's HTML content.

2. **Parse Data**  
   The `parse_economic_calendar` function then uses `BeautifulSoup` to:
   - Locate the main economic calendar table (identified by its `id`)
   - Iterate through each row of the table
   - Identify date headers to associate events with their correct dates
   - Extract specific data points (time, currency, event name, actual, consensus, previous)
   - Determine the *impact level* by counting specific `<i>` (bull) icons within the importance column

3. **Plot Data**  
   The `plot_economic_events` function:
   - Converts date and time strings into `datetime` objects for plotting
   - Groups events by their impact level
   - Uses `matplotlib` to create a scatter plot where events are positioned on a time axis (x-axis) and grouped by impact level (y-axis)
   - Assigns different colors and markers to each impact level for clarity

---

## Getting Started

### Prerequisites

Ensure you have the following Python libraries installed:

- `requests` – for making HTTP requests  
- `beautifulsoup4` – for parsing HTML and XML documents  
- `matplotlib` – for creating static and interactive plots

You can install them via pip:

```bash
pip install requests beautifulsoup4 matplotlib
