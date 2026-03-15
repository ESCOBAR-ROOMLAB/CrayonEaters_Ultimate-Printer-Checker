=========================================
=== Printer Fleet Status & Reporting Tool ===
=========================================

Version: 1.0

-----------------
1. OVERVIEW
-----------------

This tool is a complete solution for monitoring the network status of a fleet of printers or other network devices. It automates the process of checking which devices are online, updates the master tracking document, and generates a user-friendly HTML report with data summaries and visual charts.

The core workflow is as follows:
1.  Reads device data from the 'Printer_Fleet_Table.xlsx' file.
2.  Performs a high-speed, concurrent network ping of every IP address to get a live status ('Online' or 'Offline').
3.  Updates the original Excel file with this status information while preserving all existing cell formatting, colors, and rules.
4.  Generates two plots: a pie chart showing the overall status ratio and a bar chart breaking down the status by location code.
5.  Creates a final, self-contained 'Weekly_Printer_Report.html' file that embeds the data and charts for easy distribution and viewing in any web browser.


-------------------
2. HOW TO USE THE TOOL
-------------------

Follow these steps to run the tool and generate a report.

STEP 1: PREREQUISITES
---------------------
Before running, you must have Python 3 and the required libraries installed. You can install the libraries from your terminal with pip:

example: pip install pandas openpyxl matplotlib


STEP 2: FILE PLACEMENT
----------------------
Place the following files in the SAME directory (they should be there unless your dumbass moved them):
1.  main_program.py (the main script you will run)
2.  printers_data_ops.py
3.  printer_network_checks_async.py
4.  printer_plots.py
5.  printer_report_craft.py
6.  Printer_Fleet_Table.xlsx (the master data file to be read and updated)


STEP 3: RUN THE PROGRAM
-----------------------
Execute the main program from your terminal:

python main_program.py

The script will immediately display a warning. Follow the on-screen prompt and press Enter to continue. Then, enter the name of the sheet for which you want the script to run. A live progress bar will show the status of the network checks.


STEP 4: CHECK THE OUTPUT
------------------------
After the script finishes, the following files will be created or updated in the same directory:
-   Printer_Fleet_Table.xlsx: The original file, now updated with a "Status" column containing the live ping results.
-   printer_status_pie-chart.png: A pie chart image showing the overall percentage of online vs. offline devices.
-   printer_status_by_base_code_bar-chart.png: A bar chart image comparing online/offline counts for each location code.
-   Weekly_Printer_Report.html: The final, viewable report containing all the information. Double-click this file to open it in your web browser.


-----------------------
3. IMPORTANT THINGS TO KNOW
-----------------------

-   CRITICAL: CLOSE THE EXCEL FILE!
    The most common error you will encounter is a 'Permission Denied' error. This happens if 'Printer_Fleet_Table.xlsx' is open in Excel when you run the script. YOU MUST CLOSE THE FILE BEFORE RUNNING THE PROGRAM. The script includes a warning to remind you of this.

-   HOW THE NETWORK CHECK WORKS
    The tool uses a high-speed asynchronous process to ping up to 50 devices at the same time, making it very fast even for large fleets. It determines status by analyzing the "packet loss" percentage from the ping command, which is a reliable method.

-   FORMAT PRESERVATION
    The script is specifically designed to update the Excel file without destroying your existing formatting. Any custom colors, conditional formatting rules, or cell widths will be preserved.

-   FILE DEPENDENCIES
    The main program relies on the other Python (.py) files to function. Do not rename or move them unless you update the 'import' statements in 'main_program.py'.

