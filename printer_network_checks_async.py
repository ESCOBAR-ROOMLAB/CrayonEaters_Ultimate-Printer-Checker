# Used for running network operations concurrently (asynchronously) to speed up the process.
import asyncio 

# This module allows Python to create and interact with additional operating system processes, such as running command-line tools like 'ping'.
# While asyncio handles the asynchronous execution of these processes, we import this module specifically to access the 'subprocess.CREATE_NO_WINDOW' 
# constant. This is a special flag, used only on the Windows operating system, which is passed to the process creation call to prevent a new console window 
# from flashing open for each 'ping' command, ensuring a much cleaner and less distracting user experience.
import subprocess

# Used to check the operating system (e.g., Windows, Linux) to use the correct ping command syntax.
import platform 

# Stands for "regular expression"; used for advanced string searching and manipulation. We use it to determine if the printers are online
# or not by analyzing the text output of each PING subprocess.
import re

# This module will provide us useful helper functions
import common_helper_functions

# This module allows us to log errors and execution output
import logging

# This module allows us to rotate the logging file
from logging.handlers import RotatingFileHandler

########################################################################################################################################

# SETUP LOGGING
# -------------
logger = logging.getLogger(__name__) # use the module's name as the name in the logs
logger.setLevel(logging.INFO) # set the logging level

log_file_path = common_helper_functions.get_absolute_path('execution_logs.log')

# Use RotatingFileHandler.
# maxBytes: 5 * 1024 * 1024 = 5 MB
# backupCount=0: When the file is full, delete it and start a new one.
handler = RotatingFileHandler(
    log_file_path, maxBytes=5*1024*1024, backupCount=0
)

# Format the logs and set it for the HANDLER
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s") 
handler.setFormatter(formatter)

# Add the formatted HANDLER to the logger
logger.addHandler(handler)

########################################################################################################################################

# COROUTINE WITH SEMAPHORE CONTROL
# --------------------------------
async def _ping_worker(ip_address: str, semaphore: asyncio.Semaphore) -> tuple[str, str]:
   
    """
    PURPOSE
    -------
    Acts as a single, concurrent worker responsible for pinging one IP address. This
    internal asynchronous function is designed to be run as part of a larger, managed
    group of tasks. It uses a provided `Semaphore` to limit the number of simultaneous
    ping operations, preventing system resource exhaustion. The function constructs and
    executes the appropriate `ping` command for the host operating system, captures the
    output, and parses it to determine if the device is "Online" or "Offline".

    
    ARGUMENTS
    ---------
    ip_address (str): The IP address of the target device to be pinged. semaphore (asyncio.Semaphore): 
    An asyncio semaphore instance that is used to limit the number of concurrent executions of this worker.

    
    RETURN VALUE
    ------------
    Upon successful completion, it returns a tuple containing the original `ip_address` (str)
    and its determined `status` (str), which will be either "Online" or "Offline".
    If an exception occurs, an error is logged, and the function's execution is terminated
    for that specific IP.
    """
   
    try:
        # This 'async with' block ensures that no more than the semaphore's limit
        # of tasks can run this code block at the same time.
        async with semaphore:


            ### <=== DEFINE THE PING COMMAND ===> ###
            # This logic is preserved from your original script.
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '4', ip_address]


            ### <=== CREATION FLAG ARGUMENT FOR WINDOWS ===> ###
            # Define a variable to hold the special Windows flag.
            # This flag tells Windows to not create a console window for the subprocess.
            creation_flags = 0
            if platform.system() == "Windows":
                creation_flags = subprocess.CREATE_NO_WINDOW


            ### <=== CREATE AN ASYNCHRONOUS SUBPROCESS ===> ###
            # Creates an asynchronous subprocess to run the ping command.
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                creationflags=creation_flags
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
        
    except Exception as e:
        #------------------------------------------------
        logger.error(f"Failed to ping {ip_address}: {e}")
        #------------------------------------------------


# RUN CHECK AND GENERATE UPDATES AND REPORTS
# ------------------------------------------
async def ping_printers_async(printers_dataframe, progress_callback=None):

    """
    PURPOSE
    -------
    Concurrently pings a list of printer IP addresses extracted from a DataFrame to
    efficiently determine their online or offline status. This function is optimized for
    speed by running multiple ping operations at the same time, while using a semaphore
    to prevent overwhelming the network or system. It provides real-time progress
    updates both to the console and through an optional callback function, making it
    suitable for integration with a GUI.

    
    ARGUMENTS
    ---------
    printers_dataframe (pd.DataFrame): The DataFrame containing all printer information, 
    from which the IP addresses will be sourced.
    
    progress_callback (callable, optional): An optional function that is called after each ping completes. 
    It should accept a single integer argument representing the overall progress percentage.

        
    RETURN VALUE
    ------------
    Returns a dictionary that maps each IP address (str) to its final determined
    status (str), which will be either 'Online' or 'Offline'. This structure allows the
    calling function to safely update statuses without worrying about the asynchronous
    completion order.
    """

    ### <=== LIMIT THE CONCURRENT PING PROCESSES ===>
    CONCURRENT_LIMIT = 50 # Sets a safe limit on how many pings run at once.
    semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)

    ip_list = printers_dataframe['IP Address'].tolist()


    ### <=== UPDATE PROGRESS ===> ###
    # Get the total count of printers being checked by counting the total number of IP addresses
    ip_address_count = printers_dataframe['IP Address'].count()

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

    #------------------------------------------------------------------------------------------------------------
    logger.info(f"Starting to ping {ip_address_count} devices with a concurrency limit of {CONCURRENT_LIMIT}...")
    #------------------------------------------------------------------------------------------------------------
    

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
    
    # This dictionary is returned to the main script so it can safely map the results.
    return status_results_dict