# Import the 'sys' module, which provides access to system-specific parameters and functions,
# essential for managing the application's lifecycle (e.g., sys.exit).
import sys

# Import the 'os' module, which provides a way of using operating system dependent
# functionality like reading or writing to the file system.
import os

# Import the 'asyncio' library, which is the foundation for running and managing
# the asynchronous network tasks concurrently without freezing the application.
import asyncio


# Used to parse the EXCEL tracker and get the list of EXCEl sheet names, which will be needed when
# validating user input.
import pandas as pd

# From the 'main_program.py' file, import the primary 'main' asynchronous function.
# It is renamed to 'run_main_program' here to create a clear, descriptive name for use within the GUI.
from main_program import main as run_main_program

# From the PyQt5.QtWidgets module, import the fundamental classes needed to build the user interface.
# --> QApplication: Manages the application's main event loop and overall resources.
# --> QWidget: The base class for all user interface objects (e.g., a window).
# --> QLabel: A widget used to display text or images.
# --> QLineEdit: A widget that provides a single-line text input box.
# --> QPushButton: A standard command button widget.
# --> QVBoxLayout: A layout manager that arranges widgets vertically.
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout)

# From the PyQt5.QtGui module, import classes for handling graphical elements.
# --> QPixmap: A class designed for displaying images, optimized for screen rendering.
# --> QMovie: A class used for displaying animations, particularly animated GIFs.
from PyQt5.QtGui import QPixmap, QMovie

# From the PyQt5.QtCore module, import core, non-GUI functionalities.
# --> Qt: Provides a collection of flags and enums (e.g., for alignment).
# --> QObject: The base class for all Qt objects, providing the signal and slot mechanism.
# --> QThread: Provides a separate thread of execution for running long-running tasks.
# --> pyqtSignal: Allows for the creation of custom signals to communicate between threads.
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal

########################################################################################################################################

