
import os
import time
import weakref
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

import requests
import io
import tempfile

# --- Cross-platform screen grab helper ---
try:
    from PIL import ImageGrab

    def grabScreen():
        return ImageGrab.grab().convert("RGB")

except Exception:
    from mss import mss

    def grabScreen():
        with mss() as sct:
            monitor = sct.monitors[1]  # primary monitor
            img = sct.grab(monitor)
            return Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")


class HoloCapture:
    def __init__(self):
        pass

    def ensureDir(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)

    def captureScreen(self, mediaFile: str) -> str | None:
        """Captures a screenshot and saves it to the given file."""
        try:
            self.ensureDir(mediaFile)
            screenShot = grabScreen()
            screenShot.save(mediaFile, quality=15)
            return mediaFile
        except Exception as e:
            print(f"Error occurred while capturing screen: {e}")
            return None

    def recordScreen(self, mediaFile: str, duration: int = 10) -> str | None:
        """Records the screen for a specified duration and saves it to the given file."""
        duration = max(1, min(int(duration), 60))
        screenWidth, screenHeight = grabScreen().size

        self.ensureDir(mediaFile)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(mediaFile, fourcc, 10.0, (screenWidth, screenHeight))

        frameCount = 0
        maxFrames = int(10 * duration)

        try:
            while frameCount < maxFrames:
                frame = np.array(grabScreen())
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                out.write(frame)
                frameCount += 1
                time.sleep(1.0 / 10.0)
            return mediaFile
        except Exception as e:
            print(f"Error occurred while recording screen: {e}")
            return None
        finally:
            out.release()
            try:
                cv2.destroyAllWindows()
            except cv2.error:
                pass

    def captureMedia(self, combinedFile: str, *cameraIndexes: int, normalize: bool = False) -> str | None:
        """Captures images from multiple cameras and combines them into a single image."""
        cameras = []
        try:
            cameras = [cv2.VideoCapture(idx) for idx in cameraIndexes]
            if not all(cam.isOpened() for cam in cameras):
                return None

            time.sleep(2)
            for _ in range(5):
                frames = [cam.read()[1] for cam in cameras]
                if all(frame is not None for frame in frames):
                    break
                time.sleep(0.1)
            else:
                return None

            if normalize:
                frames = [self.normalizeImage(frame) for frame in frames]

            self.ensureDir(combinedFile)
            combinedFrame = np.hstack(frames)
            success = cv2.imwrite(combinedFile, combinedFrame)
            return combinedFile if success else None
        except Exception as e:
            print(f"Error occurred while capturing media: {e}")
            return None
        finally:
            for cam in cameras:
                cam.release()
            try:
                cv2.destroyAllWindows()
            except cv2.error:
                pass

    def recordMedia(self, combinedFile: str, *cameraIndexes: int, duration: int = 10, normalize: bool = False) -> str | None:
        """Records video from multiple cameras and combines them into a single video file."""
        duration = max(1, min(int(duration), 60))
        cameras = [cv2.VideoCapture(idx) for idx in cameraIndexes]
        if not all(cam.isOpened() for cam in cameras):
            for cam in cameras:
                cam.release()
            return None

        time.sleep(2)
        frameWidth = int(cameras[0].get(cv2.CAP_PROP_FRAME_WIDTH))
        frameHeight = int(cameras[0].get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cameras[0].get(cv2.CAP_PROP_FPS) or 30

        self.ensureDir(combinedFile)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        videoSize = (frameWidth * len(cameras), frameHeight)
        out = cv2.VideoWriter(combinedFile, fourcc, fps, videoSize)

        frameCount = 0
        maxFrames = int(fps * duration)

        try:
            while frameCount < maxFrames:
                frames = []
                for idx, cam in enumerate(cameras):
                    ret, frame = cam.read()
                    if not ret:
                        print(f"Error: Frame capture failed for camera {cameraIndexes[idx]}")
                        return None
                    if normalize:
                        frame = self.normalizeImage(frame)
                    label = f"View {idx+1}"
                    cv2.putText(frame, label, (10, frameHeight - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    frames.append(frame)
                combinedFrame = np.hstack(frames)
                out.write(combinedFrame)
                frameCount += 1
            return combinedFile
        except Exception as e:
            print(f"Error occurred while recording: {e}")
            return None
        finally:
            for cam in cameras:
                cam.release()
            out.release()
            try:
                cv2.destroyAllWindows()
            except cv2.error:
                pass

    def streamScreen(self, fps: int = 10, maxWidth: int = 1280, maxHeight: int = 720):
        """Yields live, resized screen frames as numpy arrays at the given FPS."""
        interval = 1.0 / fps
        try:
            while True:
                frame = np.array(grabScreen())
                h, w = frame.shape[:2]
                scale = min(maxWidth / w, maxHeight / h, 1.0)
                if scale < 1.0:
                    frame = cv2.resize(frame, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
                yield frame
                time.sleep(interval)
        except KeyboardInterrupt:
            return

    def streamCameras(self, *cameraIndexes: int, normalize: bool = False, fps: int = 30,
                  maxWidth: int = 1280, maxHeight: int = 720):
        """Yields live, resized frames from the given cameras as (frame list, frame count)."""
        cameras = [cv2.VideoCapture(idx) for idx in cameraIndexes]
        try:
            if not all(cam.isOpened() for cam in cameras):
                yield None
                return
            frameCount = 0
            while True:
                frames = []
                for cam in cameras:
                    ret, frame = cam.read()
                    if not ret:
                        frames.append(None)
                    else:
                        if normalize:
                            frame = self.normalizeImage(frame)
                        h, w = frame.shape[:2]
                        scale = min(maxWidth / w, maxHeight / h, 1.0)
                        if scale < 1.0:
                            frame = cv2.resize(frame, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
                        frames.append(frame)
                yield frames, frameCount
                frameCount += 1
                time.sleep(1.0 / fps)
        except KeyboardInterrupt:
            return
        finally:
            for cam in cameras:
                cam.release()
            try:
                cv2.destroyAllWindows()
            except cv2.error:
                pass

    def normalizeImage(self, image: np.ndarray) -> np.ndarray:
        """Applies CLAHE and gamma correction to normalize the image."""
        lab     = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe   = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l       = clahe.apply(l)
        lab     = cv2.merge((l, a, b))
        image   = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        gray           = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        meanBrightness = np.mean(gray)
        gamma          = 1.3 if meanBrightness < 80 else 1.1 if meanBrightness < 130 else 1.0

        invGamma = 1.0 / gamma
        table    = np.array([(i / 255.0) ** invGamma * 255 for i in range(256)]).astype("uint8")

        return cv2.LUT(image, table)

    def getImageFromUrl(self, url: str, maxMemoryMB: int = 50):
        """
        Fetch an image from a URL and return it as a PIL Image.

        Behavior:
        - Uses memory if the image is small enough (or size unknown but below threshold).
        - Streams to a temp file if size exceeds maxMemoryMB or grows too large.
        - Temp file is auto-deleted when the image is closed or garbage-collected.
    
        Notes:
        - Caller can use the image as usual (`.show()`, `.save()`, etc.).
        - For large images, calling `img.close()` explicitly ensures immediate cleanup of temp files.
        - For small in-memory images, no special cleanup is required.
        """
        with requests.get(url, stream=True, timeout=30) as res:
            res.raise_for_status()
            size = int(res.headers.get("Content-Length", 0))
            threshold = maxMemoryMB * 1024 * 1024

            if size and size > threshold:
                # Large file detected → stream straight to disk
                return self._openImageFromTemp(b"", res)

            # Unknown size or small size → try in memory first
            buf = io.BytesIO()
            for chunk in res.iter_content(1024 * 1024):  # 1MB chunks
                buf.write(chunk)
                if not size and buf.tell() > threshold:
                    # Too big → switch to disk
                    return self._openImageFromTemp(buf.getvalue(), res)

            buf.seek(0)
            return Image.open(buf)

    def _openImageFromTemp(self, data: bytes, response):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".img")
        try:
            if data:
                tmp.write(data)
            for chunk in response.iter_content(1024 * 1024):  # continue streaming
                tmp.write(chunk)
        finally:
            tmp.close()

        img = Image.open(tmp.name)

        # Hook cleanup on both .close() and GC
        orig_close = img.close
        def cleanup_close():
            try:
                orig_close()
            finally:
                try:
                    if os.path.exists(tmp.name):
                        os.remove(tmp.name)
                except Exception:
                    pass
        img.close = cleanup_close

        # Extra safety: cleanup on garbage collection
        weakref.finalize(img, lambda: os.remove(tmp.name) if os.path.exists(tmp.name) else None)

        return img




# Example usage of the HoloCapture class
#holoCapture = HoloCapture()

# # Stream screen preview in real time
# for frame in holoCapture.streamScreen(fps=15):
#     # Show the frame (with cv2, PIL, etc.) or process it
#     cv2.imshow("Screen", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
# cv2.destroyAllWindows()

# # Stream from cameras
# for frames, frameCount in holoCapture.streamCameras(0, 1, normalize=True):
#     if any(f is None for f in frames):
#         break
#     combined = np.hstack(frames)
#     cv2.imshow("Combined Cameras", combined)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
# cv2.destroyAllWindows()

