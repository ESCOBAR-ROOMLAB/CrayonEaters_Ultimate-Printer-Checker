# The core library for creating static, animated, and interactive visualizations. This will allow us to create visualizations and improve 
# our final report.
import matplotlib.pyplot as plt

# A high-level data visualization library based on matplotlib, for attractive statistical graphics. It will improve our plots.
import seaborn as sns

# For operations with the DataFrame
import pandas as pd

# Import the os module to handle file paths
import os

#########################################################################################################################################

def generate_printer_bar_chart(printers_dataframe, base_code_column_name, status_column_name):

    """
    PURPOSE:
    
    This function generates a bar plot that represents the number of printers online / offline per base, to identify at a high level
    any network issues with the assets.

    
    ARGUMENTS:

    printers_dataframe = the name of the DataFrame containing all the printer information. It should be a string.

    status_column_name = the name of the column with the status values. It should be a string.

    base_code_column_name = the name of the column with the Base Code values. It should be a string.

    
    RETURN VALUE:
    
    The function saves the bar plot as an image in PNG, to be later imported to the final report.
    
    """
     
    ### <=== BAR CHART GENERATION (with numerical labels) ===> ###
    # Define the standard size
    chart_figsize = (10, 6) 

    # Create the figure and axes objects
    fig, ax = plt.subplots(figsize=chart_figsize)

    # --- Your existing bar chart plotting code ---
    # We'll use the same seaborn example as before
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
            f'{int(height)}', # The text to display (as an integer)
            (p.get_x() + p.get_width() / 2., height), # The (x, y) coordinate to place the text
            ha='center',        # Horizontal alignment: center
            va='center',        # Vertical alignment: center
            xytext=(0, 5),      # Offset the text 5 points vertically
            textcoords='offset points' # Use an offset in points
        )
    # ---------------------------------------------------------

    # Set labels on the 'ax' object
    ax.set_xlabel('Base Code')
    ax.set_ylabel('Number of Printers')
    ax.tick_params(axis='x', rotation=45)

    # Let Matplotlib automatically calculate the tightest layout to fill the figure
    fig.tight_layout(pad=0.5)
    
    ### <=== SET THE OUTPUT FOLDER ===> ###
    output_folder = "images"

    ### <=== SAVE THE FILE AND CLOSE ===> ###
    # Save the figure object
    bar_chart_file_name = 'printer_status_by_base_code_bar-chart.png'
    full_save_path = os.path.join(output_folder, bar_chart_file_name)
    fig.savefig(full_save_path, bbox_inches='tight', dpi=300)

    # Close the plot
    plt.close(fig)

    print(f"\nBar chart with labels successfully saved as '{bar_chart_file_name}'")
    return full_save_path


def generate_printer_pie_chart(printers_dataframe, status_column_value):


    """
    PURPOSE:
    
    This function generates a pie plot that represents the percentage and number of printers online / offline in total, across all bases.

    
    ARGUMENTS:

    printers_dataframe = the name of the DataFrame containing all the printer information. It should be a string.

    status_column_name = the name of the column with the status values. It should be a string.

    
    RETURN VALUE:
    
    The function saves the pie plot as an image in PNG, to be later imported to the final report.
    
    """

    # --- PIE CHART GENERATION (REVISED) ---

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
        def my_autopct(pct):
            total = sum(values)
            val = int(round(pct * total / 100.0))
            return f'{val}\n({pct:.1f}%)'
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

    ### <=== SET THE OUTPUT FOLDER ===> ###
    output_folder = "images"

    ### <=== SAVE THE FILE AND CLOSE ===> ###
    # Save the figure object
    pie_chart_file_name = 'printer_status_pie-chart.png'
    full_save_path = os.path.join(output_folder, pie_chart_file_name)
    fig.savefig(full_save_path, bbox_inches='tight', dpi=300)

    # 6. Close the plot
    plt.close(fig)

    print(f"\nPie chart successfully saved as '{pie_chart_file_name}'")
    return full_save_path