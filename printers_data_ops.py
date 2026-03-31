# Used to create the DataFrame to store the printer fleet information
import pandas as pd # type: ignore

# Use openpyxl to load the existing Printer_Fleet_Table.xlsx into memory, keeping all your colors and rules.
from openpyxl import load_workbook # type: ignore
from openpyxl.utils.dataframe import dataframe_to_rows # type: ignore

# Library for interacting with system processes
import psutil # type: ignore

# Used to get the filename from a full path
import os

# Provides a way to open files in a web browser.
import webbrowser 

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

# CREATE DATAFRAME
# ----------------
def create_printers_dataframe(excel_file, excel_sheet_name):

    """
    PURPOSE:

    This function reads a specific sheet from the 'Printer_Fleet_Table.xlsx' file
    into a pandas DataFrame. It also validates that the file exists and that
    it contains an 'IP Address' column before returning the data.

    ARGUMENTS:

    excel_file = the absolute path of the EXCEl file

    excel_sheet_name = the name of the sheet inside the Excel file from which to
    read the printer data. It should be a string.

    RETURN VALUE:

    On success, the function returns a pandas DataFrame containing all the data
    from the specified Excel sheet. If the file is not found or the 'IP Address'
    column is missing, the function will print an error message and terminate
    the program, returning nothing.

    """

    try:
        # Read the data from the specified sheet
        all_printers_df = pd.read_excel(excel_file, sheet_name=excel_sheet_name)
        #------------------------------------------
        logger.info("Dataframe creation succeded!")
        #------------------------------------------
    except FileNotFoundError:
        #-------------------------------------------------------------------------------
        logger.error(f"Dataframe creation failed: The path {excel_file} was not found.")
        #-------------------------------------------------------------------------------
        exit()
    except Exception as e:
        #----------------------------------------------------------------------------------
        logger.error(f"Dataframe creation failed: error while reading the Excel file: {e}")
        #----------------------------------------------------------------------------------
        exit()

    # Check if the required column exists
    if 'IP Address' not in all_printers_df.columns:
        #------------------------------------------------------------------------------------------------------
        logger.error("Dataframe creation failed: A column named 'IP Address' was not found in the Excel file.")
        #------------------------------------------------------------------------------------------------------
        exit()
    
    return all_printers_df


# UPDATE THE STATUS COLUMN
# ------------------------
def update_excel_table_status(excel_file, excel_sheet_name, all_printers_df):
    """
    PURPOSE:

    This function updates an existing Excel file ('Printer_Fleet_Table.xlsx') with
    new status data from a pandas DataFrame, while carefully preserving all existing
    formatting like colors, conditional rules, and column widths. It uses the
    openpyxl library to load the workbook, find or create a 'Status' column,
    write the new data cell by cell, and then save the changes.

    ARGUMENTS:

    excel_file = the absolute path of the EXCEl file

    excel_sheet_name = the name of the sheet within the Excel workbook that needs to be updated. 
    It should be a string.
                    
    all_printers_df  = the pandas DataFrame containing the full dataset, including
    the 'Status' column with the updated online/offline values that will be written to the file.

    RETURN VALUE:

    This function does not return any value. Its primary effect is modifying the
    'Printer_Fleet_Table.xlsx' file by adding or updating the 'Status' column.
    It also prints messages to the console indicating the progress and the final
    success or failure of the operation.

    """
    # Initialize workbook to None before the try block. This is needed so if the user has the EXCEL file open and the program
    # cannot open it, then the "finally" block can execute anyways instead of crashing due to an invalid "workbook" variable.
    workbook = None 

    # Assuming 'printers_df' is your DataFrame with the new 'Status' column
    try:
        # Load the existing workbook with openpyxl
        workbook = load_workbook(excel_file)
        worksheet = workbook[excel_sheet_name]

        # Find the column number for the 'Status' column
        # If 'Status' already exists, use its column. If not, create it as a new column.
        status_col_index = -1
        for col in range(1, worksheet.max_column + 2):
            if worksheet.cell(row=1, column=col).value == 'Status':
                status_col_index = col
                break
        if status_col_index == -1:
            status_col_index = worksheet.max_column + 1
            worksheet.cell(row=1, column=status_col_index).value = 'Status' # Create header

        # Write the status values to the correct cells, starting from the second row
        for index, status in enumerate(all_printers_df['Status'], start=2): # start=2 for Excel's 2nd row
            worksheet.cell(row=index, column=status_col_index, value=status)
        
        # Save the workbook
        workbook.save('Printer_Fleet_Table.xlsx')
        #-------------------------------------------------------------------------------------------
        logger.info(f"Successfully updated 'Printer_Fleet_Table.xlsx' while preserving its format.")
        #-------------------------------------------------------------------------------------------

    except Exception as e:
        if isinstance(e, PermissionError):
            #---------------------------------------------------------------------------------------------------------------------------
            logger.error(f"Updating EXCEL file failed: Could not save 'Printer_Fleet_Table.xlsx'. Please make sure the file is closed.")
            #---------------------------------------------------------------------------------------------------------------------------
            # Raise the expection so that the program_gui receives the error and handles it properly, displaying the pertinent message
            # and GIF on the GUI 
            raise e  
    
        else:
            #------------------------------------------------------------------------------------------
            logger.error(f"Updating EXCEL file failed: An unexpected error occurred while saving: {e}")
            #------------------------------------------------------------------------------------------
            # Raise the expection so that the program_gui receives the error and handles it properly, displaying the pertinent message
            # and GIF on the GUI 
            raise e
        
    finally:
        # Ensure the workbook is closed, releasing the file lock. If the workbook variable is null, then we will avoid crashing the
        # program and allowing tom log the correct message on the program_gui module
        if workbook:
            workbook.close()
            #-------------------------------------------------------------
            logger.info("Workbook closed successfully after updating it.")
            #-------------------------------------------------------------


