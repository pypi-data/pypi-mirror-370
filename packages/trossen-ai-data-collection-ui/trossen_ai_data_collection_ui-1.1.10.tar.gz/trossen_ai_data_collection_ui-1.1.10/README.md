
# **Trossen AI Data Collection UI**

![Project Image](./trossen_ai_data_collection_ui/resources/trossen_ai_gui.png)

---

## **Overview**

Trossen AI Data Collection UI is a Python-based application designed for seamless and efficient robotic data collection.
It provides an intuitive GUI to manage robot configurations, perform task recordings, and streamline data collection with advanced features like camera views, task management, and progress tracking.

---

## **Pre-Installation Setup**

Before installing the application, complete the following setup:

1. **Install Miniconda:**
   Download and install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) for your operating system.

2. **Create a Virtual Environment:**
   Use Miniconda to create a virtual environment:
   ```bash
   conda create -n trossen_ai_data_collection_ui_env python=3.10 -y
   conda activate trossen_ai_data_collection_ui_env
   ```

---

## **Installation**

Install Trossen AI Data Collection UI directly using `pip`:

```bash
pip install trossen_ai_data_collection_ui
```

---

## **Post-Installation**

After installation, run the command to setup the following:
- Clones and installs required dependencies for `Interbotix/lerobot`.
- Resolves common issues with OpenCV and video encoding.
- Creates a desktop icon for launching the application.

```bash
trossen_ai_data_collection_ui_post_install
```

---

## **Launching the Application**

### **Desktop Application**

After installation, a desktop shortcut named **Trossen AI DAta Collection UI** is available.
Click on it to launch the application.

### **Command Line**

Alternatively, you can run the application directly from the terminal:

```bash
trossen_ai_data_collection_ui
```

---

## **Application Features**

### **1. Task Management**
- **Task Names:** Select predefined tasks from the dropdown menu.
- **Episodes:** Specify the number of episodes using the spin box. Adjust the count using the `+` and `-` buttons.

### **2. Recording Controls**
- **Start Recording:** Initiates data collection for the selected task.
- **Stop Recording:** Stops the current data collection session.
- **Re-Record:** Allows re-recording of the current episode if necessary.

### **3. Progress Tracking**
- A progress bar tracks the recording session in real-time, displaying completion percentage.

### **4. Camera Views**
- View multiple camera feeds in real-time during recording for better monitoring.

### **5. Configuration Management**
- **Edit Robot Configuration:** Modify the robot's YAML configuration for granular control.
- **Edit Task Configuration:** Adjust task-specific parameters via a YAML editor.

### **6. Quit Button**
- Use the Quit button in the menu to gracefully exit the application.

---

## **Hardware Setup**

For detailed instructions on the hardware setup, please refer to the official documentation:
[**Trossen AI Hardware Setup Guide**](https://docs.trossenrobotics.com/trossen_arm/main/getting_started/hardware_setup.html)

This guide provides comprehensive information, including:

- **Connecting the Arms**: Step-by-step guidance to assemble and connect the robotic arms.
- **Serial Number Configuration**: Instructions on setting up and verifying serial numbers for the arms.
- **Camera Setup**: Using the Intel RealSense Viewer for calibrating and positioning cameras effectively.
