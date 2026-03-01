# Used to encode and decode binary data (like images) into ASCII text format.
import base64

# We need this one to be able to query the current date and store it in a variable.
from datetime import date

#########################################################################################################################################

def generate_printer_report_in_html(printers_dataframe, pie_chart_image, bar_chart_image):

    """
    PURPOSE:
    
    This function generates the printer report in HTML.

    
    ARGUMENTS:

    printers_dataframe = the name of the DataFrame containing all the printer information. It should be a string.

    pie_chart_image = the name of the PNG image that contains the PIE CHART of the printer status.

    bar_chart_image = the name of the PNG image that contains the BAR CHART of the printer status per base code.


    RETURN VALUE:
    
    The function creates an HTML report and saves it locally, adding the current date to the title.
    
    """
        
    # Get the current date and store it in a variable
    current_date = date.today()

    # --- Helper function to encode images ---
    # This function reads an image file and converts it into a text string
    # that can be embedded directly into the HTML file.
    def image_to_base64_string(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    # --- Encode your images ---
    try:
        pie_chart_base64 = image_to_base64_string(pie_chart_image)
        bar_plot_base64 = image_to_base64_string(bar_chart_image)
    except FileNotFoundError as e:
        print(f"Error: Could not find an image file. Make sure your script is in the same folder as your PNG images.")
        print(f"File not found: {e.filename}")
        exit() # Stop the script if an image is missing

   
    # First, lets define some of the text we will include in the report. In this case, we want to specify the reason why the printers 
    # whose status is Offline and have a Special Note are not reachable in the network. Any unreachable printers should have a Special 
    # Note inputted on the 'printers_data' dictionary.

    # --- Filter for rows that have a special note ---
    printers_with_notes = printers_dataframe[printers_dataframe['Special Notes'].notna()].copy()

    # --- Build the HTML content with grouping ---
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
        html_special_notes_content = "No special notes for any offline printers this week." 

    # Now we can define the report and its generation as an HTML file.
    # --- Define the NEW HTML structure for the report ---
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

            /* --- NEW: Image Container for side-by-side layout --- */
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

            /* --- REVISED: Styling for each image 'box' --- */
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


            /* --- NEW: Style for the notes title --- */
            .notes-title {{
                display: inline-block;
                border-bottom: 1px solid #bdc3c7; /* A light grey underline */
                padding-bottom: 5px;             /* A little space between text and line */
                margin-top: 30px;                /* Add some space above the title */
            }}
            
        </style>
    </head>
    <body>

        <h1>Printer Status Report - {current_date}</h1>
        <p>
            Weekly report of the MCE Printer Fleet status, detailing both the overall distribution and a breakdown by device base code.
        </p>

        <!-- REVISED: The container holding both images -->
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


        <h3 class="notes-title">Offline Printers Special Notes</h3>
    
        <p>
            <!-- Special notes regarding offline printers will be detailed here. -->
            {html_special_notes_content}
        </p>
        
    </body>
    </html>
    """

    # --- Write the HTML content to a file (unchanged) ---
    file_name = 'Weekly_Printer_Report.html'
    with open(file_name, 'w') as f:
        f.write(html_content)

    print(f"Report successfully generated and saved as '{file_name}'")