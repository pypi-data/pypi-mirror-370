from functools import wraps
import logging
import math
import os
import time
from typing import (
    Dict,
    List,
    Union,
)

from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QAction, QImage, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
import cv2
from lerobot.common.datasets.image_writer import safe_stop_image_writer
from lerobot.common.datasets.lerobot_dataset import LeRobotDataset
from lerobot.common.policies.factory import make_policy
from lerobot.common.policies.pretrained import PreTrainedPolicy
from lerobot.common.robot_devices.control_configs import (
    RecordControlConfig,
    TeleoperateControlConfig,
)
from lerobot.common.robot_devices.control_utils import (
    reset_environment,
    sanity_check_dataset_name,
    sanity_check_dataset_robot_compatibility,
    stop_recording,
)
from lerobot.common.robot_devices.robots.manipulator import ManipulatorRobot
from lerobot.common.robot_devices.robots.trossen_ai_mobile import TrossenAIMobile
from lerobot.common.robot_devices.robots.utils import Robot, make_robot_from_config
from lerobot.common.robot_devices.utils import busy_wait
from lerobot.common.utils.utils import has_method, log_say
import numpy as np
import trossen_arm
import yaml

from trossen_ai_data_collection_ui.resources.app import Ui_MainWindow
from trossen_ai_data_collection_ui.resources.calibration_menu import Ui_calibration_menu
from trossen_ai_data_collection_ui.utils.constants import (
    PACKAGE_ROOT,
    TROSSEN_AI_CALIBRATION_CONFIG_PATH_PERSISTENT,
    TROSSEN_AI_ROBOT_PATH_PERSISTENT,
    TROSSEN_AI_TASK_PATH_PERSISTENT,
)
from trossen_ai_data_collection_ui.utils.utils import (
    CalibrationConfig,
    create_robot_config,
    get_last_episode_index,
    load_config,
    paintEvent,
    remove_corrupted_files,
    set_image,
)
from trossen_ai_data_collection_ui.workers.recorder import RecordWorker
from trossen_ai_data_collection_ui.workers.yaml import YamlHighlighter


