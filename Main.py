
import os
import re
import sys
import logging
import traceback

import requests
from PyQt6.QtNetwork import QNetworkProxy

from PyQt6.QtCore import pyqtSignal, QObject, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QSplashScreen
from PyQt6.QtWidgets import QMessageBox

from GANTRITHOR.MIXINS.PathsAndDirectoriesMixin import PathsAndDirectoriesMixin
from GANTRITHOR.FACTORY_GUI.FactoryGuiSkeleton import FactoryGuiSkeleton

from GANTRITHOR.IMG_ADAPTER.IMGId2LabelObserver import IMGId2LabelObserver
from GANTRITHOR.IMG_GUI.IMGgui import IMGgui
from GANTRITHOR.NER_ADAPTER.id2labelObserver import Id2LabelObserver
from GANTRITHOR.NER_GUI.NERgui import NERgui
from GANTRITHOR.OBJ_ADAPTER.OBJId2LabelObserver import OBJId2LabelObserver
from GANTRITHOR.OBJ_GUI.OBJ_GUI import OBJgui
from GANTRITHOR.SETTINGS.SettingsGui import SettingsGui
from GANTRITHOR.TEXT_ADAPTER.TEXTid2labelObserver import TEXTId2LabelObserver
from GANTRITHOR.TEXT_GUI.TEXTgui import TEXTgui
from GANTRITHOR.MIXINS.LicenseManager import LicenseManager


