from dataclasses import dataclass
import json
import os
import shutil
from typing import Tuple, Type, Union

from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QWidget
from lerobot.common.robot_devices.cameras.configs import (
    CameraConfig,
    IntelRealSenseCameraConfig,
    OpenCVCameraConfig,
)
from lerobot.common.robot_devices.motors.configs import TrossenArmDriverConfig
from lerobot.common.robot_devices.robots.configs import (
    TrossenAIMobileRobotConfig,
    TrossenAISoloRobotConfig,
    TrossenAIStationaryRobotConfig,
)
import yaml

from trossen_ai_data_collection_ui.utils.constants import (
    TROSSEN_AI_ROBOT_PATH_PERSISTENT,
    TROSSEN_AI_TASK_PATH_PERSISTENT,
)


@dataclass
class CalibrationConfig:
    """
    Configuration class for calibration menu parameters.
    """

    @dataclass
    class CalibrationFollowerArmConfig:
        """
        Configuration class for arm parameters.
        """

        arm_name: str = ""
        """Name of the arm."""

        capture_positions_rad: list[float] = None
        """List of capture positions in radians."""

    left_arm: CalibrationFollowerArmConfig = None
    """Left arm configuration."""

    right_arm: CalibrationFollowerArmConfig = None
    """Right arm configuration."""

    @staticmethod
    def from_dict(data: dict) -> "CalibrationConfig":
        """
        Create a CalibrationConfig instance from a dictionary.

        :param data: Dictionary containing configuration data.
        :return: CalibrationConfig instance.
        """
        config = CalibrationConfig()
        follower_arms_config = data["follower_arms"]

        # Get left arm config
        left_arm_config = follower_arms_config.get("left")
        if left_arm_config is None:
            raise ValueError("Left arm configuration not found.")
        config.left_arm = CalibrationConfig.CalibrationFollowerArmConfig()
        config.left_arm.arm_name = "left"
        config.left_arm.capture_positions_rad = [
            float(pos) for pos in left_arm_config.get("capture_positions_rad", [])
        ]
        if len(config.left_arm.capture_positions_rad) != 7:
            raise ValueError("Capture positions for left arm must be a list of 7 floats.")

        # Get right arm config
        right_arm_config = follower_arms_config.get("right")
        if right_arm_config is None:
            raise ValueError("Right arm configuration not found.")
        config.right_arm = CalibrationConfig.CalibrationFollowerArmConfig()
        config.right_arm.arm_name = "right"
        config.right_arm.capture_positions_rad = [
            float(pos) for pos in right_arm_config.get("capture_positions_rad", [])
        ]
        if len(config.right_arm.capture_positions_rad) != 7:
            raise ValueError("Capture positions for right arm must be a list of 7 floats.")

        return config

    def to_dict(self) -> dict:
        """
        Convert the CalibrationConfig instance to a dictionary.

        :return: Dictionary representation of the configuration.
        """
        return {
            "follower_arms": {
                "left": {
                    "capture_positions_rad": self.left_arm.capture_positions_rad,
                },
                "right": {
                    "capture_positions_rad": self.right_arm.capture_positions_rad,
                },
            }
        }


def set_image(widget: QWidget, image: object) -> None:
    """
    Convert a BGR OpenCV image to RGB format and update the widget with the image.

    :param widget: The widget where the image will be displayed.
    :param image: The image data in OpenCV format (BGR).
    """
    widget.image = QImage(
        image.data, image.shape[1], image.shape[0], QImage.Format.Format_RGB888
    ).rgbSwapped()  # Convert BGR to RGB and swap channels.
    widget.update()  # Trigger a paint event to refresh the widget.


def paintEvent(widget: QWidget, _: object) -> None:
    """
    Handle the widget's paint event to draw an image if available.

    :param widget: The widget to be painted.
    :param event: The paint event object.
    """
    if hasattr(widget, "image") and widget.image is not None:  # Check if the widget has an image.
        painter = QPainter(widget)  # Create a painter for the widget.
        painter.drawImage(widget.rect(), widget.image)  # Draw the image in the widget's rectangle.


def load_config(file_path: str = TROSSEN_AI_TASK_PATH_PERSISTENT) -> dict | None:
    """
    Load a YAML configuration file for tasks and return the parsed data as a dictionary.

    :param file_path: Path to the YAML configuration file. Defaults to TROSSEN_AI_TASK_PATH.
    :return: Parsed configuration data as a dictionary, or None if an error occurs.
    """
    try:
        with open(file_path) as file:  # Open the file for reading.
            config_data = yaml.safe_load(file)  # Parse the YAML content.
        return config_data  # Return the parsed data.
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")  # Log file not found error.
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")  # Log YAML parsing error.
        return None


def get_last_episode_index(file_path):
    file_path = os.path.join(
        os.path.expanduser("~"),
        ".cache",
        "huggingface",
        "lerobot",
        file_path,
        "meta",
        "episodes.jsonl",
    )
    if not os.path.exists(file_path):
        return None  # Return None if file is missing

    last_entry = None

    # Read the file line by line (JSONL format)
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            last_entry = json.loads(line)  # Keep updating last_entry with the latest line

    if last_entry:
        return last_entry.get("episode_index", None)
    else:
        return None