def safe_disconnect(func):
    """
    Decorator to safely disconnect a robot when an exception occurs.

    Ensures that if the decorated function raises an exception, the robot
    is properly disconnected before the exception is propagated.

    :param func: The function to decorate.
    :return: The decorated function.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        robot: None | Robot = None  # Initialize robot as None.

        # Extract the Robot instance from arguments if available.
        for arg in args:
            if hasattr(arg, "disconnect") and hasattr(
                arg, "is_connected"
            ):  # Assuming `Robot` is the correct class name.
                robot = arg
                break

        if robot is None:
            raise ValueError(
                "A Robot instance with a `disconnect` method is required as an argument."
            )

        try:
            return func(self, *args, **kwargs)  # Execute the decorated function.
        except Exception:
            if hasattr(robot, "disconnect") and robot.is_connected:
                print("Error occurred, disconnecting the robot...")
                robot.disconnect()
            raise  # Re-raise the original exception.

    return wrapper


class CalibrationMenu(QDialog):
    """
    Calibration Menu for the Trossen AI Data Collection application.

    This class provides a dialog for calibrating the robot's arms and other components. As of now,
    this menu simply allows users to move their arms to a specified pose, allowing them to run a
    script externally to run external scripts for camera extrinsics calibration.

    Note that this assumes a bimanual setup and will not work on Solo.
    """

    config: CalibrationConfig | None = None
    """Calibration for the configuration routine."""

    safe_pose: list[float] = [0.0, math.pi / 3.0, math.pi / 6.0, math.pi / 5.0, 0.0, 0.0, 0.0]
    """Safe pose for the arms before going to their home pose."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_calibration_menu()
        self.ui.setupUi(self)
        self.setWindowTitle("Calibration Menu")

        self.spinboxes_fl = [
            self.ui.doubleSpinBox_fl_0,
            self.ui.doubleSpinBox_fl_1,
            self.ui.doubleSpinBox_fl_2,
            self.ui.doubleSpinBox_fl_3,
            self.ui.doubleSpinBox_fl_4,
            self.ui.doubleSpinBox_fl_5,
            self.ui.doubleSpinBox_fl_6,
        ]

        self.spinboxes_fr = [
            self.ui.doubleSpinBox_fr_0,
            self.ui.doubleSpinBox_fr_1,
            self.ui.doubleSpinBox_fr_2,
            self.ui.doubleSpinBox_fr_3,
            self.ui.doubleSpinBox_fr_4,
            self.ui.doubleSpinBox_fr_5,
            self.ui.doubleSpinBox_fr_6,
        ]

        self.driver_fl = trossen_arm.TrossenArmDriver()
        self.driver_fr = trossen_arm.TrossenArmDriver()

        self.drivers = [self.driver_fl, self.driver_fr]

        robot = load_config(TROSSEN_AI_ROBOT_PATH_PERSISTENT).get("trossen_ai_stationary")

        try:
            self.driver_fl.configure(
                serv_ip=robot.get("follower_arms").get("left").get("ip"),
                model=trossen_arm.Model.wxai_v0,
                end_effector=trossen_arm.StandardEndEffector.wxai_v0_follower,
                clear_error=False,
            )
            self.driver_fr.configure(
                serv_ip=robot.get("follower_arms").get("right").get("ip"),
                model=trossen_arm.Model.wxai_v0,
                end_effector=trossen_arm.StandardEndEffector.wxai_v0_follower,
                clear_error=False,
            )
        except Exception as e:
            print(f"Error configuring drivers: {e}")
            QMessageBox.critical(self, "Error", f"Failed to configure drivers: {e}")

        # Load existing configurations from the filesystem
        if not self.load_calibration_configs():
            # Notify the users
            warn_msg = (
                "Failed to load calibration configs from "
                f"'{TROSSEN_AI_CALIBRATION_CONFIG_PATH_PERSISTENT}'. Using default values."
            )
            print(warn_msg)
            QMessageBox.warning(
                self,
                "Warning",
                warn_msg,
            )

        # Connect the buttons to their respective functions
        self.ui.pushButton_teleop.clicked.connect(self.calib_teleop)
        self.ui.pushButton_capture.clicked.connect(self.calib_capture)
        self.ui.pushButton_save.clicked.connect(self.save_calibration_configs)
        self.ui.pushButton_gotohome.clicked.connect(self.calib_gotohome)
        self.ui.pushButton_gotopose.clicked.connect(self.calib_gotopose)

    def closeEvent(self, event):
        """
        Override the base class closeEvent with a graceful disconnect routine.

        This puts the arms to home, sets them to idle, and cleans.
        """
        self.calib_gotohome()
        for driver in self.drivers:
            driver.set_all_modes(trossen_arm.Mode.idle)
            driver.cleanup()
            time.sleep(0.1)

        # Call the base class closeEvent method.
        super().closeEvent(event)

    def load_calibration_configs(self) -> bool:
        try:
            print(
                f"Loading calibration config from '{TROSSEN_AI_CALIBRATION_CONFIG_PATH_PERSISTENT}'"
            )
            with open(TROSSEN_AI_CALIBRATION_CONFIG_PATH_PERSISTENT) as file:
                config_dict = yaml.safe_load(file)
            self.config = CalibrationConfig.from_dict(config_dict)
        except FileNotFoundError as e:
            print(
                f"Error: Calibration config file not found at '{TROSSEN_AI_CALIBRATION_CONFIG_PATH_PERSISTENT}': {e}"
            )
            return False
        except yaml.YAMLError as e:
            print(f"Error loading calibration config: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error loading calibration config: {e}")
            return False

        # Populate the spinboxes with the loaded values
        for i, pos in enumerate(self.config.left_arm.capture_positions_rad):
            self.spinboxes_fl[i].setValue(float(np.degrees(pos)))
        for i, pos in enumerate(self.config.right_arm.capture_positions_rad):
            self.spinboxes_fr[i].setValue(float(np.degrees(pos)))
        return True

    def save_calibration_configs(self) -> bool:
        """
        Save the calibration configurations to a YAML file.
        """
        # Update configs
        self.config.left_arm.capture_positions_rad = [
            float(np.radians(spinbox.value())) for spinbox in self.spinboxes_fl
        ]
        self.config.right_arm.capture_positions_rad = [
            float(np.radians(spinbox.value())) for spinbox in self.spinboxes_fr
        ]
        try:
            print(f"Saving calibration config to '{TROSSEN_AI_CALIBRATION_CONFIG_PATH_PERSISTENT}'")
            with open(TROSSEN_AI_CALIBRATION_CONFIG_PATH_PERSISTENT, "w") as file:
                config_dict = self.config.to_dict()
                yaml.safe_dump(config_dict, file)
        except Exception as e:
            print(f"Error saving calibration config: {e}")
            return False

        # Make a dialog popup stating where the config were set to
        QMessageBox.information(
            self,
            "Success",
            f"Changes saved to '{TROSSEN_AI_CALIBRATION_CONFIG_PATH_PERSISTENT}'",
        )

        return True

    def calib_teleop(self) -> None:
        """
        Put the arms in gravity compensation mode.
        """
        for driver in self.drivers:
            driver.set_all_modes(trossen_arm.Mode.position)
            driver.set_all_positions(
                goal_positions=self.safe_pose,
                goal_time=2.0,
                blocking=False,
            )
        time.sleep(2.5)
        for driver in self.drivers:
            driver.set_all_modes(trossen_arm.Mode.external_effort)
            driver.set_all_external_efforts(
                goal_external_efforts=[0.0] * driver.get_num_joints(),
                goal_time=0.0,
                blocking=False,
            )

    def calib_capture(self) -> None:
        """
        Capture the current joint states and populate the spinboxes with them.
        """
        for i, pos in enumerate(self.driver_fl.get_positions()):
            self.spinboxes_fl[i].setValue(np.degrees(pos))

        for i, pos in enumerate(self.driver_fr.get_positions()):
            self.spinboxes_fr[i].setValue(np.degrees(pos))

    def calib_gotohome(self) -> None:
        """
        Move the arms to the home position.
        """
        # Move the arms to their home positions if they are not already there.
        positions = self.driver_fl.get_positions()
        positions.extend(self.driver_fr.get_positions())

        # Skip if arms are already close to their home positions.
        if all(abs(pos) < 0.02 for pos in positions):
            print("Arms are already in home position.")
            return

        for driver in self.drivers:
            driver.set_all_modes(trossen_arm.Mode.position)
            driver.set_all_positions(
                goal_positions=self.safe_pose,
                goal_time=2.0,
                blocking=False,
            )
        time.sleep(2.0)
        for driver in self.drivers:
            driver.set_all_positions(
                goal_positions=[0.0] * driver.get_num_joints(),
                goal_time=2.0,
                blocking=False,
            )
        time.sleep(2.0)
        for driver in self.drivers:
            driver.set_all_modes(trossen_arm.Mode.idle)
            time.sleep(0.1)

    def calib_gotopose(self) -> None:
        """
        Move the arms to the specified pose based on the spinbox values.

        Note that this method leaves the arms in position mode.
        """
        self.driver_fl.set_all_modes(trossen_arm.Mode.position)
        self.driver_fr.set_all_modes(trossen_arm.Mode.position)

        for driver in self.drivers:
            driver.set_all_positions(
                goal_positions=self.safe_pose,
                goal_time=2.0,
                blocking=False,
            )
        time.sleep(2.0)
        self.driver_fl.set_all_positions(
            goal_positions=[np.radians(spinbox.value()) for spinbox in self.spinboxes_fl],
            goal_time=2.0,
            blocking=False,
        )
        self.driver_fr.set_all_positions(
            goal_positions=[np.radians(spinbox.value()) for spinbox in self.spinboxes_fr],
            goal_time=2.0,
            blocking=False,
        )
        time.sleep(2.0)


