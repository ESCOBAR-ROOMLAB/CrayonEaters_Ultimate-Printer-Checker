#!/usr/bin/env python
# coding: utf-8

# ***IMPORT THE NECESSARY MODULES***
# Import the module that contains fucntions to read, open and write the EXCEL Table with the printer Fleet
import printers_data_ops

# Stands for "regular expression"; used for advanced string searching and manipulation. Thanks to this module we can extract easily chunks of strings 
# and place them on a separate column as column values (for example, the Base Code column)
import re

# A powerful library for data manipulation and analysis, primarily using DataFrames. We will use it to analyse and operate with the printer's data that
# has been imported from the dictionary.
import pandas as pd

# The module with the code to generate a printer report in HTML
import printer_report_craft

# The module with the code to generate data visualizations based on the printer data
import printer_plots

# This module provides the network operations to check the status of the printers
import printer_network_checks_async

# This module allows us to run asynchronous tasks
import asyncio

#########################################################################################################################################

async def main():

    # We need to warn the user before continuing running the program to close the EXCEL file, if open:
    # --- NEW: User Warning Section ---
    print("===================================================================")
    print(" *** IMPORTANT WARNING ***")
    print(" Please ensure the Excel file 'Printer_Fleet_Table.xlsx' is CLOSED.")
    print(" Keeping the file open will cause a 'Permission Denied' error.")
    print("===================================================================")
    input("Press Enter to continue...")
    # -----------------------------


    # ***DEFINE THE DATAFRAME***
    # First, we will define a DataFrame with pandas that contains all the dictionary keys as columns, so that we can operate and analize the data easily later on. We can enter whatever sheet we want to perform the check in: each sheet represents a site / excercise with its correspondent printers.
    excel_sheet_name = input("Enter the EXCEL sheet name: ")
    all_printers_df = printers_data_ops.create_printers_dataframe(excel_sheet_name)


    # ***CHECK ONLINE AND OFFLINE PRINTERS***
    # We will check which printers are online and which are offline. We will use pandas add a Online or Offline value to the Status column for each one.
    await printer_network_checks_async.ping_printers_async(all_printers_df, "Status", "Hostname", "IP Address")

    # We can also check how the DataFrame looks like now, with the Status column added...
    all_printers_df.head(2)

    # Lets add the Status column to the original EXCEL Table file, so the users can also see each printer state on the tracker.
    printers_data_ops.update_excel_table_status(excel_sheet_name, all_printers_df)


    # ***GET A COUNT OF TOTAL ONLINE AND OFFLINE PRINTERS***
    # We will add a column called 'Base Code' to group printers by base later
    all_printers_df['Base Code'] = all_printers_df['Hostname'].str[:4]

    # Lets give the counts in text format...
    # Get the count of each status
    status_counts =  all_printers_df.groupby('Status')

    # Display the text counts
    print(f"\n{status_counts.size()}\n")

    # And also in a nice Pie Chart:
    pie_chart_file_name = printer_plots.generate_printer_pie_chart(all_printers_df, "Status")


    # ***GET A COUNT OF TOTAL ONLINE AND OFFLINE PRINTERS PER BASE***
    # First, let's group the printers by base and status
    # Group rows by the 'Base' and 'Status' value
    grouped_by_base_and_status = all_printers_df.groupby(['Base Code', 'Status']).size()

    # For a cleaner DataFrame format, you can add .reset_index()
    grouped_by_base_and_status_df = grouped_by_base_and_status.reset_index(name='Count')

    # Now we can display the text counts:
    # --- Display the results ---
    print(f"\n{grouped_by_base_and_status}\n")

    # Finally, we can use a bar cart to represent the Online and Offline printer per base
    bar_chart_file_name = printer_plots.generate_printer_bar_chart(all_printers_df, "Base Code", "Status")


    # ***GENERATE A PRINTER STATUS REPORT***
    printer_report_craft.generate_printer_report_in_html(all_printers_df, pie_chart_file_name, bar_chart_file_name)

# ADD these lines at the very end of your file:
if __name__ == "__main__":
    asyncio.run(main())


