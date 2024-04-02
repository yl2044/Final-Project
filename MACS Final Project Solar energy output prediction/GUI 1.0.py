# Importing necessary modules from PyQt5 for creating the GUI.
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene, QGraphicsView

# Importing module for integrating matplotlib plots into PyQt5 applications.
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

# Subprocess module is used to spawn new processes, connect to their input/output/error pipes, and obtain their return codes.
import subprocess

# System-specific parameters and functions module. Used here likely for accessing command-line arguments.
import sys

# Python Imaging Library (PIL) adds image processing capabilities - here imported as 'Image' for basic image operations.
from PIL import Image

class Ui_Form(object):
    def setupUi(self, Form):
        # Setting the object name and initial size of the main window.
        Form.setObjectName("Photovoltaic Power Generation Forecasting System")
        Form.resize(781, 500)
        Form.setWindowTitle("Photovoltaic Power Generation Forecasting System")

        # Path for the background image of the GUI.
        background_image_path = "GUIbackground.jpg"  # Replace with the image path
        self.set_background_image(Form, background_image_path)  # Setting the background image.

        # Push button for executing the main action, positioned at specified coordinates.
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(550, 410, 175, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.run_external_script)  # Connecting button click to script execution.

        # Button to open a file dialog, allowing the user to select a file.
        self.fileDialogButton = QtWidgets.QPushButton(Form)
        self.fileDialogButton.setGeometry(QtCore.QRect(350, 410, 175, 23))
        self.fileDialogButton.setObjectName("fileDialogButton")
        self.fileDialogButton.setText("file selection")
        self.fileDialogButton.clicked.connect(self.open_file_dialog)  # Connecting button click to file dialog.

        # Line edit for user input, e.g., number of hours for prediction.
        self.lineEditA = QtWidgets.QLineEdit(Form)
        self.lineEditA.setGeometry(QtCore.QRect(150, 410, 171, 31))
        self.lineEditA.setObjectName("lineEditA")
        self.lineEditA.setPlaceholderText("hours")  # Placeholder text for guidance.

        # Text browser for displaying selected file path or other messages.
        self.textBrowser = QtWidgets.QTextBrowser(Form)
        self.textBrowser.setGeometry(QtCore.QRect(40, 340, 500, 30))
        self.textBrowser.setObjectName("textBrowser")

        # Scroll area to contain the graphics view.
        self.scrollArea = QtWidgets.QScrollArea(Form)
        self.scrollArea.setGeometry(QtCore.QRect(20, 50, 730, 280))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")

        # QGraphicsView to display the plot
        self.graphicsView = QGraphicsView(self.scrollArea)
        self.graphicsView.setGeometry(QtCore.QRect(0, 0, 730, 280))
        self.graphicsView.setObjectName("graphicsView")

        # QGraphicsScene to manage items in the view
        self.graphicsScene = QGraphicsScene()
        self.graphicsView.setScene(self.graphicsScene)  # Setting the scene to the view.
        self.scrollArea.setWidget(self.graphicsView)  # Adding the graphics view to the scroll area.
        self.retranslateUi(Form)  # Setting up translations and text.
        QtCore.QMetaObject.connectSlotsByName(Form)  # Automatically connecting signals based on object names.

    def retranslateUi(self, Form):
        # This method sets up the text for widgets using translations for internationalization.
        # '_translate' is a method for translating text based on the application's current locale.
        _translate = QtCore.QCoreApplication.translate

        # Setting the window title.
        Form.setWindowTitle(_translate("Form", "Photovoltaic Power Generation Forecasting System"))

        # Setting the text of the buttons.
        self.pushButton.setText(_translate("Form", "confirm"))
        self.fileDialogButton.setText(_translate("Form", "file selection"))

    def run_external_script(self):
        try:
            # Retrieves the user input for 'a_value' from the line edit field.
            a_value = self.lineEditA.text()

            # Retrieves the file path input from the text browser widget.
            csv_file_path = self.textBrowser.toPlainText()

            # Runs an external script ('333.py') with 'a_value' and 'csv_file_path' as arguments.
            # 'stdout=subprocess.PIPE' captures the output of the script.
            result = subprocess.run(["python", "LSTM.py", a_value, csv_file_path], stdout=subprocess.PIPE, text=True)

            # Extracts the output text from the script's execution result.
            output_text = result.stdout
            # Splits the output text by '11', assuming this is a delimiter used in the script's output.
            parts = output_text.split('11')
            # The first part before '11' is assumed to be the path to the generated plot image.
            path = parts[0].strip() + ".png"
            # The second part after '11' (if any) is displayed in the text browser.
            self.textBrowser.setText(parts[1].strip())

            # Display the plot in the QGraphicsView
            self.display_plot_in_graphicsview(path)

        except Exception as e:
            # If an error occurs during script execution, it's caught and printed to the console.
            print(f"Error executing script: {e}")

    def open_file_dialog(self):
        # Opens a dialog window for the user to select a CSV file.
        # The dialog filters to only show files with the '.csv' extension.
        csv_file_path, _ = QFileDialog.getOpenFileName(None, "Select CSV file", "", "CSV Files (*.csv)")

        # Checks if a file path was selected (i.e., the operation was not canceled).
        if csv_file_path:
            # Sets the selected file path as the text of the text browser widget, displaying it to the user.
            self.textBrowser.setText(csv_file_path)

    def display_plot_in_graphicsview(self, image_path):
        try:
            # Read the image and convert it to a QImage
            original_image = Image.open(image_path)
            original_image = original_image.convert("RGBA")

            # Resize the image to 1/4 of its original size
            resized_image = original_image.resize((original_image.width // 2, original_image.height // 2))

            q_image = QtGui.QImage(resized_image.tobytes(), resized_image.size[0], resized_image.size[1],
                                   QtGui.QImage.Format_RGBA8888)

            # Create a QGraphicsPixmapItem from the QImage
            pixmap_item = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap.fromImage(q_image))

            # Clear the existing items in the scene and add the new one
            self.graphicsScene.clear()
            self.graphicsScene.addItem(pixmap_item)

            # Adjust the size of the QGraphicsView to fit the resized image
            self.graphicsView.setSceneRect(0, 0, resized_image.width, resized_image.height)
            self.graphicsView.setScene(self.graphicsScene)

        except Exception as e:
            print(f"Error displaying plot: {e}")

    def set_background_image(self, widget, image_path):
        # Set background image for the main window
        palette = QtGui.QPalette()
        background_image = QtGui.QPixmap(image_path).scaled(widget.size(), QtCore.Qt.IgnoreAspectRatio,
                                                            QtCore.Qt.SmoothTransformation)
        palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(background_image))
        widget.setPalette(palette)


# Checks if this script is the main program and is not being imported by another module.
if __name__ == "__main__":
    # Creates an instance of QApplication. 'sys.argv' contains the command-line arguments.
    # It's necessary for initializing the GUI application.
    app = QtWidgets.QApplication(sys.argv)

    # Creates the main window widget. QWidget is a base class for all UI objects in PyQt5.
    Form = QtWidgets.QWidget()

    # Creates an instance of the Ui_Form class, which contains the setup for the UI.
    ui = Ui_Form()

    # Calls the setupUi method on the instance 'ui' to setup the UI components on 'Form'.
    ui.setupUi(Form)

    # Displays the main window to the user.
    Form.show()

    # Starts the application's event loop. The script will stay in this method call until
    # the application is closed. 'sys.exit' ensures a clean exit, passing the exit status
    # from 'app.exec_' back to the shell.
    sys.exit(app.exec_())

