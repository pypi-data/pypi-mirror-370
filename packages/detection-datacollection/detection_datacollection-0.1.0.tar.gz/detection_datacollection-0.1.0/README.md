# Detection Data Collection

[![PyPI version](https://img.shields.io/pypi/v/detection-datacollection.svg)](https://pypi.org/project/detection-datacollection/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Python tool for **collecting object detection datasets** with bounding boxes using **OpenCV**.
It allows you to draw bounding boxes on live camera/video feed and automatically saves annotated images + YOLO-format labels.

---

## 🚀 Installation

```bash
pip install detection-datacollection

````

Or install directly from GitHub:

```bash
pip install git+https://github.com/ShashwatDev-26/imageDataCollection.git
```

---

## 📦 Dependencies

This package requires:

* `numpy==2.2.6`
* `opencv-python==4.12.0.88`
* `PyYAML==6.0.2`

They are automatically installed with `pip`.

---

## 🔧 Usage

### 1. Import and initialize

```python
from detectionDataCollection import detectionDataCollection
# Create a collector instance
collector = detectionDataCollection()
# Use a video file or camera index (0 for default webcam)
collector.set_sourceID(0)  # or "video.mp4"
# Number of samples to capture per class
collector.set_nSamples(10)
# Initialize camera
collector.camera_init_()
# Start annotation mode
collector.annotation()
```

### 2. Controls

* **CTRL + Left Click** → Start drawing bounding box
* **Right Click** → Add object/class
* **CTRL + Right Click** → Start capturing samples
* **ESC** → Stop and save dataset

---

## 📂 Output Structure

When you stop annotation (`ESC`), the dataset is stored like:

```
detectionDataset/
├── train/
│   ├── images/
│   │   ├── frame_000_000.jpg
│   │   └── ...
│   ├── labels/
│   │   ├── frame_000_000.txt
│   │   └── ...
├── data.yaml
```

The labels follow **YOLO format**:

```
class_id x_center y_center width height
```

---
## 🎥
![](https://github.com/ShashwatDev-26/imageDataCollection/blob/main/media/Demo_DataDetection.gif)

## 🌍 Links

* 📦 PyPI: [detection-datacollection](https://pypi.org/project/detection-datacollection/)
* 💻 Source Code: [GitHub](https://github.com/ShashwatDev-26/imageDataCollection.git)
* 🐛 Issues: [Report bugs here](https://github.com/ShashwatDev-26/imageDataCollection/issues)

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).


# <center> To be continued ....</center>

***