class Main(QObject, PathsAndDirectoriesMixin):
    """
    The Main class serves as the central hub for the application,
    orchestrating various components and managing the overall workflow.
    It inherits from PathsAndDirectoriesMixin for path management functionalities.

    Attributes:
    - reset_pipeline_signal (pyqtSignal): A signal for resetting the pipeline.
    - license_manager (LicenseManager): Manages license-related functionalities, such as verification and activation.
    - factory (FactoryGuiSkeleton): An instance of the GUI factory, responsible for creating GUI components.
    - main_window (QWidget): The main window of the application.
    - central_layout, ner_task_frame, text_task_frame: Layout and frames for different task areas.
    - ner_button, text_button: Buttons to switch between NER and TEXT GUIs.
    - ner_gui, text_gui: Instances of NERgui and TEXTgui, representing the GUIs for NER and TEXT functionalities.
    - settings_gui (SettingsGui): A GUI for application settings.
    - settings_button, activate_button: Buttons for accessing settings and activating the product.
    - directory_labels (dict): Stores directory path labels for display.

    Methods:
    - __init__(): Initializes the class attributes, sets up GUI components, connects signals and slots.
    - is_commercial_version(): Checks if the application is a commercial version based on the license status.
    - create_main_window(): Creates and configures the main window of the application.
    - add_directory_path_gui(): Adds a GUI component to display directory paths.
    - on_model_loaded(), on_dataset_loaded(): Callbacks for model and dataset loading events.
    - format_directory_path(): Formats directory paths for display.
    - open_settings(): Displays the settings GUI.
    - switch_gui(): Switches between NER and TEXT GUIs based on user interaction.
    - open_activation_dialog(): Opens a dialog for license activation.
    - activate_license(): Activates the license based on the user-provided key.
    - show_message_dialog(), show_popup_message(): Utility methods to show message dialogs.
    - add_to_observer(), add_to_observer_text(): Adds GUI components to respective observers for updates.
    - reset_pipeline(): Resets the application pipeline, clearing and reinitializing GUI components.
    - clearBottomLayout(), clearLayout(): Utility methods to clear layouts.
    - clear_central_layout(): Clears the central layout of the main window.
    - delete_database(): Deletes the SQL database file.
    - run(): Shows the main window and starts the application.

    The Main class is designed to provide a seamless user experience,
    integrating different modules of the application and ensuring smooth transitions and interactions.

    Keys that work:
    test_key
    2b5515fc587a4a6081bc96277c3a4ba2
    6e494cc8d714431d9f43459a13ea6f73
    e94db46d91ec4545809dce61a51483e1
    0020505d38f94ef8875c98917475c318
    1fd955b7c4ca4477a5ed7184a8b1d0f3

    """

    reset_pipeline_signal = pyqtSignal()  # Define the signal
    reset_pipeline_signal_text = pyqtSignal()
    reset_pipeline_signal_img = pyqtSignal()
    reset_pipeline_signal_obj = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.version = "Free"
        self.initialize_paths_and_directories()
        # self.error_signal.error_occurred.connect(self.show_error_popup)
        self.setup_logging()  # Set up logging configuration
        self.delete_database()
        self.factory = FactoryGuiSkeleton()  # Create an instance of your GUI factory

        self.main_window = self.create_main_window()  # Create the main window using the factory
        self.license_manager = LicenseManager(self.main_window)

        # Add the 'ner' task frame to the central layout of the main window
        self.central_layout = self.factory.central_layout

        # Create task frames for 'ner' and 'text'
        self.ner_task_frame, self.ner_task_frame_layout = self.factory.create_task_frame("ner")
        self.text_task_frame, self.text_task_frame_layout = self.factory.create_task_frame("text")
        self.img_task_frame, self.img_task_frame_layout = self.factory.create_task_frame("img")
        # self.object_task_frame, self.object_task_frame_layout = self.factory.create_task_frame("object")

        # Create NER and TEXT buttons.
        self.ner_button, _ = self.factory.create_control_button("NER", width=100, height=24, font_size=12, toggle_option=True)
        self.text_button, _ = self.factory.create_control_button("TEXT", width=100, height=24, font_size=12, toggle_option=True)
        self.img_button, _ = self.factory.create_control_button("IMAGE", width=100, height=24, font_size=12, toggle_option=True)
        # self.obj_button, _ = self.factory.create_control_button("OBJECT", width=100, height=24, font_size=12, toggle_option=True)

        # Connect to slot
        self.ner_gui = NERgui(self.factory)
        self.ner_gui.reset_pipeline_requested_ner.connect(self.reset_pipeline_signal.emit)
        self.reset_pipeline_signal.connect(self.reset_pipeline_ner)
        self.ner_button.setChecked(True)  # Mark the button as checked

        self.text_gui = TEXTgui(self.factory)  # Assuming similar structure for TEXTgui
        self.text_gui.reset_pipeline_requested_text.connect(self.reset_pipeline_signal_text.emit)
        self.reset_pipeline_signal_text.connect(self.reset_pipeline_text)
        # self.text_gui.setup_logging()

        self.img_gui = IMGgui(self.factory)
        self.img_gui.reset_pipeline_requested_img.connect(self.reset_pipeline_signal_img.emit)
        self.reset_pipeline_signal_img.connect(self.reset_pipeline_img)

        self.obj_gui = OBJgui(self.factory)
        self.obj_gui.reset_pipeline_requested.connect(self.reset_pipeline_signal_obj.emit)
        self.reset_pipeline_signal_obj.connect(self.reset_pipeline_obj)

        self.add_to_observer()  # Add NERgui to the observer
        self.add_to_observer_text()
        self.add_to_observer_img()
        self.add_to_observer_obj()


        self.central_layout.addWidget(self.ner_gui)
        # self.central_layout.addWidget()

        # Connect buttons to switch GUI
        self.ner_button.clicked.connect(lambda: self.switch_gui("ner"))
        self.text_button.clicked.connect(lambda: self.switch_gui("text"))
        self.img_button.clicked.connect(lambda: self.switch_gui("img"))
        # self.obj_button.clicked.connect(lambda: self.switch_gui("obj"))

        # Add NER and TEXT buttons to the top_frame layout
        self.factory.top_layout.addWidget(self.ner_button)
        self.factory.top_layout.addWidget(self.text_button)
        self.factory.top_layout.addWidget(self.img_button)
        # self.factory.top_layout.addWidget(self.obj_button)

        self.factory.top_layout.addStretch(1)  # Add stretch after the buttons

        self.settings_gui = SettingsGui(self.factory)
        self.settings_gui.hide()

        # Create the third button with an icon
        self.settings_icon_path = os.path.join(self.icons_path, "icon_settings")
        self.settings_button, _ = self.factory.create_control_button("",
                                                                     width=24,
                                                                     height=24,
                                                                     hover=True,
                                                                     tooltip_text="Settings",
                                                                     icon_path=self.settings_icon_path)

        # Add version label to the top frame
        self.version_label = QLabel(f"Version: {self.version}  ")
        self.version_label.setStyleSheet("font-weight: bold; color: red;")
        self.factory.top_layout.addWidget(self.version_label)
        # self.factory.top_layout.addStretch(1)  # Add stretch to align the version label to the left

        self.activate_button, _ = self.factory.create_control_button("Activate", width=100, height=24, font_size=12)
        self.activate_button.clicked.connect(self.license_manager.open_activation_dialog)
        self.factory.top_layout.addWidget(self.activate_button, 1)

        self.settings_button.clicked.connect(self.open_settings)
        self.settings_button.setStyleSheet("border: None")

        self.is_commercial_version()

        self.directory_labels = {}

        self.ner_gui.load_model_gui.load_model_signal.connect(self.on_model_loaded)
        self.ner_gui.load_dataset_gui.load_dataset_signal.connect(self.on_dataset_loaded)
        self.text_gui.load_model_gui.load_model_signal.connect(self.on_model_loaded)
        self.text_gui.load_dataset_gui.load_dataset_signal.connect(self.on_dataset_loaded)
        self.img_gui.load_model_gui.load_model_signal.connect(self.on_model_loaded)
        self.img_gui.load_dataset_gui.load_dataset_signal.connect(self.on_dataset_loaded)
        self.obj_gui.load_model_gui.load_model_signal.connect(self.on_model_loaded)
        self.obj_gui.load_dataset_gui.load_dataset_signal.connect(self.on_dataset_loaded)

        # self.divide_zero_error = 5 / 0
        # Add the third button to the top_frame layout
        self.factory.top_layout.addWidget(self.settings_button)

    def is_commercial_version(self):
        license_status = self.license_manager.load_and_decrypt()
        self.license_status = license_status
        self.version = "Commercial" if license_status == "commercial" else "Free"
        self.version_label.setText(f"Version: {self.version}")  # Update the version label text
        if license_status == "commercial":
            self.version_label.setStyleSheet("font-weight: bold; color: green;")
        self.ner_gui.ner_singleton.license_status = self.license_status
        self.text_gui.text_singleton.license_status = self.license_status
        self.img_gui.img_singleton.license_status = self.license_status
        self.obj_gui.obj_singleton.license_status = self.license_status

    def create_main_window(self):
        # Use the factory's method to create the main window
        light_blue = "#ADD8E6"
        return self.factory.create_main_window(background_color=light_blue)

    def set_proxy(self, proxy_host, proxy_port):
        proxy = QNetworkProxy()
        proxy.setType(QNetworkProxy.ProxyType.HttpProxy)
        proxy.setHostName(proxy_host)
        proxy.setPort(proxy_port)
        QNetworkProxy.setApplicationProxy(proxy)

    def add_directory_path_gui(self, directory_path, label_type):
        formatted_path = self.format_directory_path(directory_path, label_type)
        object_name = f"label_{label_type}"

        if object_name in self.directory_labels:
            # Update existing label
            self.directory_labels[object_name].setText(formatted_path)
        else:
            # Create new label and add to layout
            dir_path_label = self.factory.create_directory_path_gui(formatted_path)
            dir_path_label.setObjectName(object_name)
            self.directory_labels[object_name] = dir_path_label
            self.factory.bottom_layout.addWidget(dir_path_label)

    def on_model_loaded(self, model_path):
        self.add_directory_path_gui(f"Model: {model_path}", 'model')

    def on_dataset_loaded(self, dataset_path):
        self.add_directory_path_gui(f"Dataset: {dataset_path}", 'dataset')

    def format_directory_path(self, directory_path, label_type):
        label_prefix = f"{label_type}: "
        path = directory_path.replace(label_prefix, "")

        # Split the directory path using regular expression
        dir_parts = re.split(r'[\\/]', path)
        formatted_dir = " > ".join(dir_parts)

        was_truncated = False
        # Shorten the path if it exceeds 140 characters, keeping the label prefix
        while len(formatted_dir) > 140 - len(label_prefix):
            was_truncated = True
            dir_parts = dir_parts[1:]  # Remove the first part
            formatted_dir = " > ".join(dir_parts)  # Rejoin the remaining parts

        # Add ellipses if the path was truncated
        if was_truncated:
            formatted_dir = "..." + formatted_dir
        else:
            formatted_dir = formatted_dir

        return formatted_dir

    def open_settings(self):
        # Method to show the SettingsGui
        self.settings_gui.show()

    def switch_gui(self, gui_name):
        self.reset_button_styles()

        current_widget = self.central_layout.takeAt(0).widget()
        if current_widget is not None:
            current_widget.setParent(None)

        # Add the new GUI based on the button clicked
        if gui_name == "ner":
            self.central_layout.addWidget(self.ner_gui)
            self.ner_button.setChecked(True)  # Mark the button as checked
        elif gui_name == "text":
            self.central_layout.addWidget(self.text_gui)
            self.text_button.setChecked(True)  # Mark the button as checked
        elif gui_name == "img":
            self.central_layout.addWidget(self.img_gui)
            self.img_button.setChecked(True)  # Mark the button as checked
        elif gui_name == "obj":
            self.central_layout.addWidget(self.obj_gui)
            # self.obj_button.setChecked(True)  # Mark the button as checked

    def reset_button_styles(self):
        """
        Resets the style of all control buttons by setting their checked state to False.
        """
        self.ner_button.setChecked(False)
        self.text_button.setChecked(False)
        self.img_button.setChecked(False)
        # self.obj_button.setChecked(False)

    def show_message_dialog(self, title, message):
        """
        Shows a message dialog with the given title and message.
        """
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.exec()

    def show_popup_message(self, title, message):
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle(title)
        layout = QVBoxLayout()
        label = QLabel(message)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.close)
        layout.addWidget(label)
        layout.addWidget(ok_button)
        dialog.setLayout(layout)
        dialog.exec()

    def add_to_observer(self):
        """
        This method adds the modules that are involved in creating label buttons from
        the model and dataset parameters. The observer pattern here is for making sure the data and model
        initialization in our pipeline all has access to all attributes related to the id2label in model config.

        :return:
        """

        id2label_observer = Id2LabelObserver()

        self.ner_gui.id2label_converter_instance.reset()
        id2label_observer.add_observer(self.ner_gui.ner_dataframe)
        id2label_observer.add_observer(self.ner_gui.load_dataset_gui)
        id2label_observer.add_observer(self.ner_gui.create_dataset_gui)
        id2label_observer.add_observer(self.ner_gui.load_model_gui)
        id2label_observer.add_observer(self.ner_gui.create_model_gui)
        id2label_observer.add_observer(self.ner_gui)

    def add_to_observer_text(self):
        """
        Same as the add_to_observer method, but used to for text classification.

        :return:
        """

        text_id2label_observer = TEXTId2LabelObserver()

        self.text_gui.text_id2label_converter_instance.reset()
        text_id2label_observer.add_observer(self.text_gui.text_dataframe)
        text_id2label_observer.add_observer(self.text_gui.load_dataset_gui)
        text_id2label_observer.add_observer(self.text_gui.create_dataset_gui)
        text_id2label_observer.add_observer(self.text_gui.load_model_gui)
        text_id2label_observer.add_observer(self.text_gui.create_model_gui)
        text_id2label_observer.add_observer(self.text_gui)

    def add_to_observer_img(self):
        """
        Adds the modules involved in creating label buttons for image classification to the observer.
        Ensures that data and model initialization have access to attributes related to the id2label in model config.
        """
        img_id2label_observer = IMGId2LabelObserver()

        # Reset the id2label converter instance for image GUI
        self.img_gui.img_id2label_converter_instance.reset()

        # Add necessary GUI components to the observer
        img_id2label_observer.add_observer(self.img_gui.img_dataframe)
        img_id2label_observer.add_observer(self.img_gui.load_dataset_gui)
        img_id2label_observer.add_observer(self.img_gui.create_dataset_gui)
        img_id2label_observer.add_observer(self.img_gui.load_model_gui)
        img_id2label_observer.add_observer(self.img_gui.create_model_gui)
        img_id2label_observer.add_observer(self.img_gui)

    def add_to_observer_obj(self):
        """
        Adds the modules involved in creating label buttons for object classification to the observer.
        Ensures that data and model initialization have access to attributes related to the id2label in model config.


        """
        obj_id2label_observer = OBJId2LabelObserver()

        # Reset the id2label converter instance for object GUI
        self.obj_gui.obj_id2label_converter_instance.reset()

        # Add necessary GUI components to the observer
        obj_id2label_observer.add_observer(self.obj_gui.obj_dataframe)
        obj_id2label_observer.add_observer(self.obj_gui.load_dataset_gui)
        obj_id2label_observer.add_observer(self.obj_gui.create_dataset_gui)
        obj_id2label_observer.add_observer(self.obj_gui.load_model_gui)
        obj_id2label_observer.add_observer(self.obj_gui.create_model_gui)
        obj_id2label_observer.add_observer(self.obj_gui)

    def reset_pipeline_ner(self):
        # Clear NER related components
        if hasattr(self, 'ner_gui'):
            self.ner_gui.deleteLater()  # Safely delete the current instance

        # Reinitialize NER GUI component
        self.ner_gui = NERgui(self.factory)
        self.ner_gui.reset_pipeline_requested_ner.connect(self.reset_pipeline_signal.emit)
        self.reset_pipeline_signal.connect(self.reset_pipeline_ner)
        self.ner_gui.load_model_gui.load_model_signal.connect(self.on_model_loaded)
        self.ner_gui.load_dataset_gui.load_dataset_signal.connect(self.on_dataset_loaded)

        # Update the central layout
        self.switch_gui("ner")
        self.directory_labels = {}
        self.clearBottomLayout()
        self.add_to_observer()
        self.is_commercial_version()

    def reset_pipeline_text(self):
        # Clear TEXT related components
        if hasattr(self, 'text_gui'):
            self.text_gui.deleteLater()  # Safely delete the current instance

        # Reinitialize TEXT GUI component
        self.text_gui = TEXTgui(self.factory)
        self.text_gui.reset_pipeline_requested_text.connect(self.reset_pipeline_signal_text.emit)
        self.reset_pipeline_signal_text.connect(self.reset_pipeline_text)
        self.text_gui.load_model_gui.load_model_signal.connect(self.on_model_loaded)
        self.text_gui.load_dataset_gui.load_dataset_signal.connect(self.on_dataset_loaded)

        # Update the central layout
        self.switch_gui("text")
        self.directory_labels = {}
        self.clearBottomLayout()
        self.add_to_observer_text()
        self.is_commercial_version()

    def reset_pipeline_img(self):
        # Clear IMG related components
        if hasattr(self, 'img_gui'):
            self.img_gui.deleteLater()  # Safely delete the current instance

        # Reinitialize IMG GUI component
        self.img_gui = IMGgui(self.factory)
        self.img_gui.reset_pipeline_requested_img.connect(self.reset_pipeline_signal_img.emit)
        self.reset_pipeline_signal_img.connect(self.reset_pipeline_img)
        self.img_gui.load_model_gui.load_model_signal.connect(self.on_model_loaded)
        self.img_gui.load_dataset_gui.load_dataset_signal.connect(self.on_dataset_loaded)

        # Update the central layout
        self.switch_gui("img")
        self.directory_labels = {}
        self.clearBottomLayout()
        self.add_to_observer_img()
        self.is_commercial_version()

    def reset_pipeline_obj(self):
        # Clear OBJ related components
        if hasattr(self, 'obj_gui'):
            self.obj_gui.deleteLater()  # Safely delete the current instance

        # Reinitialize OBJ GUI component
        self.obj_gui = OBJgui(self.factory)
        self.obj_gui.reset_pipeline_requested.connect(self.reset_pipeline_signal_obj.emit)
        self.reset_pipeline_signal_obj.connect(self.reset_pipeline_obj)
        self.obj_gui.load_model_gui.load_model_signal.connect(self.on_model_loaded)
        self.obj_gui.load_dataset_gui.load_dataset_signal.connect(self.on_dataset_loaded)

        # Update the central layout
        self.switch_gui("obj")
        self.directory_labels = {}
        self.add_to_observer_obj()
        self.is_commercial_version()


    def clearBottomLayout(self):
        """Clear all widgets from the bottom layout."""
        self.clearLayout(self.factory.bottom_layout)

    def clearLayout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clearLayout(item.layout())
                item.layout().deleteLater()

    def clear_central_layout(self):
        self.clearLayout(self.central_layout)

    def run(self):
        # Set the global exception handler
        sys.excepthook = self.global_exception_handler
        try:
            # Show the main window
            self.main_window.show()
        except Exception as e:
            logging.error("An error occurred: %s", str(e), exc_info=True)
            # self.show_error_popup(str(e))

    def show_error_popup(self, error_message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Error")
        msg_box.setText("An error occurred. Would you like to send an error report?")
        msg_box.setInformativeText(f"Error details: {error_message}")
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        response = msg_box.exec()
        if response == QMessageBox.StandardButton.Yes:
            self.send_error_report(error_message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    paths = PathsAndDirectoriesMixin()
    paths.initialize_paths_and_directories()
    image_path = os.path.join(paths.icons_path, "icon_gantrithor_2.png")
    splash_image = QPixmap(image_path)
    # splash_image = QPixmap(r"C:\Users\doren\PycharmProjects\GANTRITHOR_FINAL_2024\GANTRITHOR\gantrithors\icons\icon_gantrithor_2.png")

    # Get the current size of the image
    current_width = splash_image.width()
    current_height = splash_image.height()

    # Resize the image to be twice as big
    new_size = splash_image.scaled(current_width * 2, current_height * 2, Qt.AspectRatioMode.KeepAspectRatio)

    splash = QSplashScreen(splash_image, Qt.WindowType.WindowStaysOnTopHint)

    # Optionally, you can add a message to the splash screen
    splash.showMessage("Loading...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, Qt.GlobalColor.white)

    splash.show()

    app.processEvents()  # Process any pending events to ensure the splash screen is displayed promptly

    main_app = Main()  # Create an instance of your main application class
    splash.hide()
    main_app.run()
    sys.exit(app.exec())