# This class will define the GUI graphically and add functionality to it.
class PrinterCheckerApp(QWidget):


    # BASIC COMPONENTS AND INITIALIZATION
    # -----------------------------------
    def __init__(self):


        ### <=== CONSTRUCTOR ===> ###
        # Run the CONSTRUCTOR of the parent class (QWidget): (It registers the widget with the PyQt/PySide framework, it allocates memory 
        # for painting, handling mouse clicks, and managing its position, it sets up its internal state, preparing it to be shown on the 
        # screen and it does hundreds of other complex setup tasks that you don't have to worry about.)
        super().__init__()


        ### <=== ESSENTIAL WIDGETS ===> ###
        # Create the widgets
        self.tracker_label = QLabel("Enter the EXCEL sheet name: ", self) # Prompts the user to enter the name of the EXCEL sheet
        self.tracker_name_input = QLineEdit(self) # Creates a text box for the user to input the prompted data
        self.generate_report_and_update_tracker_button = QPushButton("I'm feeling complacient", self) # Creates the button for the user to start the check
        self.progress_indication_text_label = QLabel("Checking your stupid printers...", self) # Indicates that the porgram is running
        self.progress_counter_label = QLabel("0%", self) # Indicates the percentage of progress of the check
        

        ### <=== DISPLAY INTRO GIF ===> ###
        self.show_intro_gif()


        ### <=== INITIALIZE THE LAYOUT ===> ###
        self.initUI() # Manage the layout of the widgets within the window


    # LAYOUT, STYLE AND ADDITION OF FUNCTIONALITY
    # -------------------------------------------
    def initUI(self):


        ### <=== WINDOW TITLE ===> ###
        # Define the Windows Title
        self.setWindowTitle("CrayonEaters Ultimate Printer Checker")


        ### <=== MANAGE THE LAYOUT ===> ###
        # Add all the widgets to the vertical layout manager
        vertical_layout_manager = QVBoxLayout()
        vertical_layout_manager.addWidget(self.tracker_label)
        vertical_layout_manager.addWidget(self.tracker_name_input)
        vertical_layout_manager.addWidget(self.generate_report_and_update_tracker_button)
        vertical_layout_manager.addWidget(self.progress_indication_text_label)
        vertical_layout_manager.addWidget(self.progress_counter_label)
        vertical_layout_manager.addWidget(self.progress_gif_label)

        # Assign the QVBoxLayout layout manager to the window widget
        self.setLayout(vertical_layout_manager)

        # Centralize the widgets horizontally. The button and the text box are not needed to be centralized, since they occupy all the 
        # width already.
        self.tracker_label.setAlignment(Qt.AlignCenter)
        self.progress_indication_text_label.setAlignment(Qt.AlignCenter)
        self.progress_counter_label.setAlignment(Qt.AlignCenter)
        self.progress_gif_label.setAlignment(Qt.AlignCenter)


        ### <=== APPLY CSS STYLING ===> ###
        # Define the Object names for each widget:
        self.tracker_label.setObjectName("tracker_label")
        self.tracker_name_input.setObjectName("tracker_name_input")
        self.generate_report_and_update_tracker_button.setObjectName("generate_report_and_update_tracker_button")
        self.progress_indication_text_label.setObjectName("progress_indication_text_label")
        self.progress_counter_label.setObjectName("progress_counter_label")
        self.progress_gif_label.setObjectName("progress_gif_label")

        # Define the CSS Style Sheet by referencing widgets with their assigned object names.
        self.setStyleSheet("""

            /* This settings apply to all objects */
            QLabel, QPushButton{
                font-family: calibri;
            }
                           
            /* Only for the tracker_label object */
            QLabel#tracker_label{
                font-size: 40px;
                font-style: italic;
                background-color: rgba(34, 49, 34, 180); /* dark forest green */
                color: #DDE5D1; /* light desaturated green */
                padding: 10px;
                border-radius: 10px;
                border: 2px solid #556B2F; /* olive border */
            }
                           
            /* Only for the tracker_name_input object */
            QLabel#tracker_name_input{
                font-size: 40px;
            } 

            /* Only for the generate_report_and_update_tracker_button object */
            QLabel#generate_report_and_update_tracker_button{
                font-size: 30px;
                font-weight: bold;
            }
                           
            /* Only for the progress_indication_text_label object */
            QLabel#progress_indication_text_label{
                font-size: 50px;
            }
      
            /* Only for the progress_counter_label object */
            QLabel#progress_counter_label{
                font-size: 50px;
            }
                           
            /* Only for the progress_gif_label object */
            QLabel#progress_gif_label object{
            }
        """)


        ### <=== ADD FUNCTIONALITY ===> ###
        self.generate_report_and_update_tracker_button.clicked.connect(self.run_check)


    # DEFINE FUNCTIONALITY
    # --------------------
    def run_check(self):
        """

        PURPOSE
        This function acts as a project manager who needs to delegate a big, time-consuming job (pinging all the printers) to a 
        specialist worker. The manager's goal is to give the specialist the instructions, let them work independently, and get updates 
        without having to stop their own work (i.e., without freezing the GUI).

        ARGUMENTS
        excel_file = the absolute path of the EXCEL tracker of the printers. We will use it when validating the
        user's input of the EXCEL sheet name, in the function that compares such input with the current names of
        all the worksheets.
        """


        ### <=== GET AND VALIDATE USER INPUT ===> ###
        # It reads the current text from the QLineEdit where the user types the sheet name. It then checks if the box is empty. This is a 
        # "fail-fast" validation step. It ensures that the program has the necessary information before it goes through the effort of 
        # creating threads and workers. If the input is invalid, it shows an error and stops immediately, re-enabling the button for the
        # user to be able to try again.

        # Extract the EXCEL sheet name from the text box:
        excel_sheet_name = self.tracker_name_input.text()

        # Call the function to validate the user's input.
        if self.check_sheet_name(excel_sheet_name) == True:
            pass
        # If false...
        else:
            return

        # Stop any current GIF (like the error GIF)
        if self.movie and self.movie.state() == QMovie.Running:
            self.movie.stop()

        # Load and start the "running" GIF.
        self.movie = QMovie("images/ultimate-printer-checker_slap.gif") # Or whatever your running GIF is called
        self.progress_gif_label.setMovie(self.movie)
        self.movie.start()


        ### <=== PREPARE THE USER INTERFACE FOR THE TASK ===> ###
        # The very first thing is to disable the "Run" button and update a status label.
        # This provides immediate feedback to the user that their click was successful. Disabling the button is crucial to prevent the 
        # user from clicking it again and starting multiple, conflicting background jobs at the same time.
        self.generate_report_and_update_tracker_button.setEnabled(False)
        self.progress_indication_text_label.setText("Preparing to run...")

       
        ### <=== CREATE THE BACKGROUND WORKER AND ITS "OFFICE" ===> ###
        # This creates a new, empty thread of execution. Think of this as building a new, empty office room. It doesn't do anything on its
        # own yet.
        self.thread = QThread()

        # This creates an instance of your Worker class (the specialist). It passes the excel_sheet_name to the worker's constructor, so 
        # the worker knows exactly what EXCEL sheet to work on.
        self.worker = Worker(excel_sheet_name=excel_sheet_name)

        # This is the most critical step in Qt threading. It tells the worker object, "You no longer live in the main GUI thread. Move 
        # into that new, empty office (self.thread) I just created for you." 
        # From now on, all of the worker's code will run in that separate background thread.
        self.worker.moveToThread(self.thread)

        
        ### <=== SET UP THE COMMUNICATION CHANNELS (SIGNALS AND SLOTS) ===> ###
        # This section is like the project manager giving the specialist a set of instructions on how to report back. All the connect 
        # calls are setting up these communication lines before the work starts.

        # Connects the thread's started signal to the worker's run method. This means, "The moment the background thread officially starts,
        # automatically call the worker.run() method." This is the trigger that begins your actual task.
        self.thread.started.connect(self.worker.run)

        # These lines connect the worker's custom signals back to methods (slots) in your main GUI window:
        # "Whenever the worker sends a text progress update, just put that text directly into my status label."
        self.worker.progress.connect(self.progress_indication_text_label.setText)

        # "Whenever the worker sends a percentage number, call my update_progress_label method with that number."
        self.worker.progress_percent.connect(self.update_progress_label)

        # This next block is crucial for cleanup. It ensures that once the worker is done (either by finishing or by erroring), the 
        # thread's event loop is properly stopped (quit) and both the worker and thread objectsare scheduled to be safely deleted 
        # (deleteLater), preventing memory leaks.
         
        # When the worker emits an error, clean up and report it. The self.report_error method will be automatically called.
        self.worker.error.connect(self.report_error) # this function is defined later in this class
        self.worker.error.connect(self.thread.quit)
        self.worker.error.connect(self.worker.deleteLater)
        self.worker.error.connect(self.thread.deleteLater)

        # When the worker finishes successfully, clean up and report success. The self.report_finished method will be automatically called.
        self.worker.finished.connect(self.report_finished) # this function is defined later in this class
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        

        ### <=== START THE WORK ===> ###
        # This is the final command. It tells the background thread to start its event loop. This call is non-blocking—it returns 
        # immediately. The thread.start() call immediately emits the thread.started signal. Because we connected that signal, it instantly
        # calls the worker.run() method in the background, and your entire asynchronous pinging process begins without ever freezing the 
        # main GUI.
        self.thread.start()


    # END OF PROGRAM FUNCTIONS
    # ------------------------
    def report_finished(self):
        """
        The report_finished function is a "slot" in the Qt signal/slot mechanism. Its sole purpose is to execute a set of final UI 
        cleanup and notification tasks only after the long-running background process has completed successfully. It acts as the 
        designated "success handler" for your application's main task.

        The function is called by the run_check method when the worker job is completed successfully.
        """

        # Update the status label
        self.progress_indication_text_label.setText("Process complete! Files have been generated.")

        # Re-enable the button for the user to be able to run another check
        self.generate_report_and_update_tracker_button.setEnabled(True)

    def report_error(self, error_message):
        """
        The report_error function is a "slot" in the Qt signal/slot mechanism. Its sole purpose is to execute a set of final UI 
        cleanup and notification tasks only after the long-running background process has encountered an error. It acts as the 
        designated "error handler" for your application's main task.

        The function is called by the run_check method when the worker job encounters an error.
        """

        # Update the status label
        self.progress_indication_text_label.setText(f"Error: {error_message}")


    # GET A FILE'S ABSOLUTE PATH
    # --------------------------
    def get_base_path(self):
        """Gets the base path for the application, whether running as a script or frozen."""
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle (e.g., by PyInstaller)
            return os.path.dirname(sys.executable)
        else:
            # If running as a normal .py script
            return os.path.dirname(os.path.abspath(__file__))


    # CHECK EXCEL SHEET NAME
    # ----------------------
    def check_sheet_name(self, excel_sheet_name):
        """
        PURPOSE
        Checks if a user's input matches any of the worksheet names in an Excel file. 

        ARGUMENTS
        excel_file = The path to the Excel file.

        RETURN VALUE
        If the user input is empty or invalid, we will return a False boolean. If it matches one of
        the worksheet names, we will returna True boolean.
        """
        
        ### <=== GET THE EXCEL ABSOLUTE PATH ===> ###
        # Get the EXCEL file path
        BASE_PATH = self.get_base_path()
        excel_file = os.path.join(BASE_PATH, 'Printer_Fleet_Table.xlsx')
        print(excel_file)

        ### <=== CHECK IF USER INPUT IS EMPTY ===> ###
        if not excel_sheet_name:
            self.progress_indication_text_label.setStyleSheet("""
                    QLabel#progress_indication_text_label{
                    font-size: 40px;
                    }
                """)
            self.show_empty_error_gif(excel_sheet_name)
            return False
        
        ### <=== CHECK IF USER INPUT IS A VALID EXCEL SHEET ===> ###
        else:
            try:
                # Get the list of sheet names from the Excel file
                xls = pd.ExcelFile(excel_file)
                sheet_names_list = xls.sheet_names

                # Check if the user's input matches any of the sheet names
                if excel_sheet_name in sheet_names_list:
                    print(f"Success! The worksheet '{excel_sheet_name}' was found in the Excel file.")
                    return True   
                else:
                    print(f"Error: The worksheet '{excel_sheet_name}' was not found.")
                    #print("Available worksheets are:", sheet_names)
                    # Show the specific GIF for this:
                    self.progress_indication_text_label.setStyleSheet("""
                        QLabel#progress_indication_text_label{
                        font-size: 40px;
                        }
                    """)
                    self.show_wrong_name_gif(excel_sheet_name)
                    return False

            except FileNotFoundError:
                print(f"Error: The file '{excel_file}' was not found.")
            except Exception as e:
                print(f"An error occurred: {e}")


    # DEFINE THE PROGRESS COUNTER
    # ---------------------------
    def update_progress_label(self, percentage):
        """
        Updates the progress counter label with the percentage. The percentage argument is retrieved directly from the value that was 
        emitted by the progress_percent signal in the Worker object.
        
        """
        
        # Display the received value of the percentage variable
        self.progress_counter_label.setText(f"{percentage}%")
    

    # EMPTY INPUT ERROR
    # ------------------------
    def show_empty_error_gif(self, excel_sheet_name):
        """
        Show a different GIF if the user does not enter any text input in the text box.
        """
        if not excel_sheet_name:

            # Display an error message:
            self.progress_indication_text_label.setText("ERROR: Dumbass, you forgot to \nenter the godamn sheet name.")

            # Stop any GIF that might already be running
            if self.movie and self.movie.state() == QMovie.Running:
                self.movie.stop()

                # Load your new GIF for the empty input error.
                # Replace the current GIF with the actual path.
                self.movie = QMovie('images/ultimate-printer-checker_error_empty.gif')
                self.progress_gif_label.setMovie(self.movie)
                self.movie.start()

            # Re-enable the button, since the button's trigger process is not running yet
            self.generate_report_and_update_tracker_button.setEnabled(True) 
            return

    def show_wrong_name_gif(self, excel_sheet_name):
        """
        Show a different GIF if the user enters an inexistent worksheet name.
        """

        # Display an error message:
        self.progress_indication_text_label.setText("ERROR: Retard, the name you entered \ndoes not exist.")

        # Stop any GIF that might already be running
        if self.movie and self.movie.state() == QMovie.Running:
            self.movie.stop()

            # Load your new GIF for the empty input error.
            # Replace the current GIF with the actual path.
            self.movie = QMovie('images/ultimate-printer-checker_wrong_worksheet.gif')
            self.progress_gif_label.setMovie(self.movie)
            self.movie.start()

        # Re-enable the button, since the button's trigger process is not running yet
        self.generate_report_and_update_tracker_button.setEnabled(True) 
        return


    # INTRO DISPLAY
    # -------------
    def show_intro_gif(self):
        # Create an empty QLabel for the GIF
        self.progress_gif_label = QLabel(self) 
        # Create a QMovie object with your GIF
        self.movie = QMovie("images/ultimate-printer-checker_slap.gif")
        # Set the QMovie on the QLabel
        self.progress_gif_label.setMovie(self.movie)
        # Start the animation
        self.movie.start()


