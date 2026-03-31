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

# Import the logging module to be able to log errors and execution output
import logging

# Import the Rotating File Handler to rotate the logging file
from logging.handlers import RotatingFileHandler

########################################################################################################################################

# SETUP LOGGING
# -------------
logger = logging.getLogger(__name__) # use the module's name as the name in the logs
logger.setLevel(logging.INFO) # set the logging level

# Use RotatingFileHandler.
# maxBytes: 5 * 1024 * 1024 = 5 MB
# backupCount=0: When the file is full, delete it and start a new one.
handler = RotatingFileHandler(
    'execution_logs.log', maxBytes=5*1024*1024, backupCount=0
)

handler = logging.FileHandler('execution_logs.log') # save the logs to an output file

# Format the logs and set it for the HANDLER
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s") 
handler.setFormatter(formatter) 

logger.addHandler(handler) # add the formatted HANDLER to the logger

#########################################################################################################################################

# HELPER FUNCTION: GET THE RIGHT PATH FOR FILES
# ---------------------------------------------
def get_base_path():
    """Gets the base path for the application, whether running as a script or frozen."""
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle (e.g., by PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # If running as a normal .py script
        return os.path.dirname(os.path.abspath(__file__))
    
 
# RUN CHECK AND GENERATE UPDATES AND REPORTS
# ------------------------------------------
async def main(excel_sheet_name, progress_callback=None):


    ### <=== USER WARNING ===> ### Correct this and print an error message on the GUI when document is open
    # We need to warn the user before continuing running the program to close the EXCEL file, if open:
    #--------------------------------------------------------------------
    logger.info(f"Starting main program for sheet: '{excel_sheet_name}'")
    #--------------------------------------------------------------------

    ### <=== GET THE FILE PATHS ===> ###
    BASE_PATH = get_base_path()
    excel_file = os.path.join(BASE_PATH, 'Printer_Fleet_Table.xlsx')
    report_file = os.path.join(BASE_PATH, 'Printer_Report.html')
    #-------------------------------------------------------------
    logger.info(f"Retrieving the EXCEL file path: '{excel_file}'")
    logger.info(f"Retrieving the HTML file path: '{report_file}'")
    #-------------------------------------------------------------


    ### <=== CLOSE THE EXCEL FILE IF OPEN ===> ###
    # After warning the user, the EXCEL file will be closed if open...
    #---------------------------------------------
    logger.info("Closing the EXCEL File if open.")
    #---------------------------------------------
    printers_data_ops.close_excel_file_if_open(excel_file)


    ### <=== DEFINE THE DATAFRAME ===> ###
    # First, we will define a DataFrame with pandas that contains all the dictionary keys as columns, so that we can operate and analize the data easily later on. 
    # We can enter whatever sheet we want to perform the check in: each sheet represents a site / excercise with its correspondent printers.
    #-------------------------------------------------------------------------------
    logger.info(f"Creating the DataFrame from the EXCEL file: '{excel_sheet_name}'")
    #-------------------------------------------------------------------------------
    all_printers_df = printers_data_ops.create_printers_dataframe(excel_file, excel_sheet_name)
    

    ### <=== CHECK ONLINE AND OFFLINE PRINTERS ===> ###
    # We will check which printers are online and which are offline. We will use pandas add a Online or Offline value to the Status column for each one.
    #status_dict = await printer_network_checks_async.ping_printers_async(all_printers_df, "IP Address")
    # Find the call to ping_printers_async and pass the callback
    #-----------------------------------------
    logger.info("Starting the network check.")
    #-----------------------------------------
    status_dict = await printer_network_checks_async.ping_printers_async(
        all_printers_df,
        "IP Address",
        progress_callback=progress_callback # Pass it down
    )
    
    #------------------------------------------------------------------------
    logger.info("Network check complete. Proceeding with the status update.")
    #------------------------------------------------------------------------


    ### <=== UPDATE STATUS COLUMN ===> ###
    # This line uses the returned dictionary to safely map the statuses to the correct rows.
    #----------------------------------------------
    logger.info("Updating the printer statuses...")
    #----------------------------------------------
    all_printers_df['Status'] = all_printers_df['IP Address'].map(status_dict)

    # Lets add the Status column to the original EXCEL Table file, so the users can also see each printer state on the tracker.
    printers_data_ops.update_excel_table_status(excel_file, excel_sheet_name, all_printers_df)
    #----------------------------------------------
    logger.info("Printer status update completed.")
    #----------------------------------------------


    ### <=== GET A COUNT OF ONLINE AND OFFLINE PRINTERS ===> ###
    # We will add a column called 'Base Code' to group printers by base later
    all_printers_df['Base Code'] = all_printers_df['Hostname'].str[:4]

    # Then, let's group the printers by base and status
    # Group rows by the 'Base' and 'Status' value
    grouped_by_base_and_status = all_printers_df.groupby(['Base Code', 'Status']).size()

    # For a cleaner DataFrame format, we can add .reset_index()
    grouped_by_base_and_status.reset_index(name='Count')


    ### <=== PLOT THE COUNTS ===> ###
    # Lets make a nice Pie Chart:
    #-------------------------------------------------------------
    logger.info("Generating a Pie Chart with the printer counts.")
    #-------------------------------------------------------------
    pie_chart_file_name = printer_plots.generate_printer_pie_chart(all_printers_df, "Status")

    #-------------------------------------------------------------
    logger.info("Generating a Bar Chart with the printer counts.")
    #-------------------------------------------------------------
    # Finally, we can use a bar cart to represent the Online and Offline printer per base
    bar_chart_file_name = printer_plots.generate_printer_bar_chart(all_printers_df, "Base Code", "Status")


    ### <=== GENERATE THE HTML REPORT ===> ###
    #----------------------------------------------
    logger.info("Generating the HTML Report.")
    #----------------------------------------------
    printer_report_craft.generate_printer_report_in_html(excel_sheet_name, all_printers_df, pie_chart_file_name, bar_chart_file_name)
    
    # Now we can open it
    printers_data_ops.open_output_files(excel_file, report_file)