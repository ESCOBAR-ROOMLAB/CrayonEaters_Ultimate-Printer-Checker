# Used to encode and decode binary data (like images) into ASCII text format.
import base64

# We need this one to be able to query the current date and store it in a variable.
from datetime import date

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

# GENERATE HTML REPORT
# --------------------
def generate_printer_report_in_html(report_file, excel_sheet_name, printers_dataframe, pie_chart_image, bar_chart_image):

    """
    PURPOSE
    -------
    Generates a complete, self-contained HTML report detailing the printer fleet status.
    This function takes a DataFrame and chart images, converts the images to Base64
    to embed them directly into the HTML, and formats the data into structured, styled
    sections. It creates dedicated sections for "Offline Printers" and "Special Notes,"
    grouping the data by base code for improved readability. The final HTML string,
    complete with CSS styling, is then written to a local file.

    
    ARGUMENTS
    ---------
    report_file (str): The file path where the generated HTML report will be saved.

    excel_sheet_name (str): The name of the exercise or location, which is used as the
    main title for the report.
    printers_dataframe (pd.DataFrame): The DataFrame containing all the printer information,
    including status, hostname, and special notes.

    pie_chart_image (str): The file path to the PNG image of the status pie chart.

    bar_chart_image (str): The file path to the PNG image of the status bar chart.

    
    RETURN VALUE
    ------------
    None. The function's primary outcome is the creation and saving of the HTML report
    file to the specified path.
    """
        
    # Get the current date and store it in a variable
    current_date = date.today()

    ### <=== HELPER FUNCTION TO ENCODE IMAGES ===> ###
    # This function reads an image file and converts it into a text string
    # that can be embedded directly into the HTML file.
    def image_to_base64_string(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    ### <=== ENCODING PLOT IMAGES ===> ###
    try:
        pie_chart_base64 = image_to_base64_string(pie_chart_image)
        bar_plot_base64 = image_to_base64_string(bar_chart_image)
        #--------------------------------------------------------
        logger.info("Plot images have been successfully encoded")
        #--------------------------------------------------------
    except FileNotFoundError as e:
        #------------------------------------------------------------------------------------------------------------------------------------------
        logger.error(f"Encoding plot images failed: Could not find an image file. Make sure your script is in the same folder as your PNG images.")
        logger.error(f"Encoding plot images failed: File not found: {e.filename}")
        #------------------------------------------------------------------------------------------------------------------------------------------
        exit() # Stop the script if an image is missing

   
    # First, lets define some of the text we will include in the report. In this case, we want to specify the reason why the printers 
    # whose status is Offline and have a Special Note are not reachable in the network. Some printers may have a Special  Note inputted 
    # on the EXCEL tracker. Also, we want to include a section listing the Offline printers by site / base.

    ### <=== FILTER FOR ROWS THAT HAVE A SPECIAL NOTE ===> ###
    printers_with_notes = printers_dataframe[printers_dataframe['Special Notes'].notna()].copy()

    ### <=== BUILD THE HTML CONTENT WITH GROUPING ===> ###
    if not printers_with_notes.empty:
        # Use groupby to process each 'base_code' separately
        printers_with_notes_grouped_by_base = printers_with_notes.groupby('Base Code') 
    
        # A list to hold the HTML for each group
        all_groups_html = []

        for site_code, group_df in printers_with_notes_grouped_by_base:
            # Start each group with the site code in bold
            group_html = [f"<b>{site_code}</b>"]
        
            # Create the list of "hostname: note" strings for the current group
            notes_list = [
                f"<i>{row['Hostname']}</i>: {row['Special Notes']}" 
                for index, row in group_df.iterrows()
            ]
        
            # Add the notes to the group's HTML
            group_html.extend(notes_list)
        
            # Join the lines for this group and add it to our main list
            all_groups_html.append("<br>".join(group_html))

        # Join all the group sections together, separated by a blank line (<br><br>)
        html_special_notes_content = "<br><br>".join(all_groups_html)

    else:
        html_special_notes_content = "No special notes for any printers this week." 

    ### <=== BUILDING THE HTML FOR THE OFFLINE PRINTERS SECTION ===> ###
    offline_printers_df = printers_dataframe[printers_dataframe['Status'] == 'Offline']

    if not offline_printers_df.empty:
        # Start the main container for the entire section
        offline_printers_html = '<div class="offline-section">'
        offline_printers_html += '<h3>Offline Printers by Site</h3>'
        
        # Start the flexbox grid container
        offline_printers_html += '<div class="offline-grid-container">'

        grouped_by_site = offline_printers_df.groupby('Base Code')
        
        # Loop through each site and create a column for it
        for site_code, group_df in grouped_by_site:
            # Each site's list is now a column in the grid
            offline_printers_html += '<div class="offline-grid-column">'
            offline_printers_html += f"<b>{site_code}</b>"
            offline_printers_html += "<ul>"
            for hostname in group_df['Hostname']:
                offline_printers_html += f"<li>{hostname}</li>"
            offline_printers_html += "</ul>"
            offline_printers_html += '</div>' # Close the column div
            
        # Close the grid container div
        offline_printers_html += '</div>'
        # Close the main section div
        offline_printers_html += '</div>'

    ### <=== HTML CONTENT ===> ###
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Printer Status Report</title>
        <style>
            /* General page styling */
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                color: #333;
            }}
            h1, h2 {{
                color: #2c3e50; /* A darker blue for headings */
                border-bottom: 2px solid #3498db; /* A blue bottom border */
                padding-bottom: 8px;
            }}
            p {{
                line-height: 1.6;
            }}

            /* --- Image Container for side-by-side layout --- */
            .image-container {{
                display: flex; /* Use flexbox to align items horizontally */
                justify-content: space-around; /* Distribute space around items */
                align-items: flex-start; /* Align items to the top */
                gap: 20px; /* The space between the two images */
                margin-top: 20px;
                padding: 10px;
                background-color: #f8f9fa; /* A very light grey background */
                border: 1px solid #e9ecef; /* A light border */
                border-radius: 8px; /* Rounded corners */
            }}

            /* --- Styling for each image 'box' --- */
            .image-box {{
                width: 48%;
                text-align: center;
            }}
            
            /* This is the new container for the chart image */
            .chart-display {{
                width: 100%;
                /* This maintains a consistent aspect ratio (height is 60% of width) */
                padding-top: 60%; 
                position: relative; /* Required for the aspect ratio trick */
                background-size: contain; /* Scales the image down to fit */
                background-position: center; /* Centers the image */
                background-repeat: no-repeat; /* Prevents tiling */
                border: 1px solid #ccc;
                border-radius: 4px;
            }}

            .image-box h3 {{
                color: #34495e;
                margin-bottom: 15px;
            }}


            /* --- Style for the notes title --- */
            .notes-title {{
                display: inline-block;
                border-bottom: 1px solid #bdc3c7; /* A light grey underline */
                padding-bottom: 5px;             /* A little space between text and line */
                margin-top: 30px;                /* Add some space above the title */
            }}

            /* --- Styling for the Offline Printers section --- */
            .offline-section {{
                margin-top: 30px;
                padding: 15px;
                background-color: #fff9f9; /* A very light red background */
                border: 1px solid #f2dede;   /* A light red border */
                border-radius: 8px;
            }}
            .offline-section h3 {{
                color: #a94442; /* A darker red for the title */
                margin-top: 0;
            }}
            .offline-section ul {{
                list-style-type: square;
                padding-left: 20px;
            }}
            .offline-section li {{
                margin-bottom: 5px;
            }}

            /* --- Styling for the multi-column grid layout for the Offline Printers section --- */
            .offline-grid-container {{
                display: flex;
                flex-wrap: wrap; /* Allows items to wrap to the next line */
                gap: 20px;       /* The space between the columns */
            }}
            .offline-grid-column {{
                flex: 1 1 22%; /* Flex-grow, flex-shrink, and base width (approx 25% minus gap) */
                min-width: 200px; /* Prevents columns from becoming too narrow */
            }}

            
        </style>
    </head>
    <body>

        <h1>{excel_sheet_name} Printer Status Report -- {current_date}</h1>
        <p>
            Report of the Printer Fleet status, detailing both the overall distribution and a breakdown by device base code.
        </p>

        <!-- The container holding both images -->
        <div class="image-container">

            <!-- Box for the Pie Chart -->
            <div class="image-box">
                <h3>Overall Printer Status</h3>
                <!-- The image is now a background on this div -->
                <div class="chart-display" style="background-image: url('data:image/png;base64,{pie_chart_base64}');">
                </div>
            </div>

            <!-- Box for the Bar Plot -->
            <div class="image-box">
                <h3>Status by Base Code</h3>
                <!-- The image is now a background on this div -->
                <div class="chart-display" style="background-image: url('data:image/png;base64,{bar_plot_base64}');">
                </div>
            </div>

        </div>

         <!-- The new Offline Printers section will be injected here -->
        {offline_printers_html}

        <h3 class="notes-title">Printers Special Notes</h3>
        <p>
            <!-- Special notes regarding offline printers will be detailed here. -->
            {html_special_notes_content}
        </p>
        
    </body>
    </html>
    """

    # Write the HTML content to a file
    file_name = report_file
    with open(file_name, 'w') as f:
        f.write(html_content)

    #-----------------------------------------------------------------------
    logger.info(f"Report successfully generated and saved as '{file_name}'")
    #-----------------------------------------------------------------------