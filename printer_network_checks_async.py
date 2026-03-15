# printer_network_checks_async.py

# Used for running network operations concurrently (asynchronously) to speed up the process.
import asyncio  

# Used to check the operating system (e.g., Windows, Linux) to use the correct ping command syntax.
import platform 

# Stands for "regular expression"; used for advanced string searching and manipulation. Thanks to this module we can extract easily chunks of strings 
# and place them on a separate column as column values (for example, the Base Code column)
import re

#########################################################################################################################################

async def _ping_worker(ip_address: str, semaphore: asyncio.Semaphore) -> str:
    """
    (Internal Worker) Asynchronously pings a single IP under the control of a semaphore.
    """
    # Use an 'async with' block to safely acquire the semaphore.
    # The code inside this block will only run when a "slot" is available.
    # The semaphore is automatically released when the block is exited.
    async with semaphore:
        # Determine the correct command-line parameter for the ping command based on the OS.
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        # Construct the full ping command as a list of arguments.
        command = ['ping', param, '4', ip_address]

        # Asynchronously create and start a new subprocess to run the ping command.
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Asynchronously wait for the subprocess to complete and read all of its output.
        stdout_bytes, _ = await process.communicate()
        # Decode the captured output from a 'bytes' object into a regular 'string'.
        ping_output = stdout_bytes.decode(errors='ignore')
        
        # Set a default status of "Offline".
        status = "Offline"

        # Use a regular expression to search the ping output for the packet loss percentage.
        match = re.search(r"\((\d+)% loss\)", ping_output)
        
        # Check if the regular expression found a match in the output text.
        if match:
            loss_percentage = int(match.group(1))
            if loss_percentage < 100:
                status = "Online"
        # As a fallback, check for other signs of a successful ping.
        elif "TTL=" in ping_output or "time=" in ping_output:
            status = "Online"
            
        # Return the final determined status for this single IP address.
        return status

async def ping_printers_async(printers_dataframe, status_column_name_str, hostname_column_name_str, ip_address_column_name_str):
    """
    Asynchronously pings all printers, safely limiting the number of concurrent pings
    using a semaphore.
    """
    # Define the maximum number of concurrent ping tasks. 50 is a safe starting point.
    CONCURRENT_LIMIT = 50
    # Create the semaphore "bouncer" with the specified limit.
    semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)

    # Get the list of IP addresses from the DataFrame.
    ip_list = printers_dataframe[ip_address_column_name_str].tolist()
    total_ips = len(ip_list)
    completed_count = 0

    def update_progress():
        """Nested helper function to calculate and display progress."""
        nonlocal completed_count
        completed_count += 1
        progress_percentage = int((completed_count / total_ips) * 100)
        print(f"\rCurrent progress: {progress_percentage}% ({completed_count}/{total_ips})", end="")

    print(f"Starting to ping {total_ips} devices with a concurrency limit of {CONCURRENT_LIMIT}...")
    
    # Create a list of tasks, passing the semaphore to each worker.
    tasks = [_ping_worker(ip, semaphore) for ip in ip_list]
    
    results = []
    # Use asyncio.as_completed to get results as they finish.
    for task in asyncio.as_completed(tasks):
        result = await task
        results.append(result)
        # Update the on-screen counter as each task completes.
        update_progress()

    print("\nAll ping checks are complete.")
    
    # Update the DataFrame with the collected results.
    printers_dataframe[status_column_name_str] = results