# CLOSE THE EXCEL FILE IF OPEN
# ----------------------------
def close_excel_file_if_open(excel_file):

    """
    PURPOSE:

    This function robustly checks all running system processes to see if the
    specified Excel file is currently open in any instance of Microsoft Excel.
    If it finds the file open, it forcefully terminates that specific Excel
    process to prevent file access errors ('Permission Denied') later in the
    script. This action is automated and requires no user input.

    ARGUMENTS:

    excel_file = The file path of the Excel workbook to check for. It should be
    a string (e.g., 'Printer_Fleet_Table.xlsx').

    RETURN VALUE:

    This function does not return any value. Its primary effect is terminating
    a process if necessary. It also prints messages to the console indicating
    whether the file was found open and if a process was closed.

    """

    file_name_to_check = os.path.basename(excel_file)
    process_found_and_killed = False
    
    #------------------------------------------------------------
    logger.info(f"Checking if '{file_name_to_check}' is open...")
    #------------------------------------------------------------

    # Iterate over all currently running processes on the system
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # We only care about processes that are Microsoft Excel
            if 'excel' in proc.info['name'].lower():
                # For each Excel process, check the files it has open
                for file_handle in proc.open_files():
                    # Check if the base name of the open file matches our target file
                    if file_name_to_check in os.path.basename(file_handle.path):
                        #------------------------------------------------------------------------------------------------------------
                        logger.warning(f"Found '{file_name_to_check}' open in process '{proc.info['name']}' (PID: {proc.pid}).")
                        logger.info("Attempting to close the process to prevent errors...")
                        #------------------------------------------------------------------------------------------------------------
                        
                        proc.kill()  # Forcefully terminate the process
                        proc.wait()  # Wait for the process to fully close
                        
                        #-----------------------------------------------
                        logger.info("Process closed successfully.")
                        #-----------------------------------------------

                        process_found_and_killed = True
                        break # Exit the inner loop (no need to check other files for this process)
            
            if process_found_and_killed:
                break # Exit the outer loop (no need to check other processes)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # These exceptions happen if a process terminates while we are checking it. It's safe to ignore.
            #-----------------------------------------------
            logger.warning("The EXCEL file was opened and its process terminated while checking if it was open.")
            continue
            
    if not process_found_and_killed:
        #----------------------------------------------------------
        logger.info("File is not currently open. Proceeding.")
        #----------------------------------------------------------
        

# OPEN THE EXCEL AND REPORT FILES
# -------------------------------
def open_output_files(excel_file, report_file):
    """
    PURPOSE:

    This function automatically opens the two final output files for immediate
    user review. It opens the generated HTML report in the default web browser
    and the updated Excel workbook in its default application (e.g., Microsoft
    Excel). It is designed to work on the Windows operating system.

    ARGUMENTS:

    excel_file  = The file path of the Excel workbook that was updated.
    It should be a string.
    
    report_file = The file path of the HTML report that was generated.
    It should be a string.

    RETURN VALUE:

    This function does not return any value. Its primary effect is launching
    external applications to open the specified files. It also prints messages
    to the console indicating its actions or any errors encountered.

    """

    #-----------------------------------------------------------------------------
    logger.info("Opening the generated HTML report and the updated Excel file...")
    #-----------------------------------------------------------------------------
    
    try:
        # Get the full, absolute path to the files for reliability.
        report_path_abs = os.path.abspath(report_file)
        excel_path_abs = os.path.abspath(excel_file)

        # Open the HTML report in a new tab in the default web browser.
        webbrowser.open_new_tab('file://' + report_path_abs)
        
        # Open the Excel file using the default application.
        # os.startfile() is a Windows-specific command.
        os.startfile(excel_path_abs)

        #-----------------------------------------------------------------------------
        logger.info("Files have been opened successfully")
        #-----------------------------------------------------------------------------
        
    except FileNotFoundError as e:
        #-----------------------------------------------------------------------------------------------------
        logger.error(f"Opening the file failed: Could not open a file because it was not found: {e.filename}")
        #-----------------------------------------------------------------------------------------------------
    except Exception as e:
        #-------------------------------------------------------------------------
        print(f"An unexpected error occurred while trying to open the files: {e}")
        #-------------------------------------------------------------------------