class MainWindow(QMainWindow):
    """
    Main window class for the Trossen AI Data Collection application.

    This class initializes the user interface, handles user interactions,
    and manages robot recording tasks.
    """

    log_signal = Signal(str, bool)  # Signal for logging messages.

    def __init__(self) -> None:
        """
        Initialize the main window, set up the UI, and configure event handlers.
        """
        super().__init__()  # Call the superclass constructor.
        self.ui = Ui_MainWindow()  # Initialize the UI.
        self.ui.setupUi(self)  # Set up the UI layout and widgets.

        self.log_signal.connect(self.set_logs_slot)  # Connect the log signal to the log method.

        self.thread = None  # Placeholder for the recording thread.

        self.disable_active_ui_updates = False

        # Connect the start recording button to the recording function.
        self.ui.pushButton_start_recording.clicked.connect(self.start_recording)

        # Set initial task selection.
        self.selected_task = self.ui.comboBox_task_selection.currentText()
        self.ui.comboBox_task_selection.currentIndexChanged.connect(
            self.on_dataset_selection
        )  # Handle task selection changes.

        self.ui.pushButton_start_recording.setEnabled(True)  # Enable the start button.
        self.set_logs("Application started! Ready to record...")  # Log startup message.

        self.episode_count = self.ui.spinBox_episode_count.value()  # Get the episode count.

        # Connect buttons to update the episode count.
        self.ui.pushButton_episode_count_plus.clicked.connect(lambda: self.update_episode_count(1))
        self.ui.pushButton_episode_count_minus.clicked.connect(
            lambda: self.update_episode_count(-1)
        )

        self.tasks_config = load_config()  # Load task configurations.

        self.populate_task_combobox()  # Populate the task selection combobox.

        # Checkbox for Displaying cameras.
        self.ui.checkBox_camera_feed.setEnabled(True)

        # Dynamically assign methods to each camera widget.
        self.camera_widgets = [
            self.ui.openGLWidget_camera_0,
            self.ui.openGLWidget_camera_1,
            self.ui.openGLWidget_camera_2,
            self.ui.openGLWidget_camera_3,
        ]

        self.elements_disabled_while_recording: list[QWidget] = [
            self.ui.pushButton_start_recording,
            self.ui.pushButton_dryrun,
            self.ui.spinBox_episode_count,
            self.ui.pushButton_episode_count_plus,
            self.ui.pushButton_episode_count_minus,
            self.ui.comboBox_task_selection,
            self.ui.checkBox_camera_feed,
        ]

        self.placeholder_path = (
            PACKAGE_ROOT / "resources/no_video.jpg"
        )  # Path to the placeholder image.
        self.placeholder_image = None  # Initialize placeholder image.

        self.initialize_image()  # Load and set up the placeholder image.

        # Event flags for recording tasks.
        self.events = {
            "exit_early": False,
            "stop_recording": False,
            "rerecord_episode": False,
        }

        # Connect buttons for re-recording, dry run and stopping recording.
        self.ui.pushButton_rerecord.clicked.connect(self.set_rerecord_episode)
        self.ui.pushButton_stop_recording.clicked.connect(self.set_stop_recording)
        self.ui.pushButton_dryrun.clicked.connect(self.start_dry_run)

        # Enable re-recording, dry run and stop buttons.
        self.ui.pushButton_rerecord.setEnabled(True)
        self.ui.pushButton_stop_recording.setEnabled(True)
        self.ui.pushButton_dryrun.setEnabled(True)

        # Connect menu actions for editing configurations.
        self.ui.actionRobot_Configuration.triggered.connect(self.edit_robot_config)
        self.ui.actionTask_Configuration.triggered.connect(self.edit_task_config)

        # Connect menu actions for calibration
        self.ui.actionCalibrate.triggered.connect(self.open_calibration_menu)

        # Add a quit action to the menu.
        quit_action = QAction("Quit", self)  # Create the quit action.
        quit_action.setShortcut("Ctrl+Q")  # Assign a keyboard shortcut.
        quit_action.triggered.connect(QApplication.quit)  # Connect to quit the application.
        self.ui.menuQuit.addAction(quit_action)  # Add the quit action to the menu.

    def open_calibration_menu(self) -> None:
        self.calibration_popup = CalibrationMenu(self)

        # Open the calibration menu dialog.
        self.calibration_popup.exec()

    def initialize_image(self) -> None:
        """
        Load and set a placeholder image for all camera widgets.

        This method attempts to load a placeholder image from the specified path
        and assigns it to the camera widgets. If the image cannot be loaded,
        warnings or errors are printed to the console.
        """
        # Load and convert the placeholder image.
        if os.path.exists(self.placeholder_path):  # Check if the placeholder path exists.
            self.placeholder_image = cv2.imread(
                str(self.placeholder_path)
            )  # Read the image from the path.
            if self.placeholder_image is not None:
                self.placeholder_image = cv2.cvtColor(
                    self.placeholder_image, cv2.COLOR_BGR2RGB
                )  # Convert image from BGR to RGB.
            else:
                print(
                    f"Error: Unable to load placeholder image {self.placeholder_path}"
                )  # Log an error if loading fails.
                return
        else:
            print(
                f"Warning: Placeholder image not found at {self.placeholder_path}"
            )  # Log a warning if the path is invalid.
            return

        # Assign the placeholder image to all camera widgets.
        if self.placeholder_image is not None:  # Ensure the placeholder image was loaded.
            for widget in self.camera_widgets:  # Iterate over all camera widgets.
                qimage = QImage(
                    self.placeholder_image.data,
                    self.placeholder_image.shape[1],
                    self.placeholder_image.shape[0],
                    QImage.Format.Format_RGB888,
                )  # Convert OpenCV image to QImage.

                # Assign the converted QImage and related methods to the widget.
                widget.set_image = lambda image=qimage, widget=widget: set_image(widget, image)
                widget.paintEvent = lambda event, widget=widget: paintEvent(widget, event)
                widget.image = qimage  # Initialize the widget with the placeholder image.

    def edit_robot_config(self) -> None:
        """
        Open the robot configuration editor.

        This method opens a dialog allowing the user to edit the robot configuration YAML file.
        """
        self.open_edit_dialog("Edit Robot Configuration", TROSSEN_AI_ROBOT_PATH_PERSISTENT)

    def edit_task_config(self) -> None:
        """
        Open the task configuration editor.

        This method opens a dialog allowing the user to edit the task configuration YAML file.
        """
        self.open_edit_dialog("Edit Task Configuration", TROSSEN_AI_TASK_PATH_PERSISTENT)

    def open_edit_dialog(self, title: str, file_path: str) -> None:
        """
        Open a dialog for editing a configuration file.

        This method creates a dialog where the user can view and edit a specified configuration file.
        Changes are validated as YAML before saving.

        :param title: The title of the dialog window.
        :param file_path: The path to the configuration file to be edited.
        """
        self.initialize_image()  # Initialize placeholder images.

        # Create and configure the dialog window.
        dialog = QDialog(self)
        dialog.setWindowTitle(title)  # Set the title of the dialog.
        dialog.setWindowModality(Qt.ApplicationModal)  # Make the dialog modal.
        dialog.resize(800, 600)  # Set the dialog size.

        # Create layout and widgets.
        layout = QVBoxLayout(dialog)
        text_edit = QPlainTextEdit(dialog)  # Text editor for file content.
        save_button = QPushButton("Save", dialog)  # Button to save changes.
        cancel_button = QPushButton("Cancel", dialog)  # Button to cancel changes.

        layout.addWidget(text_edit)  # Add text editor to layout.
        layout.addWidget(save_button)  # Add save button to layout.
        layout.addWidget(cancel_button)  # Add cancel button to layout.

        # Apply YAML syntax highlighting to the text editor.
        _ = YamlHighlighter(text_edit.document())

        # Load the file content into the text editor.
        try:
            with open(file_path) as file:  # Open the file for reading.
                content = file.read()  # Read the file content.
                text_edit.setPlainText(content)  # Display content in the text editor.
        except FileNotFoundError:
            QMessageBox.critical(
                self, "Error", f"File not found: {file_path}"
            )  # Show error message for missing file.
            return
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load file: {e}"
            )  # Show error message for other issues.
            return

        # Define the save action.
        def save_changes():
            try:
                yaml.safe_load(text_edit.toPlainText())  # Validate YAML format.

                # Save validated changes to the file.
                with open(file_path, "w") as file:
                    file.write(text_edit.toPlainText())
                QMessageBox.information(
                    self, "Success", f"Changes saved to {file_path}"
                )  # Show success message.
                self.tasks_config = load_config()  # Reload the task configuration.
                self.populate_task_combobox()  # Refresh the task selection combobox.
                dialog.accept()  # Close the dialog.
            except yaml.YAMLError as e:
                QMessageBox.critical(
                    self, "Error", f"Invalid YAML format: {e}"
                )  # Show error for invalid YAML.
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to save file: {e}"
                )  # Show error for save failure.

        # Define the cancel action.
        def cancel_changes():
            dialog.reject()  # Close the dialog without saving.

        # Connect buttons to their respective actions.
        save_button.clicked.connect(save_changes)
        cancel_button.clicked.connect(cancel_changes)

        dialog.exec()  # Execute the dialog.

    def set_rerecord_episode(self) -> None:
        """
        Trigger re-recording of the current episode.

        Sets the appropriate event flags to indicate that the current episode
        should be re-recorded and the recording process should exit early.
        """
        self.set_logs("Re-record episode triggered")  # Log the action.
        self.events["rerecord_episode"] = True  # Set re-recording flag.
        self.events["exit_early"] = True  # Indicate that the current recording should exit early.

    def set_stop_recording(self) -> None:
        """
        Stop the recording process.

        Sets the appropriate event flags to indicate that the recording process
        should stop and exit early.
        """
        self.set_logs("Stop recording triggered")  # Log the action.
        self.events["stop_recording"] = True  # Set stop recording flag.
        self.events["exit_early"] = True  # Indicate that the current recording should exit early.

    def populate_task_combobox(self) -> None:
        """
        Populate the task selection combobox with tasks from the configuration file.

        Clears the existing items in the combobox and adds task names from the loaded
        YAML configuration. Logs a message if no tasks are found.
        """
        self.ui.comboBox_task_selection.clear()  # Clear existing items in the combobox.

        # Populate the combobox with task names from the configuration.
        if (
            self.tasks_config and "tasks" in self.tasks_config
        ):  # Check if tasks exist in the configuration.
            for task in self.tasks_config["tasks"]:  # Iterate over the tasks.
                task_name = task.get("task_name")  # Get the task name.
                if task_name:
                    self.ui.comboBox_task_selection.addItem(
                        task_name
                    )  # Add task name to the combobox.
        else:
            self.set_logs(
                "No tasks found in the configuration file."
            )  # Log a message if no tasks are found.

    def get_task_parameters(self, task_name: str) -> dict | None:
        """
        Retrieve the configuration of a specific task by its name.

        Searches through the loaded task configuration to find a matching task
        by its name. Logs a message if the task or configuration is not found.

        :param task_name: The name of the task to search for.
        :return: The task configuration as a dictionary if found, otherwise None.
        """
        if not self.tasks_config or "tasks" not in self.tasks_config:  # Check if tasks are loaded.
            self.set_logs(
                "Task configuration not found or tasks not defined."
            )  # Log error if config is missing.
            return None

        for task in self.tasks_config["tasks"]:  # Iterate over tasks in the configuration.
            if task["task_name"] == task_name:  # Check if the task name matches.
                return task  # Return the matching task configuration.

        self.set_logs(
            f"Task '{task_name}' not found in configuration."
        )  # Log message if task is not found.
        return None  # Return None if no match is found.

    @Slot(int)
    def update_progress(self, value: int) -> None:
        """
        Update the progress bar with the given value.

        This method is triggered by a signal to visually indicate progress during recording.

        :param value: The progress value to set (0-100).
        """
        self.ui.progressBar_recording_progress.setValue(value)  # Update the progress bar.

    @Slot(int, object)
    def update_image(self, index: int, image: object) -> None:
        """
        Update the image display for a specified camera widget.

        This method is triggered by a signal to update the displayed image
        for a specific camera widget.

        :param index: The index of the camera widget to update.
        :param image: The image data to display.
        """
        if 0 <= index < len(self.camera_widgets):  # Ensure the index is within range.
            self.camera_widgets[index].set_image(image)  # Update the image in the widget.

    def update_episode_count(self, change: int) -> None:
        """
        Update the episode count by a specified change value.

        Ensures the episode count does not go below zero and updates the corresponding UI element.

        :param change: The value to add to the current episode count.
        """
        self.episode_count += change  # Adjust the episode count.
        if self.episode_count < 0:  # Ensure the count does not go below zero.
            self.episode_count = 0
        self.ui.spinBox_episode_count.setValue(self.episode_count)  # Update the UI element.

    def start_recording(self) -> None:
        """
        Start the recording process for the selected task.

        This method initializes a QThread and a RecordWorker instance to manage
        the recording process. It retrieves the task configuration, sets up the worker,
        connects signals, and starts the recording process.

        :return: None
        """
        # Disable the UI elements that are not required while recording.
        for element in self.elements_disabled_while_recording:
            element.setEnabled(False)

        task_config = self.get_task_parameters(
            self.selected_task
        )  # Retrieve the task configuration.
        if not task_config:  # Handle missing configuration.
            self.set_logs("Unable to find configuration for the selected task.")  # Log an error.
            return
        self.disable_active_ui_updates = task_config.get("disable_active_ui_updates", False)
        # Check if Display Cameras is enabled
        display_cameras = self.ui.checkBox_camera_feed.isChecked()

        config = RecordControlConfig(
            repo_id=f"{task_config.get('hf_user')}/{self.selected_task}",
            single_task=task_config.get("task_description", "No task definition was provided"),
            num_episodes=self.episode_count,
            fps=task_config.get("fps", 30),
            push_to_hub=task_config.get("push_to_hub", False),
            warmup_time_s=task_config.get("warmup_time_s", 3),
            episode_time_s=task_config.get("episode_length_s", 10),
            reset_time_s=task_config.get("reset_time_s", 5),
            display_cameras=display_cameras,
            num_image_writer_threads_per_camera=8,
            play_sounds=task_config.get("play_sounds", False),
        )
        # Initialize the robot with the configuration.
        self.robot = make_robot_from_config(create_robot_config(task_config.get("robot_model")))

        # Get the operators from the task configuration.
        operators = []
        for operator in task_config.get("operators", []):
            operators.append({"name": operator.get("name", None), "email": operator.get("email", None)})

        # Initialize the thread and worker with the task configuration.
        self._thread = QThread()  # Create a new thread.
        self.worker = RecordWorker(  # Set up the recording worker.
            robot=self.robot,
            config=config,
            operators=operators,
            main_window=self,
        )

        # Move the worker to the thread.
        self.worker.moveToThread(self._thread)

        # Connect worker signals to relevant slots.
        self.worker.progress.connect(self.update_progress)  # Connect progress updates.
        self.worker.image_update.connect(self.update_image)  # Connect image updates.
        self.worker.finished.connect(self._thread.quit)  # Quit the thread when worker finishes.
        self.worker.finished.connect(self.worker.deleteLater)  # Clean up the worker.
        self._thread.finished.connect(self._thread.deleteLater)  # Clean up the thread.

        self._thread.started.connect(self.worker.run)  # Start the worker when the thread starts.
        self._thread.start()  # Start the thread.

        # Log the start of recording.
        self.set_logs(f"Starting recording with, {self.selected_task=}.")  # Log recording details.
        log_say("Initializing", True)  # Log preparation message.
        self.set_logs(
            "Please be patient, while the robot is being prepared for recording."
        )  # Log preparation message.

    def start_dry_run(self) -> None:
        """
        Start the recording process for the selected task.

        This method initializes a QThread and a RecordWorker instance to manage
        the recording process. It retrieves the task configuration, sets up the worker,
        connects signals, and starts the recording process.

        :return: None
        """
        # Disable the UI elements that are not required during dry run.
        for element in self.elements_disabled_while_recording:
            element.setEnabled(False)

        task_config = self.get_task_parameters(
            self.selected_task
        )  # Retrieve the task configuration.
        if not task_config:  # Handle missing configuration.
            self.set_logs("Unable to find configuration for the selected task.")  # Log an error.
            return
        self.disable_active_ui_updates = task_config.get("disable_active_ui_updates", False)
        # Check if Display Cameras is enabled
        display_cameras = self.ui.checkBox_camera_feed.isChecked()

        config = TeleoperateControlConfig(
            fps=task_config.get("fps", 30),
            teleop_time_s=task_config.get("episode_length_s", 10),
            display_cameras=display_cameras,
        )
        # Initialize the robot with the configuration.
        self.robot = make_robot_from_config(create_robot_config(task_config.get("robot_model")))

        # Initialize the thread and worker with the task configuration.
        self._thread = QThread()  # Create a new thread.
        self.worker = RecordWorker(  # Set up the recording worker.
            robot=self.robot,
            config=config,
            operators=[],
            main_window=self,
        )

        # Move the worker to the thread.
        self.worker.moveToThread(self._thread)

        # Connect worker signals to relevant slots.
        self.worker.progress.connect(self.update_progress)  # Connect progress updates.
        self.worker.image_update.connect(self.update_image)  # Connect image updates.
        self.worker.finished.connect(self._thread.quit)  # Quit the thread when worker finishes.
        self.worker.finished.connect(self.worker.deleteLater)  # Clean up the worker.
        self._thread.finished.connect(self._thread.deleteLater)  # Clean up the thread.

        self._thread.started.connect(
            self.worker.dry_run
        )  # Start the worker when the thread starts.
        self._thread.start()  # Start the thread.

        # Log the start of recording.
        self.set_logs(f"Starting Dry Run for {self.selected_task=}.")  # Log recording details.
        message = "Initializing."
        log_say(message, True)  # Log preparation message.
        self.set_logs(message)  # Log preparation message.

    def on_dataset_selection(self, _) -> None:
        """
        Handle changes in the selected dataset from the combobox.

        This method updates the currently selected task based on the user's selection
        in the combobox and logs the change.

        :param _: The current index of the combobox (unused).
        :return: None
        """
        self.selected_task = (
            self.ui.comboBox_task_selection.currentText()
        )  # Get the selected task name.
        self.set_logs(f"Selected new task: {self.selected_task}")  # Log the selection.

    def set_logs(self, logs: str, clear: bool = True) -> None:
        """
        Update the log display with a new log message.

        This method appends or replaces the content of the log display widget
        based on the `clear` parameter.

        :param logs: The log message to display.
        :param clear: Whether to clear existing logs before adding the new message.
        :return: None
        """

        text_browser = self.ui.textBrowser_log  # Reference to the QTextBrowser

        if not clear:
            logs = text_browser.toHtml() + "<br>" + logs  # Append new logs using HTML

        text_browser.setHtml(logs)  # Update text display

        # Ensure auto-scroll
        cursor = text_browser.textCursor()  # Get current cursor
        cursor.movePosition(QTextCursor.MoveOperation.End)  # Move cursor to end
        text_browser.setTextCursor(cursor)  # Apply new cursor position
        text_browser.ensureCursorVisible()  # Ensure scrolling to the end

    @Slot(str, bool)
    def set_logs_slot(self, logs: str, clear: bool):
        self.set_logs(logs, clear)

    @safe_stop_image_writer
    def control_loop(
        self,
        robot: Union[ManipulatorRobot, TrossenAIMobile],
        control_time_s: float = None,
        teleoperate: bool = False,
        display_cameras: bool = False,
        dataset: LeRobotDataset | None = None,
        events=None,
        policy: PreTrainedPolicy = None,
        fps: int | None = None,
        single_task: str | None = None,
    ) -> None:
        """
        Execute a control loop for the robot with optional teleoperation and data recording.

        This method performs the control operations for the robot, updates the display with camera images,
        and records data into a dataset if provided. It supports teleoperation and policy-based control.

        :param robot: The robot instance to control.
        :param control_time_s: The total duration for the control loop in seconds. Defaults to infinite.
        :param teleoperate: Whether to enable teleoperation. Defaults to False.
        :param display_cameras: Whether to display camera images. Defaults to True.
        :param dataset: A dataset dictionary to record observations and actions. Defaults to None.
        :param events: A dictionary of events controlling the loop behavior. Defaults to None.
        :param policy: A policy object for automated control. Defaults to None.
        :param device: The device to execute the policy on. Defaults to None.
        :param use_amp: Whether to use automatic mixed precision. Defaults to None.
        :param fps: The desired frames per second for the control loop. Defaults to None.
        :return: None
        """
        if not robot.is_connected:  # Connect the robot if not already connected.
            try:
                robot.connect()
            except RuntimeError as e:
                self.log_signal.emit(f"Error connecting to robot:\n{e}", False)
                return None

        if events is None:  # Initialize events dictionary if not provided.
            events = {"exit_early": False}

        if control_time_s is None:  # Set control time to infinite if not specified.
            control_time_s = float("inf")

        if teleoperate and policy is not None:  # Validate teleoperation and policy usage.
            raise ValueError("When `teleoperate` is True, `policy` should be None.")

        if dataset is not None and fps is not None and dataset.fps != fps:
            raise ValueError(
                f"The dataset fps should be equal to requested fps ({dataset['fps']} != {fps})."
            )

        timestamp = 0
        start_episode_t = time.perf_counter()  # Record the start time of the episode.

        while timestamp < control_time_s:  # Run the loop until the specified control time.
            start_loop_t = time.perf_counter()  # Record the loop start time.

            if teleoperate:  # Perform teleoperation if enabled.
                observation, action = robot.teleop_step(record_data=True)

            if dataset is not None:  # Record data into the dataset if provided.
                frame = {**observation, **action, "task": single_task}
                dataset.add_frame(frame)

            if display_cameras:  # Display images from the robot's cameras.
                image_keys = [
                    key for key in observation if "image" in key
                ]  # Filter image-related keys.

                for i, key in enumerate(image_keys[:4]):  # Limit to the first 4 cameras.
                    image = observation[key].numpy()  # Extract image data.
                    rgb_image = cv2.cvtColor(
                        image, cv2.COLOR_RGB2BGR
                    )  # Convert image to RGB format.
                    self.worker.image_update.emit(i, rgb_image)  # Emit the updated image signal.

            if fps is not None:  # Enforce the desired frames per second.
                dt_s = time.perf_counter() - start_loop_t  # Calculate loop duration.
                busy_wait(1 / fps - dt_s)  # Wait to maintain the desired FPS.

            dt_s = time.perf_counter() - start_loop_t  # Measure the actual loop duration.
            info = self.log_control_info(robot, dt_s, fps=fps)  # Log control loop information.

            timestamp = time.perf_counter() - start_episode_t  # Update elapsed time.

            if not self.disable_active_ui_updates:
                self.log_signal.emit(info, False)  # Emit the log signal.

                progress_value = int(
                    (timestamp / control_time_s) * 100
                )  # Calculate progress percentage.

                self.worker.progress.emit(progress_value)  # Update progress bar.

            if events["exit_early"]:  # Exit the loop early if the event is triggered.
                events["exit_early"] = False
                break

    def log_control_info(
        self,
        robot: Union[ManipulatorRobot, TrossenAIMobile],
        dt_s: float,
        episode_index: int | None = None,
        frame_index: int | None = None,
        fps: int | None = None,
    ) -> None:
        """
        Log timing and performance information for the control loop.

        This method logs information about the control loop's execution time, including
        per-iteration duration and frequencies. It also logs device-specific timing metrics
        for leader arms, follower arms, and cameras.

        :param robot: The robot instance to retrieve log data from.
        :param dt_s: Duration of the control loop iteration in seconds.
        :param episode_index: The current episode index being recorded. Defaults to None.
        :param frame_index: The current frame index being processed. Defaults to None.
        :param fps: The desired frames per second for the control loop. Defaults to None.
        :return: None
        """
        log_items: list[str] = []  # Collect log information as a list of strings.

        if episode_index is not None:  # Log episode index if provided.
            log_items.append(f"ep:{episode_index}")
        if frame_index is not None:  # Log frame index if provided.
            log_items.append(f"frame:{frame_index}")

        def log_dt(shortname: str, dt_val_s: float) -> None:
            """
            Add timing and frequency information to the log.

            :param shortname: A short description of the metric being logged.
            :param dt_val_s: The duration of the metric in seconds.
            """
            nonlocal log_items, fps
            info_str = f"{shortname}:{dt_val_s * 1000:5.2f}ms ({1 / dt_val_s:3.1f}hz)"  # Format duration and frequency.
            if fps is not None:  # Check for FPS consistency.
                actual_fps = 1 / dt_val_s
                if actual_fps < fps - 1:  # Highlight low FPS in yellow.
                    info_str = (
                        f'<span style="color:yellow;">{info_str}</span>'  # Use HTML for coloring.
                    )
            log_items.append(info_str)  # Add to the log.

        log_dt("dt", dt_s)  # Log total loop time.

        # Log device-specific timing metrics for robots other than "stretch".
        if not robot.robot_type.startswith("stretch"):
            # Log leader arm timings.
            for name in robot.leader_arms:
                key = f"read_leader_{name}_pos_dt_s"
                if key in robot.logs:
                    log_dt("dtRlead", robot.logs[key])

            # Log follower arm write and read timings.
            for name in robot.follower_arms:
                write_key = f"write_follower_{name}_goal_pos_dt_s"
                read_key = f"read_follower_{name}_pos_dt_s"
                if write_key in robot.logs:
                    log_dt("dtWfoll", robot.logs[write_key])
                if read_key in robot.logs:
                    log_dt("dtRfoll", robot.logs[read_key])

            # Log camera read timings.
            for name in robot.cameras:
                key = f"read_camera_{name}_dt_s"
                if key in robot.logs:
                    log_dt(f"dtR{name}", robot.logs[key])

        info_str = " ".join(log_items)  # Combine log items into a single string.
        logging.info(info_str)  # Log the information.
        return info_str  # Return the formatted log string.

    @safe_disconnect
    def record(
        self,
        robot: Union[ManipulatorRobot, TrossenAIMobile],
        cfg: RecordControlConfig,
        operators: List[Dict[str, str]],
    ) -> dict:
        """
        Record episodes of robot operation, optionally using a pretrained policy.

        This method initializes a dataset for recording robot observations and actions.
        It optionally applies a policy for automated operation, handles teleoperation,
        and manages episodes with reset and rerecord functionality.

        :param robot: The robot instance to operate and record.
        :param root: The root directory for storing datasets.
        :param repo_id: The Hugging Face repository ID for the dataset.
        :param pretrained_policy_name_or_path: Path to a pretrained policy (optional).
        :param policy_overrides: Overrides for policy configuration (optional).
        :param fps: Desired frames per second for the recording loop (optional).
        :param warmup_time_s: Duration of the warmup phase in seconds. Defaults to 2.
        :param episode_time_s: Duration of each episode in seconds. Defaults to 10.
        :param reset_time_s: Duration for resetting the environment between episodes. Defaults to 5.
        :param num_episodes: Number of episodes to record. Defaults to 50.
        :param video: Whether to record video during the episodes. Defaults to True.
        :param run_compute_stats: Whether to compute dataset statistics after recording. Defaults to True.
        :param push_to_hub: Whether to push the dataset to Hugging Face Hub. Defaults to True.
        :param tags: Tags for the dataset (optional).
        :param num_image_writer_processes: Number of processes for writing images. Defaults to 0.
        :param num_image_writer_threads_per_camera: Threads per camera for writing images. Defaults to 4.
        :param force_override: Whether to override existing datasets. Defaults to False.
        :param display_cameras: Whether to display camera feeds during recording. Defaults to True.
        :param play_sounds: Whether to play sounds during key events. Defaults to True.
        :return: A dictionary containing the recorded dataset information.
        """
        last_recorded_episode_index = get_last_episode_index(cfg.repo_id)
        if last_recorded_episode_index is not None:
            dataset = LeRobotDataset(
                cfg.repo_id,
                root=cfg.root,
            )
            if len(robot.cameras) > 0:
                dataset.start_image_writer(
                    num_processes=cfg.num_image_writer_processes,
                    num_threads=cfg.num_image_writer_threads_per_camera * len(robot.cameras),
                )
            sanity_check_dataset_robot_compatibility(dataset, robot, cfg.fps, cfg.video)
        else:
            # Remove corrupted files
            remove_corrupted_files(cfg.repo_id)
            # Create empty dataset or load existing saved episodes
            sanity_check_dataset_name(cfg.repo_id, cfg.policy)
            dataset = LeRobotDataset.create(
                cfg.repo_id,
                cfg.fps,
                root=cfg.root,
                robot=robot,
                use_videos=cfg.video,
                image_writer_processes=cfg.num_image_writer_processes,
                image_writer_threads=cfg.num_image_writer_threads_per_camera * len(robot.cameras),
            )
        
        for operator in operators:
            name = operator.get("name")
            email = operator.get("email") if "email" in operator else None
            dataset.meta.update_operator(name, email)

        policy = (
            None
            if cfg.policy is None
            else make_policy(cfg.policy, cfg.device, ds_meta=dataset.meta)
        )

        if not robot.is_connected:  # Connect the robot if not already connected.
            try:
                robot.connect()
            except RuntimeError as e:
                self.log_signal.emit(f"Error connecting to robot:\n{e}", False)
                return None

        # Execute a few seconds without recording to:
        # 1. teleoperate the robot to move it in starting position if no policy provided,
        # 2. give times to the robot devices to connect and start synchronizing,
        # 3. place the cameras windows on screen
        log_say("Warmup", cfg.play_sounds)
        self.ui.label_total_time.setText(f"{float(cfg.warmup_time_s)}s")
        self.control_loop(
            robot=robot,
            control_time_s=cfg.warmup_time_s,
            teleoperate=True,
            display_cameras=cfg.display_cameras,
            dataset=None,
            events=self.events,
            policy=None,
            fps=cfg.fps,
        )

        if has_method(robot, "teleop_safety_stop"):
            robot.teleop_safety_stop()

        recorded_episodes = 0
        # Recording loop
        while True:
            if recorded_episodes >= cfg.num_episodes:  # Stop if enough episodes recorded.
                break

            log_say(f"Episode {dataset.num_episodes}", cfg.play_sounds)
            self.log_signal.emit(f"Recording episode {dataset.num_episodes}", True)

            self.ui.label_total_time.setText(f"{float(cfg.episode_time_s)}s")

            self.control_loop(
                robot=robot,
                control_time_s=cfg.episode_time_s,
                teleoperate=True,
                display_cameras=cfg.display_cameras,
                dataset=dataset,
                events=self.events,
                policy=policy,
                fps=cfg.fps,
                single_task=cfg.single_task,
            )

            # Reset phase
            if not self.events["stop_recording"] and (
                (recorded_episodes < cfg.num_episodes - 1) or self.events["rerecord_episode"]
            ):
                log_say("Reset", cfg.play_sounds)
                self.log_signal.emit("Reset the environment", True)
                reset_environment(robot, self.events, cfg.reset_time_s, cfg.fps)

            # Handle rerecord event
            if self.events["rerecord_episode"]:
                log_say("Re-record", cfg.play_sounds)
                self.log_signal.emit("Re-record episode", True)
                self.events["rerecord_episode"] = False
                self.events["exit_early"] = False
                dataset.clear_episode_buffer()
                continue

            dataset.save_episode()  # Save the current episode.
            recorded_episodes += 1

            if self.events["stop_recording"]:  # Exit loop if stop event is triggered.
                break

        log_say("Stop", cfg.play_sounds, blocking=True)
        self.log_signal.emit("Stop recording", True)
        stop_recording(robot, None, cfg.display_cameras)

        self.initialize_image()  # Reinitialize the camera images.

        # Enable the UI elements after recording.
        for element in self.elements_disabled_while_recording:
            element.setEnabled(True)

        if cfg.push_to_hub:  # Push the dataset to the Hugging Face Hub if requested.
            dataset.push_to_hub(tags=cfg.tags, private=cfg.private)

        log_say("Done", cfg.play_sounds)
        self.log_signal.emit("Done", True)
        return dataset

    @safe_disconnect
    def dry_run(
        self,
        robot: Union[ManipulatorRobot, TrossenAIMobile],
        cfg: TeleoperateControlConfig,
    ) -> None:
        """
        Execute a dry run of the robot's operation.

        This method performs a dry run of the robot's operation, allowing for
        teleoperation and testing without recording data. It handles camera display
        and teleoperation events.

        :param robot: The robot instance to operate.
        :param cfg: The configuration object for the dry run.
        :return: None
        """
        if not robot.is_connected:  # Connect the robot if not already connected.
            try:
                robot.connect()
            except RuntimeError as e:
                self.log_signal.emit(f"Error connecting to robot:\n{e}", False)
                return None
        self.ui.label_total_time.setText(f"{float(cfg.teleop_time_s)}s")
        self.control_loop(
            robot=robot,
            control_time_s=cfg.teleop_time_s,
            teleoperate=True,
            display_cameras=cfg.display_cameras,
            dataset=None,
            events=self.events,
            policy=None,
            fps=cfg.fps,
        )
        if has_method(robot, "teleop_safety_stop"):
            robot.teleop_safety_stop()
        robot.disconnect()

        self.initialize_image()  # Reinitialize the camera images.

        # Enable the UI elements after recording.
        for element in self.elements_disabled_while_recording:
            element.setEnabled(True)

        log_say("Exiting", True)
        self.log_signal.emit("Exiting", True)
