# LiDAR Motion Detection and Visualization

A Python application for real-time motion detection and visualization using the innomaker DTOF LiDAR Time-of-Flight Lidar STL-19P.

## LiDAR Sensor

This project is designed to work with the **innomaker DTOF LiDAR Time-of-Flight Lidar STL-19P** with the following specifications:
- 360 Degree Omni-Directional Laser Scanning
- Anti-Glare 60000Lux
- 5000Hz ranging Frequency
- 12m Radius ranging
- Support for ROS/ROS2

## Project Overview

This application connects to the LiDAR sensor via a serial port, processes the incoming point cloud data, applies a Mixture of Gaussians (MOG) algorithm for motion detection, and visualizes the results in a real-time 3D web dashboard.

## Components

The project consists of three main components:

1. **DataExtractor** (`DataExtractor.py`): Handles communication with the LiDAR sensor via serial port, parses the incoming data packets, and provides access to the latest point cloud.

2. **LiDARMOG** (`LMOG.py`): Implements a Mixture of Gaussians algorithm adapted for LiDAR data to detect motion by identifying foreground points that don't match the background model.

3. **Visualization** (`Visualization.py`): Creates a web-based dashboard using Dash and Plotly to visualize the LiDAR data and motion detection results in real-time.

## Setup and Usage

1. Install the required dependencies:
   ```
   pip install numpy dash plotly pyserial
   ```

2. Connect the innomaker DTOF LiDAR to your computer via USB.

3. Update the serial port in `main.py` if necessary (default is 'COM6' for Windows).

4. Run the application:
   ```
   python main.py
   ```

5. Open a web browser and navigate to the URL displayed in the console (typically http://127.0.0.1:8050/).

6. The dashboard will display:
   - Raw point cloud data from the LiDAR (colored by confidence)
   - Motion detection results (orange points)
   - A red diamond marker at the origin (LiDAR position)

7. Use the "Pause" button to freeze/resume the visualization.

## Dependencies

- numpy: For numerical operations
- pyserial: For serial communication with the LiDAR
- dash: For web dashboard framework
- plotly: For interactive 3D visualization

## License

This project is licensed under the terms included in the LICENSE file.