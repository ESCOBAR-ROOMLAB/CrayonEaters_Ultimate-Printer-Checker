# The core library for creating static, animated, and interactive visualizations. This will allow us to create visualizations and improve 
# our final report.
import matplotlib.pyplot as plt

# A high-level data visualization library based on matplotlib, for attractive statistical graphics. It will improve our plots.
import seaborn as sns

# For operations with the DataFrame
import pandas as pd

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

log_file_path = 'execution_logs.log'

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

# GENERATE PLOTS
# --------------
def generate_printer_bar_chart(printers_dataframe, base_code_column_name, status_column_name):

    """
    PURPOSE
    -------
    Generates a bar chart that visually represents the number of 'Online' and 'Offline'
    printers for each base location. This provides a high-level overview of network
    health across different sites. The function uses seaborn and matplotlib to create
    the plot, adds numerical labels on top of each bar for exact counts, and saves the
    final chart as an image file.

    
    ARGUMENTS
    ---------
    printers_dataframe (pd.DataFrame): The DataFrame containing the printer data. It must include 
    the columns specified by the other arguments.

    base_code_column_name (str): The name of the column in the DataFrame that contains the base location codes.

    status_column_name (str): The name of the column in the DataFrame that contains the 'Online' or 'Offline' 
    status for each printer.

        
    RETURN VALUE
    ------------
    Returns the absolute file path (str) to the newly created PNG image of the bar
    chart. This path can then be used to embed the image in other documents, such as
    an HTML report.
    """
     
    ### <=== BAR CHART GENERATION (with numerical labels) ===> ###
    # Define the standard size
    chart_figsize = (10, 6) 

    # Create the figure and axes objects
    fig, ax = plt.subplots(figsize=chart_figsize)

    # We'll use the seaborn
    sns.countplot(
        data=printers_dataframe, 
        x=str(base_code_column_name), 
        hue=str(status_column_name), 
        ax=ax, 
        palette={'Online': '#2ecc71', 'Offline': '#e74c3c'}
    )

    # Loop through the bars to add the count on top
    # ax.patches contains the geometric shapes of the bars
    for p in ax.patches:
        # Get the height of the bar (which is the count)
        height = p.get_height()
        
        # Check if height is NaN or zero to avoid printing '0' on empty bars
        if pd.isna(height) or height == 0:
            continue
        
        # The 'annotate' function places text on the plot
        ax.annotate(
            f'{int(height)}',                           # The text to display (as an integer)
            (p.get_x() + p.get_width() / 2., height),   # The (x, y) coordinate to place the text
            ha='center',                                # Horizontal alignment: center
            va='center',                                # Vertical alignment: center
            xytext=(0, 5),                              # Offset the text 5 points vertically
            textcoords='offset points'                  # Use an offset in points
        )

    # Set labels on the 'ax' object
    ax.set_xlabel('Base Code')
    ax.set_ylabel('Number of Printers')
    ax.tick_params(axis='x', rotation=45)

    # Let Matplotlib automatically calculate the tightest layout to fill the figure
    fig.tight_layout(pad=0.5)

    ### <=== SAVE THE FILE AND CLOSE ===> ###
    # Save the figure object
    bar_chart_file_path = common_helper_functions.get_absolute_path('images\printer_status_by_base_code_bar-chart.png')
    fig.savefig(bar_chart_file_path, bbox_inches='tight', dpi=300)

    # Close the plot
    plt.close(fig)

    #---------------------------------------------------------------------------------------
    logger.info(f"Bar chart with labels successfully saved in path '{bar_chart_file_path}'")
    #---------------------------------------------------------------------------------------

    # Return the absolute file path for the plot
    return bar_chart_file_path


def generate_printer_pie_chart(printers_dataframe, status_column_value):


    """
    PURPOSE
    -------
    Generates a pie chart that displays the overall distribution of 'Online' versus
    'Offline' printers across all sites. The chart shows both the absolute number of
    printers and their corresponding percentage of the total. The function uses a
    custom color map to ensure consistent coloring and saves the resulting chart as a
    high-resolution PNG image file.

    
    ARGUMENTS
    ---------
    printers_dataframe (pd.DataFrame): The DataFrame containing the printer data, which must include the status column.
    
    status_column_value (str): The name of the column in the DataFrame that holds the 'Online' or 'Offline' status for each printer.

        
    RETURN VALUE
    ------------
    Returns the absolute file path (str) to the newly created PNG image of the pie
    chart. This path can be used to embed the image into other reports or documents.
    """

    # Define a standard size for all report charts
    chart_figsize = (10, 6)

    # Create a figure AND an axes object (the subplot)
    fig, ax = plt.subplots(figsize=chart_figsize)

    # Ensure that the name of the column for which we will plot values is a string
    status_column_value_str = str(status_column_value)

    # Prepare the data:
    status_counts = printers_dataframe[status_column_value_str].value_counts()

    # Define a color for each specific status label.
    color_map = {'Online': '#2ecc71', 'Offline': '#e74c3c'}

    # Create a list of colors that is ordered to perfectly match the 'status_counts' labels. This ensures 'Offline' is always red, 
    # regardless of its position in the data.
    ordered_colors = [color_map.get(label, '#bdc3c7') for label in status_counts.index] #The '#bdc3c7' is a neutral grey fallback for any unexpected status.

    def make_autopct(values):
        """
        This is a "function factory". Its only job is to create and return
        another function that is configured to format the labels on a pie chart.
        This pattern (a function inside a function) is called a closure.
        """

        # Define the inner function that will actually be used by Matplotlib.
        # This inner function will have access to the 'values' variable from its parent.
        def my_autopct(pct):
            """
            This is the actual labeling function that Matplotlib will call for each slice.
            Matplotlib provides the percentage of the slice as the 'pct' argument.
            """

            # Calculate the total sum of all the pie slices.
            # It can see the 'values' variable from the outer function's scope.
            total = sum(values)

            # Calculate the absolute number (the raw count) for this specific slice
            # by converting the percentage back from the total.
            val = int(round(pct * total / 100.0))

            # Create and return the final formatted string to be displayed on the slice.
            # It includes the absolute number and the percentage on a new line.
            # For example: "15\n(75.0%)"
            return f'{val}\n({pct:.1f}%)'

        # The outer function returns the inner function itself.
        # This returned function is now "primed" and ready for Matplotlib to use.
        return my_autopct

    # Draw the pie chart on the 'ax' object, not using 'plt'
    ax.pie(
        status_counts,
        labels=status_counts.index,
        autopct=make_autopct(status_counts),
        startangle=90,
        colors=ordered_colors,
        textprops={'fontsize': 14}
    )

    # Let Matplotlib automatically calculate the tightest layout to fill the figure
    fig.tight_layout(pad=0.5)

    # This command ensures the pie is drawn as a circle, but now it's contained within the subplot, not dominating the whole figure.
    ax.axis('equal') 

    ### <=== SAVE THE FILE AND CLOSE ===> ###
    # Save the figure object
    pie_chart_file_path = common_helper_functions.get_absolute_path('images\printer_status_pie-chart.png')
    fig.savefig(pie_chart_file_path, bbox_inches='tight', dpi=300)

    # Close the plot
    plt.close(fig)

    #---------------------------------------------------------------------------
    logger.info(f"Pie chart successfully saved in path '{pie_chart_file_path}'")
    #---------------------------------------------------------------------------

    return pie_chart_file_path