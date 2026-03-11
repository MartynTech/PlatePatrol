# PlatePatrol

https://github.com/user-attachments/assets/8551d49c-a361-4bf1-b01e-b2fe9fd7bf5e

## Description
This project develops a real-time vehicle detection and license plate recognition system using advanced deep learning techniques. By integrating the YOLO (You Only Look Once) model for object detection and the SORT (Simple Online and Realtime Tracking) algorithm for tracking, the system efficiently identifies and tracks vehicles in video footage. Additionally, it utilizes a specialized model for accurately detecting and reading license plate numbers.

## Data
The video I used in this tutorial can be downloaded [here](https://www.pexels.com/video/traffic-flow-in-the-highway-2103099/).

## Model
A Yolov8 pre-trained model (YOLOv8n) was used to detect vehicles.

A licensed plate detector was used to detect license plates. The model was trained with Yolov8 using this [dataset](https://universe.roboflow.com/roboflow-universe-projects/license-plate-recognition-rxg4e/dataset/4).

## Dependencies
The sort module needs to be downloaded from this [repository](https://github.com/abewley/sort).

## Installation
To get started, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/arij01/automatic-number-plate-recognition.git
   ```
2. **Navigate to the project directory:**
   ```bash
   cd automatic-number-plate-recognition
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## CLI workflow
1. **Run detection:**
   ```bash
   python main.py
   ```
2. **Interpolate missing data:**
   ```bash
   python add_missing_data.py
   ```
3. **Generate visualization video:**
   ```bash
   python visualize.py
   ```

## Windows GUI workflow
A Tkinter desktop app is included for reviewing detections and correcting OCR mistakes.

1. Launch the app:
   ```bash
   python gui_app.py
   ```
2. Choose a video and click **Run Detection** (or load a previous `test.csv` from **Load CSV**).
3. Select a detected vehicle from the table.
4. Correct the registration if needed (format: `AA00AAA`) and click **Apply Correction**.
5. Save reviewed results with **Save Corrections**.

The GUI renders each registration in a UK-style plate format with a yellow plate body and blue `UK` strip.

## Build standalone `.exe` for Windows
Use PyInstaller on a Windows machine:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed gui_app.py
```

The executable will be created in `dist/gui_app.exe`.
