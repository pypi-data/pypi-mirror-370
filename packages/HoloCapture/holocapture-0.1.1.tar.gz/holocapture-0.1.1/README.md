
---

# HoloCapture

**HoloCapture** is a simple, production-ready Python utility for screen and camera capture, screen/camera streaming, multi-camera compositing, and media normalization—using only a few lines of code.

---

## Features

* Capture screenshots to file
* Record screen to video
* Capture images from one or more cameras (with optional normalization)
* Record video from multiple cameras to a single file (side-by-side)
* Real-time screen streaming (with auto-resize)
* Real-time multi-camera streaming (with auto-resize, optional normalization)
* Simple directory management
* No external dependencies beyond common imaging libraries

---

## Installation

```bash
pip install HoloCapture
```

---

## Usage

```python
from HoloCapture import HoloCapture
import cv2
import numpy as np

mediaCapture = HoloCapture()

# Capture a screenshot
mediaCapture.captureScreen('screenshots/screen.jpg')

# Record the screen for 10 seconds
mediaCapture.recordScreen('videos/screen.mp4', duration=10)

# Capture from two cameras and save side-by-side
mediaCapture.captureMedia('images/cameras.jpg', 0, 1, normalize=True)

# Record from two cameras for 15 seconds
mediaCapture.recordMedia('videos/cameras.mp4', 0, 1, duration=15, normalize=True)

# Stream live screen preview (press 'q' to exit)
for frame in mediaCapture.streamScreen(fps=15):
    cv2.imshow("Screen", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()

# Stream from cameras (press 'q' to exit)
for frames, frameCount in mediaCapture.streamCameras(0, 1, normalize=True):
    if any(f is None for f in frames):
        break
    combined = np.hstack(frames)
    cv2.imshow("Combined Cameras", combined)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
```

---

## Methods

| Method                                     | Description                                   |
| ------------------------------------------ | --------------------------------------------- |
| `captureScreen(mediaFile)`                 | Capture screenshot to file                    |
| `recordScreen(mediaFile, duration=10)`     | Record the screen to video file               |
| `captureMedia(combinedFile, *cameras)`     | Capture side-by-side from one or more cameras |
| `recordMedia(combinedFile, *cameras, ...)` | Record video from one or more cameras         |
| `streamScreen(fps=10, maxWidth=1280, ...)` | Generator: live screen frames (resized)       |
| `streamCameras(*cameras, ...)`             | Generator: live camera frames (resized)       |
| `normalizeImage(image)`                    | Normalize contrast/gamma of a frame           |

---

## Notes

* `ImageGrab` requires Windows/macOS or X11-based Linux.
* For multi-camera capture, you must have multiple camera devices attached.
* Streaming windows can be exited by pressing the `q` key.
* Output directories are created automatically if they don’t exist.

---

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).
Copyright 2025 Tristan McBride Sr.

---

## Acknowledgements

Project by:
- Tristan McBride Sr.
- Sybil

