# Ultimate Printer Status Checker

The Ultimate Printer Status Checker is a desktop application designed to automate the process of verifying the network status of a large fleet of printers. It reads printer information from an Excel file, pings each device to determine if it's online, updates the Excel file with the latest status, and generates a clean, easy-to-read HTML report with data visualizations.


## Features

**Graphical User Interface**: A simple and intuitive UI built with PyQt5.
**Asynchronous Network Checks**: Uses `asyncio` to ping hundreds of devices concurrently, making the process incredibly fast and efficient.
**Excel Integration**: Reads printer data directly from a specified sheet in an `.xlsx` file.
**Non-Destructive Updates**: Updates the status column in the Excel file while perfectly preserving all existing data, formatting, colors, and conditional formatting rules.
**Automated Reporting**: Generates a self-contained HTML report with embedded charts (Pie and Bar) summarizing the online/offline status.
**Data Visualization**: Creates a pie chart showing the overall online vs. offline percentage and a bar chart breaking down the offline count by site.
**Robust and Responsive**: The main work is performed in a background thread, ensuring the user interface never freezes, with real-time progress updates.


## How It Works

1.  The user enters the name of the Excel sheet containing the printer fleet data and clicks "I'm feeling complacient".
2.  The application reads the data from `Printer_Fleet_Table.xlsx` into a pandas DataFrame.
3.  It initiates an asynchronous process to ping the IP address of every printer in the list. A semaphore limits concurrent pings to prevent network overload.
4.  The status of each printer ('Online' or 'Offline') is determined by analyzing the ping command's output with a regular expression.
5.  The original DataFrame is updated with the new status.
6.  Using `openpyxl`, the application carefully writes only the status data back into the original Excel file, leaving all other cells and formatting untouched.
7.  `matplotlib` is used to generate a pie chart and a bar chart, which are saved as temporary image files.
8.  The `printer_report_craft.py` module builds a single, portable `Printer_Report.html` file, embedding the chart images directly using base64.
9.  Finally, the updated Excel file and the newly generated HTML report are automatically opened for the user.


## Requirements

The application is built with Python 3 and requires the following libraries:

*   `PyQt5`: For the graphical user interface.
*   `pandas`: For data manipulation and reading the Excel file.
*   `openpyxl`: For writing data back to the `.xlsx` file while preserving styles.
*   `matplotlib`: For creating the pie and bar charts.
*   `psutil`: To check if the Excel file is open and close it to prevent permission errors.


## Setup

1.  **Clone the Repository (or download the files):**
    ```bash
    git clone [your-repository-url]
    cd [your-repository-folder]
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    You can install the required packages using pip.
    ```bash
    pip install PyQt5 pandas openpyxl matplotlib psutil
    ```


## Usage

1.  **Prepare the Excel File**:
    *   Ensure you have a file named `Printer_Fleet_Table.xlsx` in the same directory as the application.
    *   This file must contain a sheet with a name you can provide to the application (e.g., `MRF-D`).
    *   The sheet must contain at least the following columns: `IP Address`, `Status`, and `Site`. The application will read IPs and Sites, and update the Status.

2.  **Run the Application**:
TO BE WRITTEN WHEN FINISH PYINSTALLER

3.  **Use the Interface**:
    *   The application window will appear.
    *   Enter the exact name of the sheet containing your printer data into the input box.
    *   Click the **"I'm feeling complacient"** button.
    *   The application will show progress updates. Once complete, it will automatically open the updated `Printer_Fleet_Table.xlsx` and the `Printer_Report.html`.


## Project Structure
.
├── images/ # Contains GIFs for the UI
│ ├── ultimate-printer-checker_error_empty.gif
│ ├── ultimate-printer-checker_running.gif
│ └── ultimate-printer-checker_slap.gif
├── main_program.py # Orchestrates the entire workflow
├── printer_network_checks_async.py # Core logic for asynchronous pinging
├── printer_plots.py # Generates pie and bar charts
├── printer_report_craft.py # Builds the final HTML report
├── printers_data_ops.py # Handles all file I/O (read/write Excel)
├── program_gui.py # Main entry point, builds the GUI
├── Printer_Fleet_Table.xlsx # Input data file with printer information
├── Printer_Report.html # Example of the generated output report
└── README.md # This file