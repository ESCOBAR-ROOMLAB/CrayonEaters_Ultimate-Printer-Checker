# Used to create the DataFrame to store the printer fleet information
import pandas as pd

# Use openpyxl to load the existing Printer_Fleet_Table.xlsx into memory, keeping all your colors and rules.
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows

#########################################################################################################################################

def create_printers_dataframe(excel_sheet_name):

    """
    PURPOSE:

    This function reads a specific sheet from the 'Printer_Fleet_Table.xlsx' file
    into a pandas DataFrame. It also validates that the file exists and that
    it contains an 'IP Address' column before returning the data.

    ARGUMENTS:

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
        all_printers_df = pd.read_excel('Printer_Fleet_Table.xlsx', sheet_name=excel_sheet_name)
    except FileNotFoundError:
        print(f"ERROR: The file 'Printer_Fleet_Table.xlsx' was not found in this directory.")
        exit()
    except Exception as e:
        print(f"An error occurred while reading the Excel file: {e}")
        exit()

    # Check if the required column exists
    if 'IP Address' not in all_printers_df.columns:
        print("ERROR: A column named 'IP Address' was not found in the Excel file.")
        exit()
    
    return all_printers_df

def update_excel_table_status(excel_sheet_name, all_printers_df):
    """
    PURPOSE:

    This function updates an existing Excel file ('Printer_Fleet_Table.xlsx') with
    new status data from a pandas DataFrame, while carefully preserving all existing
    formatting like colors, conditional rules, and column widths. It uses the
    openpyxl library to load the workbook, find or create a 'Status' column,
    write the new data cell by cell, and then save the changes.

    ARGUMENTS:

    excel_sheet_name = the name of the sheet within the Excel workbook that needs
                    to be updated. It should be a string.
                    
    all_printers_df  = the pandas DataFrame containing the full dataset, including
                    the 'Status' column with the updated online/offline values
                    that will be written to the file.

    RETURN VALUE:

    This function does not return any value. Its primary effect is modifying the
    'Printer_Fleet_Table.xlsx' file by adding or updating the 'Status' column.
    It also prints messages to the console indicating the progress and the final
    success or failure of the operation.

    """

    # Assuming 'printers_df' is your DataFrame with the new 'Status' column
    print("\nOpening Excel file to update it while preserving formatting...")

    try:
        # Load the existing workbook with openpyxl
        workbook = load_workbook('Printer_Fleet_Table.xlsx')
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
        print(f"Successfully updated 'Printer_Fleet_Table.xlsx' while preserving its format.")

    except PermissionError:
        print(f"\nERROR: Could not save 'Printer_Fleet_Table.xlsx'. Please make sure the file is closed.")
    except Exception as e:
        print(f"\nAn unexpected error occurred while saving: {e}")
    
    finally:
        # Ensure the workbook is closed, releasing the file lock.
        if workbook:
            workbook.close()
            print("Workbook closed successfully.")