# This class will manage the asynchronous task part of the GUI functionality.
class Worker(QObject):
    """
    A worker object that runs a long-running task in a separate thread. Its primary purpose is to run a time-consuming operation in 
    a separate thread, preventing the main application window from freezing and becoming unresponsive.
    Emits signals to communicate with the main GUI thread.
    """
    
    # DEFINE THE SIGNALS
    # ------------------
    # This defines a signal named finished. It carries no data. Its purpose is simply to announce, "The task is complete and was successful."
    finished = pyqtSignal() 

    # This defines an error signal. It is configured to carry a string (str). When an error occurs, the worker can emit this signal and 
    # pass the error message along with it. The GUI can then display this message to the user.
    error = pyqtSignal(str)

    # A signal to send general status updates as text. For example, it could emit messages like "Connecting to database..." or "Processing 
    # row 500...".
    progress = pyqtSignal(str)

    # A signal designed to send an integer (int). This is perfect for updating a progress bar in the GUI. The worker can emit 
    # progress_percent.emit(25) to set the progress bar to 25%.
    progress_percent = pyqtSignal(int)


    # CONSTRUCTOR
    # -----------
    def __init__(self, excel_sheet_name: str):
        super().__init__()
        # Store the sheet name safely when the worker is created.
        self.excel_sheet_name = excel_sheet_name


    # EXECUTE THE ASYNC PROGRAM
    # -------------------------
    def run(self):
        """Executes the asynchronous main program."""
        try:
            self.progress.emit("Running, please wait...")

            ### <=== PERCENTAGE COUNTER ===> ###
            # Create a simple, unnamed function called progress_callback. This function's only job is to take one input value and 
            # immediately 'emit' it using the progress_percent signal.
            progress_callback = lambda percentage: self.progress_percent.emit(percentage)

            ### <=== RUN MAIN PROGRAM ===> ###
            asyncio.run(run_main_program(
                self.excel_sheet_name,
                # The main_program must be updated to accept and pass this down
                progress_callback=progress_callback 
            ))

            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


# Ensure that this GUI only runs on the main program file, and not as an imported module on any other file
if __name__ == "__main__":
    app = QApplication(sys.argv)
    printerchecker_app = PrinterCheckerApp()
    printerchecker_app.show()
    sys.exit(app.exec_())
