# Used to run external commands and shell processes from within Python. We will use it in our script to ping each printer's IP address.
import subprocess

# Stands for "regular expression"; used for advanced string searching and manipulation. Thanks to this module we can extract easily chunks of strings 
# and place them on a separate column as column values (for example, the Base Code column)
import re

#########################################################################################################################################

def printer_ping_check(printers_dataframe, status_column_name, hostname_column_name, ip_address_column_name):

    """
    PURPOSE:
    
    This function runs the PING command for every printer's IP address, and based on the output it determines if the printer
    is online or offline.

    
    ARGUMENTS:

    printers_dataframe = the name of the DataFrame containing all the printer information. It should be a string.

    status_column_name = the name of the column with the status values. It should be a string.

    hostname_column_name = the name of the column with the hostname values. It should be a string.

    ip_address_column_name = then name of the column with the IP addresses. It should be a string.

    
    RETURN VALUE:
    
    The function adds the status of the printer to the Status column of the DataFrame, based on the results of the PING.
    It also prints a counter indicating the progress.
    
    """
    
    # The counter is for testing purposes, when we don't want to iterate over all the IP addresses
    counter = 0
    progress_percentage = 0
    
    # Ensure that all column names are strings
    status_column_name_str = str(status_column_name)
    hostname_column_name_str = str(hostname_column_name)
    ip_address_column_name_str = str(ip_address_column_name)
    
    printers_dataframe[status_column_name_str] = "Unknown"

    for index, row in printers_dataframe.iterrows():

        # --- This section is for the progress counter ---
        ip_address_count = printers_dataframe[ip_address_column_name_str].count()
        counter = counter + 1
        progress_percentage = int((counter / ip_address_count) * 100)


        # Get the value you need to check
        ip_address = row[ip_address_column_name_str]

        # Define the hostname
        hostname = row[hostname_column_name_str]

        # For testing, only iterate over the first 3 items
        #counter += 1
        #if counter >= 4:
            #print("Reached 3 items, stopping.")
            #break # Exit the loop immediately
        
        # Define the "ping" command as a subprocess to run in the Powershell
        pshell_command = f"ping {ip_address}"
        
        # Use a try-except statement to handle errors properly
        try:
            result = subprocess.run(
                ["powershell", "-Command", pshell_command],
                capture_output=True,
                text=True,
                check=True
            )
        
            ping_output = result.stdout
        
            # Find the packet loss percentage using a regular expression
            match = re.search(r"\((\d+)% loss\)", ping_output)
        
            if match:
                # Extract the percentage (the first captured group) and convert to an integer
                loss_percentage = int(match.group(1))
                
                # Conditional statement to check the loss percentage
                if loss_percentage < 100:
                    status = "Online"
                    printers_dataframe.loc[index, 'Status'] = "Online"
                else:
                    status = "Offline"
                    printers_dataframe.loc[index, 'Status'] = "Offline"
            else:
                # Handle cases where the ping output might be malformed or different
                if "TTL=" in ping_output or "time=" in ping_output:
                    status = "Online" # Assume online if we see any successful reply line
                    printers_dataframe.loc[index, 'Status'] = "Online"
                else:
                    status = "Could not determine status"
                    printers_dataframe.loc[index, 'Status'] = "Offline"
            
            print(f"\rCurrent progress: {progress_percentage}%", end="")
        
        except subprocess.CalledProcessError:
            # This block is executed if check=True and the command returns a non-zero exit status (e.g., 1).
            # This is the primary indicator of an offline device that times out.
            print(f"\rCurrent progress: {progress_percentage}%", end="")
            status = "Offline"
            printers_dataframe.loc[index, 'Status'] = "Offline"
            
        except subprocess.TimeoutExpired:
            # This block is executed if the command takes longer than the specified timeout.
            print(f"\rCurrent progress: {progress_percentage}%", end="")
            status = "Offline"
            printers_dataframe.loc[index, 'Status'] = "Offline"
                
        except Exception as e:
            # Catch any other potential errors
            print(f"An unexpected error occurred for IP {ip_address}: {e}")
            print("Error")