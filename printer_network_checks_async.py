# printer_network_checks_async.py

# Used for running network operations concurrently (asynchronously) to speed up the process.
import asyncio  

# Used to check the operating system (e.g., Windows, Linux) to use the correct ping command syntax.
import platform 

# Stands for "regular expression"; used for advanced string searching and manipulation. We use it to determine if the printers are online
# or not by analyzing the text output of each PING subprocess.
import re

#########################################################################################################################################

# COROUTINE WITH SEMAPHORE CONTROL
# --------------------------------
async def _ping_worker(ip_address: str, semaphore: asyncio.Semaphore) -> tuple[str, str]:
    """
    (Internal async worker) Pings a single IP address under semaphore control.
    It returns a tuple containing the IP address and its final status to ensure
    results can be correctly mapped later, regardless of completion order.
    """
    # This 'async with' block ensures that no more than the semaphore's limit
    # of tasks can run this code block at the same time.
    async with semaphore:


        ### <=== DEFINE THE PING COMMAND ===> ###
        # This logic is preserved from your original script.
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '4', ip_address]


        ### <=== CREATE AN ASYNCHRONOUS SUBPROCESS ===> ###
        # Creates an asynchronous subprocess to run the ping command.
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Reads the output from the completed process.
        stdout_bytes, _ = await process.communicate()
        ping_output = stdout_bytes.decode(errors='ignore')
        

        ### <=== DETERMINE STATUS ===> ###
        # Determine if the loss percentage is 100% or less.

        # Initialize the status variable as "Offline"
        status = "Offline"

        # This line is looking for text that looks exactly like (some number% loss), for example, (0% loss) or (100% loss). If it finds 
        # it, the match variable will hold a special match object; otherwise, match will be None.
        match = re.search(r"\((\d+)% loss\)", ping_output)
        if match:
            loss_percentage = int(match.group(1))
            if loss_percentage < 100:
                status = "Online"
        elif "TTL=" in ping_output or "time=" in ping_output:
            status = "Online"
        
        # This return value is crucial for the dictionary mapping solution.
        return (ip_address, status)


# RUN CHECK AND GENERATE UPDATES AND REPORTS
# ------------------------------------------
async def ping_printers_async(printers_dataframe, ip_address_column_name_str, progress_callback=None):
    """
    PURPOSE:

    This function runs the PING command for every printer's IP address, and based
    on the output it determines if the printer is online or offline. This version
    runs the pings concurrently for high speed, while preserving the original
    progress counter logic.
    

    ARGUMENTS:

    printers_dataframe = the name of the DataFrame containing all the printer information.

    status_column_name_str = the name of the column with the status values.

    hostname_column_name_str = the name of the column with the hostname values.

    ip_address_column_name_str = the name of the column with the IP addresses.

    
    RETURN VALUE:

    This function returns a dictionary mapping each IP Address to its final 'Online'
    or 'Offline' status. It also prints a counter indicating the progress, exactly
    like the original function.
    """


    ### <=== LIMIT THE CONCURRENT PING PROCESSES ===>
    CONCURRENT_LIMIT = 50 # Sets a safe limit on how many pings run at once.
    semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)

    ip_list = printers_dataframe[ip_address_column_name_str].tolist()


    ### <=== UPDATE PROGRESS ===> ###
    # Get the total count of printers being checked by counting the total number of IP addresses
    ip_address_count = printers_dataframe[ip_address_column_name_str].count()

    # Initialize the progress counter
    counter = 0

    def update_progress():
        """This nested function contains your original progress counter logic."""
        nonlocal counter
        counter = counter + 1
        progress_percentage = int((counter / ip_address_count) * 100)
        print(f"\rCurrent progress: {progress_percentage}%", end="")

        # The callback function is called, passing this integer as its argument. This sends the current percentage value to the Worker
        # process, so that the progress can be displayed in the GUI.
        if progress_callback:
            progress_callback(progress_percentage)

    print("\n===================================================================")
    print(f"Starting to ping {ip_address_count} devices with a concurrency limit of {CONCURRENT_LIMIT}...")
    

    ### <=== RUN PINGS ===> ###
    # Prepares all the asynchronous tasks to be run.
    tasks = [_ping_worker(ip, semaphore) for ip in ip_list]
    
    # This dictionary will store the results safely, using the IP as a key.
    status_results_dict = {}
    
    # asyncio.as_completed yields tasks as they finish, which is perfect for a live progress bar.
    for task in asyncio.as_completed(tasks):
        # The result is a tuple, e.g., ('192.168.1.10', 'Online')
        ip, status = await task
        # The result is stored in the dictionary, ensuring no data is scrambled.
        status_results_dict[ip] = status
        # This calls your original counter logic as each task completes.
        update_progress()

    print("\nAll ping checks are complete.")
    print("===================================================================")
    
    # This dictionary is returned to the main script so it can safely map the results.
    return status_results_dict