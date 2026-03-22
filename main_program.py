#!/usr/bin/env python
# coding: utf-8

# ***IMPORT THE NECESSARY MODULES***
# Import the module that contains fucntions to read, open and write the EXCEL Table with the printer Fleet
import printers_data_ops

# The module with the code to generate a printer report in HTML
import printer_report_craft

# The module with the code to generate data visualizations based on the printer data
import printer_plots

# This module provides the network operations to check the status of the printers
import printer_network_checks_async # type: ignore

# This module allows us to run asynchronous tasks
import asyncio

# This module will help us retrieve the absolute path for the files that we operate in the program
import os

# This module will let the program itself determine if is being run as a bundle or as a script
import sys


#########################################################################################################################################

# This helper function determines the correct base path, whether running as a script or a bundled .exe
def get_base_path():
    """Gets the base path for the application, whether running as a script or frozen."""
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle (e.g., by PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # If running as a normal .py script
        return os.path.dirname(os.path.abspath(__file__))
    
 
async def main(excel_sheet_name, progress_callback=None):

    # We need to warn the user before continuing running the program to close the EXCEL file, if open:
    # --- User Warning Section ---
    print("\n\n===================================================================")
    print(" *** IMPORTANT WARNING ***")
    print(" The Excel file 'Printer_Fleet_Table.xlsx' will be CLOSED if open.")
    print(" Keeping the file open will cause a 'Permission Denied' error.")
    print("===================================================================")
    #input("\nPress Enter to continue...\n")
    # -----------------------------

    # Use the helper function to build reliable paths to your files.
    BASE_PATH = get_base_path()
    excel_file = os.path.join(BASE_PATH, 'Printer_Fleet_Table.xlsx')
    report_file = os.path.join(BASE_PATH, 'Printer_Report.html')

    # ***CLOSE THE EXCEL FILE IF OPEN***
    # After warning the user, the EXCEL file will be closed if open...
    printers_data_ops.close_excel_file_if_open(excel_file)


    # ***DEFINE THE DATAFRAME***
    # First, we will define a DataFrame with pandas that contains all the dictionary keys as columns, so that we can operate and analize the data easily later on. 
    # We can enter whatever sheet we want to perform the check in: each sheet represents a site / excercise with its correspondent printers.
    all_printers_df = printers_data_ops.create_printers_dataframe(excel_sheet_name)


    # ***CHECK ONLINE AND OFFLINE PRINTERS***
    # We will check which printers are online and which are offline. We will use pandas add a Online or Offline value to the Status column for each one.
    #status_dict = await printer_network_checks_async.ping_printers_async(all_printers_df, "IP Address")
    # Find the call to ping_printers_async and pass the callback
    status_dict = await printer_network_checks_async.ping_printers_async(
        all_printers_df,
        "IP Address",
        progress_callback=progress_callback # Pass it down
    )

    # This line uses the returned dictionary to safely map the statuses to the correct rows.
    all_printers_df['Status'] = all_printers_df['IP Address'].map(status_dict)

    # Lets add the Status column to the original EXCEL Table file, so the users can also see each printer state on the tracker.
    printers_data_ops.update_excel_table_status(excel_sheet_name, all_printers_df)


    # ***GET A COUNT OF TOTAL ONLINE AND OFFLINE PRINTERS***
    # We will add a column called 'Base Code' to group printers by base later
    all_printers_df['Base Code'] = all_printers_df['Hostname'].str[:4]

    # And also in a nice Pie Chart:
    pie_chart_file_name = printer_plots.generate_printer_pie_chart(all_printers_df, "Status")


    # ***GET A COUNT OF TOTAL ONLINE AND OFFLINE PRINTERS PER BASE***
    # First, let's group the printers by base and status
    # Group rows by the 'Base' and 'Status' value
    grouped_by_base_and_status = all_printers_df.groupby(['Base Code', 'Status']).size()

    # For a cleaner DataFrame format, you can add .reset_index()
    grouped_by_base_and_status.reset_index(name='Count')

    # Finally, we can use a bar cart to represent the Online and Offline printer per base
    bar_chart_file_name = printer_plots.generate_printer_bar_chart(all_printers_df, "Base Code", "Status")


    # ***GENERATE A PRINTER STATUS REPORT***
    printer_report_craft.generate_printer_report_in_html(excel_sheet_name, all_printers_df, pie_chart_file_name, bar_chart_file_name)


    # ***OPEN THE HMTL REPORT FILE AND THE EXCEL FILE***
    printers_data_ops.open_output_files(excel_file, report_file) 

# ADD these lines at the very end of your file. This is if we want to ensure that this file stays as the main program file. If using a GUI,
# then we will have to comment these lines:
#if __name__ == "__main__":
 #   asyncio.run(main())



