# program_gui.py

# Import the 'sys' module, which is necessary for application-level operations like exiting the script.
import sys
# Import the 'asyncio' module to manage the asynchronous tasks.
import asyncio
# Import the necessary widgets and core components from the PyQt6 library.
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt6.QtCore import QObject, QThread, pyqtSignal

# Import the main asynchronous function from your program logic file, renaming it to avoid conflicts.
from main_program import main as run_main_program

# This is the Worker class, designed to run a task in a background thread to keep the GUI responsive.
class movie(QObject):
    # 'finished' is a signal that will be emitted when the background task is complete.
    finished = pyqtSignal()
    # 'error' is a signal that will be emitted if an error occurs, carrying the error message as a string.
    error = pyqtSignal(str)

    # This is the main method that the QThread will execute.
    def run(self):
        # This 'try...except' block is used to catch any errors that happen during the task.
        try:
            # asyncio.run() starts the event loop and runs the main asynchronous function until it's done.
            # This is a blocking call, but it runs in a separate thread, so it doesn't freeze the GUI.
            asyncio.run(run_main_program())
        # If any exception occurs in the 'try' block, it is caught here.
        except Exception as e:
            # The 'error' signal is emitted, sending the error message back to the main GUI thread.
            self.error.emit(str(e))
        # The 'finally' block ensures that the code inside it runs regardless of whether an error occurred or not.
        finally:
            # The 'finished' signal is emitted, indicating that the worker's run() method has completed.
            self.finished.emit()

# This is the main application window class, which inherits from QWidget.
class App(QWidget):
    # The constructor method, which is called when an instance of the App class is created.
    def __init__(self):
        # Calls the constructor of the parent QWidget class to initialize it.
        super().__init__()
        # Sets the title that appears in the window's title bar.
        self.setWindowTitle("My App")
        # Sets the initial dimensions of the window (width, height).
        self.resize(300, 200)
        
        # Creates a push button widget with the label "Run Program".
        self.button = QPushButton("Run Program", self)
        # Sets the position and size of the button within the window.
        self.button.setGeometry(100, 100, 100, 30)
        # Connects the button's 'clicked' signal to the 'on_button_click' method.
        self.button.clicked.connect(self.on_button_click)

    # This method (a "slot") is called whenever the button is clicked.
    def on_button_click(self):
        # Disables the button to prevent the user from clicking it again while a task is running.
        self.button.setEnabled(False)
        
        # Creates a new QThread object, which provides a separate thread for background work.
        self.thread = QThread()
        # Creates an instance of your worker class (named 'movie').
        self.worker = movie()
        # Moves the worker object to the newly created thread. This is a crucial step.
        self.worker.moveToThread(self.thread)
        
        # Connects the thread's 'started' signal to the worker's 'run' method.
        # This means that as soon as the thread starts, it will begin executing the run() method.
        self.thread.started.connect(self.worker.run)
        # Connects the worker's 'finished' signal to the 'thread.quit' method, which stops the thread's event loop.
        self.worker.finished.connect(self.thread.quit)
        # Connects the worker's 'finished' signal to its own 'deleteLater' method for garbage collection.
        self.worker.finished.connect(self.worker.deleteLater)
        # Connects the thread's 'finished' signal to its own 'deleteLater' method for garbage collection.
        self.thread.finished.connect(self.thread.deleteLater)
        # Connects the worker's 'error' signal to a lambda function that will print the error message to the console.
        self.worker.error.connect(lambda e: print(f"Error: {e}"))
        # Connects the worker's 'finished' signal to a lambda function that will re-enable the button.
        self.worker.finished.connect(lambda: self.button.setEnabled(True))
        
        # Starts the thread, which in turn will trigger the worker's run() method. This call is non-blocking.
        self.thread.start()

# This standard Python entry point ensures the code only runs when the script is executed directly.
if __name__ == '__main__':
    # Creates the main application instance, required for any PyQt application.
    app = QApplication(sys.argv)
    # Creates an instance of your main window class.
    ex = App()
    # Makes the main window visible.
    ex.show()
    # Starts the application's main event loop and handles exiting the program.
    sys.exit(app.exec())