def remove_corrupted_files(file_path):
    file_path = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "lerobot", file_path)
    if os.path.exists(file_path):
        shutil.rmtree(file_path)


def get_camera_interface(camera_type: str) -> Tuple[CameraConfig, str]:
    if camera_type == "opencv":
        return OpenCVCameraConfig, "camera_index"
    elif camera_type == "intel_realsense":
        return IntelRealSenseCameraConfig, "serial_number"
    else:
        raise ValueError(f"Invalid camera interface: {camera_type}")


def make_camera_config(
    serial_number: str,
    fps: int,
    width: int,
    height: int,
    camera_interface_class: Type[Union[IntelRealSenseCameraConfig, OpenCVCameraConfig]],
    key_name: str,
) -> Union[IntelRealSenseCameraConfig, OpenCVCameraConfig]:
    return camera_interface_class(
        **{key_name: serial_number},
        fps=fps,
        width=width,
        height=height,
    )


def create_robot_config(
    robot_name: str,
) -> Union[TrossenAIStationaryRobotConfig, TrossenAISoloRobotConfig, TrossenAIMobileRobotConfig]:
    robot = load_config(TROSSEN_AI_ROBOT_PATH_PERSISTENT).get(robot_name)

    camera_interface_class, key_name = get_camera_interface(robot.get("camera_interface"))

    cameras = {
        name: make_camera_config(index["serial_number"], index["fps"], index["width"], index["height"], camera_interface_class, key_name)
        for name, index in robot.get("cameras").items()
    }
    min_time_to_move_multiplier = robot.get("min_time_to_move_multiplier", 3.0)

    if robot_name == "trossen_ai_stationary":
        robot_config = TrossenAIStationaryRobotConfig(
            max_relative_target=None,
            mock=False,
        )
        robot_config.leader_arms = {
            "left": TrossenArmDriverConfig(
                ip=robot.get("leader_arms").get("left").get("ip"),
                model=robot.get("leader_arms").get("left").get("model"),
                min_time_to_move_multiplier=min_time_to_move_multiplier,
            ),
            "right": TrossenArmDriverConfig(
                ip=robot.get("leader_arms").get("right").get("ip"),
                model=robot.get("leader_arms").get("right").get("model"),
                min_time_to_move_multiplier=min_time_to_move_multiplier,
            ),
        }
        robot_config.follower_arms = {
            "left": TrossenArmDriverConfig(
                ip=robot.get("follower_arms").get("left").get("ip"),
                model=robot.get("follower_arms").get("left").get("model"),
                min_time_to_move_multiplier=min_time_to_move_multiplier,
            ),
            "right": TrossenArmDriverConfig(
                ip=robot.get("follower_arms").get("right").get("ip"),
                model=robot.get("follower_arms").get("right").get("model"),
                min_time_to_move_multiplier=min_time_to_move_multiplier,
            ),
        }
        robot_config.cameras = cameras
    elif robot_name == "trossen_ai_solo":
        robot_config = TrossenAISoloRobotConfig(
            max_relative_target=None,
            mock=False,
        )
        robot_config.leader_arms = {
            "main": TrossenArmDriverConfig(
                ip=robot.get("leader_arms").get("main").get("ip"),
                model=robot.get("leader_arms").get("main").get("model"),
                min_time_to_move_multiplier=min_time_to_move_multiplier,
            ),
        }
        robot_config.follower_arms = {
            "main": TrossenArmDriverConfig(
                ip=robot.get("follower_arms").get("main").get("ip"),
                model=robot.get("follower_arms").get("main").get("model"),
                min_time_to_move_multiplier=min_time_to_move_multiplier,
            ),
        }
        robot_config.cameras = cameras

    elif robot_name == "trossen_ai_mobile":
        robot_config = TrossenAIMobileRobotConfig(
            max_relative_target=None,
            mock=False,
        )
        robot_config.leader_arms = {
            "left": TrossenArmDriverConfig(
                ip=robot.get("leader_arms").get("left").get("ip"),
                model=robot.get("leader_arms").get("left").get("model"),
                min_time_to_move_multiplier=min_time_to_move_multiplier,
            ),
            "right": TrossenArmDriverConfig(
                ip=robot.get("leader_arms").get("right").get("ip"),
                model=robot.get("leader_arms").get("right").get("model"),
                min_time_to_move_multiplier=min_time_to_move_multiplier,
            ),
        }
        robot_config.follower_arms = {
            "left": TrossenArmDriverConfig(
                ip=robot.get("follower_arms").get("left").get("ip"),
                model=robot.get("follower_arms").get("left").get("model"),
            ),
            "right": TrossenArmDriverConfig(
                ip=robot.get("follower_arms").get("right").get("ip"),
                model=robot.get("follower_arms").get("right").get("model"),
            ),
        }
        robot_config.cameras = cameras
    else:
        raise ValueError(f"Invalid robot name: {robot_name}")

    return robot_config
